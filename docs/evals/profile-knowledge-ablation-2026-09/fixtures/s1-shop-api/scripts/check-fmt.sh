#!/bin/sh
# Fail (exit 1) when any Go file in the repository is not gofmt-formatted.
set -eu

bad=$(find . -name '*.go' -not -path './.git/*' | xargs gofmt -l)
if [ -n "$bad" ]; then
    echo "gofmt needed:"
    echo "$bad"
    exit 1
fi
