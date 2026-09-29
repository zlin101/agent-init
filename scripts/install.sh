#!/bin/sh
# Trellium skill installer.
#
# Installs or upgrades a Trellium Skill package (trellium / trellium-zh) into
# an agent's skills directory. Safe to re-run: the installed package is
# replaced in place, so the same command upgrades it.
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/zlin101/trellium/develop/scripts/install.sh | sh -s -- \
#     [--lang en|zh] [--agent codex|claude|all] [--version TAG] [--dir PATH] [--project] [--source DIR]
#
# Defaults: --lang en; agent auto-detected ($CODEX_HOME or ~/.codex -> codex,
# then ~/.claude -> claude); network installs require an explicit --version
# tag (local --source installs need no version).
#
# Audit note: this script downloads one tagged tarball from codeload.github.com
# over HTTPS (only when --version is given) and copies one directory. It never
# edits shell configs or elevates privileges, and it never resolves
# "latest release" aliases.

set -eu

REPO="zlin101/trellium"
LANG_OPT="en"
AGENT=""
VERSION=""
TARGET_DIR=""
PROJECT=0
SOURCE_DIR=""

usage() {
  cat <<'EOF'
usage: install.sh [--lang en|zh] [--agent codex|claude|all] [--version TAG]
                  [--dir PATH] [--project] [--source DIR]

  --lang      package language: en (default) or zh
  --agent     skills directory owner: codex, claude, or all
              when omitted: auto-detects $CODEX_HOME/~/.codex -> codex, ~/.claude -> claude
  --version   release tag to install (required for network installs;
              --source installs are local and need no version)
  --dir       explicit destination skills directory
  --project   install into ./.claude/skills of the current directory
  --source    install from a local checkout/release tree instead of downloading
EOF
  exit 2
}

while [ $# -gt 0 ]; do
  case "$1" in
    --lang) [ $# -ge 2 ] || usage; LANG_OPT=$2; shift 2 ;;
    --agent) [ $# -ge 2 ] || usage; AGENT=$2; shift 2 ;;
    --version) [ $# -ge 2 ] || usage; VERSION=$2; shift 2 ;;
    --dir) [ $# -ge 2 ] || usage; TARGET_DIR=$2; shift 2 ;;
    --project) PROJECT=1; shift ;;
    --source) [ $# -ge 2 ] || usage; SOURCE_DIR=$2; shift 2 ;;
    -h|--help) usage ;;
    *) echo "error: unknown option: $1" >&2; usage ;;
  esac
done

case "$LANG_OPT" in
  en) PACKAGE="trellium" ;;
  zh) PACKAGE="trellium-zh" ;;
  *) echo "error: --lang must be en or zh" >&2; exit 1 ;;
esac

# Removed (TASK-0024): latest-release resolution is not supported. Network
# installs require an explicit --version tag and fail closed without one.

TEMP_ROOT=$(mktemp -d) || exit 1
trap 'rm -rf "$TEMP_ROOT"' EXIT INT TERM

if [ -n "$SOURCE_DIR" ]; then
  TREE="$SOURCE_DIR"
  [ -d "$TREE/skills/$PACKAGE" ] || {
    echo "error: $TREE/skills/$PACKAGE not found in --source" >&2
    exit 1
  }
  VERSION_DESC="local source"
else
  if [ -z "$VERSION" ]; then
    echo "error: network installs require an explicit --version TAG (for example: --version 2026.09.10)" >&2
    echo "       latest-release resolution is not supported; pick a tag from the repository's tagged releases," >&2
    echo "       or use --source <dir> to install from a local checkout without a version." >&2
    exit 1
  fi
  echo "==> fetching $REPO tag $VERSION"
  curl -fsSL "https://codeload.github.com/$REPO/tar.gz/refs/tags/$VERSION" -o "$TEMP_ROOT/release.tar.gz"
  mkdir "$TEMP_ROOT/extract"
  tar -xzf "$TEMP_ROOT/release.tar.gz" -C "$TEMP_ROOT/extract"
  ROOTS=$(ls "$TEMP_ROOT/extract")
  [ -d "$TEMP_ROOT/extract/$ROOTS/skills/$PACKAGE" ] || {
    echo "error: package $PACKAGE missing in release $VERSION" >&2
    exit 1
  }
  TREE="$TEMP_ROOT/extract/$ROOTS"
  VERSION_DESC="$VERSION"
fi

install_to() {
  dest_dir=$1
  mkdir -p "$dest_dir"
  staging="$dest_dir/.$PACKAGE.install.$$"
  rm -rf "$staging"
  cp -R "$TREE/skills/$PACKAGE" "$staging"
  rm -rf "$dest_dir/$PACKAGE"
  mv "$staging" "$dest_dir/$PACKAGE"
  echo "==> installed $PACKAGE ($VERSION_DESC) -> $dest_dir/$PACKAGE"
}

codex_skills_dir() { printf '%s/skills' "${CODEX_HOME:-$HOME/.codex}"; }
claude_skills_dir() { printf '%s/skills' "$HOME/.claude"; }

detect_agent() {
  if [ -n "${CODEX_HOME:-}" ] || [ -d "$HOME/.codex" ]; then
    echo "codex"
    return 0
  fi
  if [ -d "$HOME/.claude" ]; then
    echo "claude"
    return 0
  fi
  echo ""
}

if [ "$PROJECT" -eq 1 ]; then
  install_to "$PWD/.claude/skills"
elif [ -n "$TARGET_DIR" ]; then
  install_to "$TARGET_DIR"
else
  RESOLVED="${AGENT:-$(detect_agent)}"
  case "$RESOLVED" in
    codex) install_to "$(codex_skills_dir)" ;;
    claude) install_to "$(claude_skills_dir)" ;;
    all)
      install_to "$(codex_skills_dir)"
      install_to "$(claude_skills_dir)"
      ;;
    *)
      cat >&2 <<EOF
error: could not detect an agent skills directory.
Pass --agent codex|claude|all, or --dir <path>, or --project.
  codex : \$(codex_skills_dir)
  claude: \$HOME/.claude/skills
EOF
      exit 1
      ;;
  esac
fi

cat <<EOF

Next:
  1. Restart your agent so the new skill is discovered.
  2. Ask the agent to adopt or upgrade a project ("adopt this project" /
     "update the vault"), or run the bundled updater directly:
     python3 <skills-dir>/$PACKAGE/assets/trellium.py --help
EOF
