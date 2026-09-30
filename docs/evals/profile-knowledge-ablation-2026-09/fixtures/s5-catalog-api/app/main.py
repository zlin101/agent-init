# pyright: reportMissingImports=false
"""Catalog API application."""

from fastapi import FastAPI

app = FastAPI(title="catalog-api")


@app.get("/authors")
def list_authors():
    """Return all authors as plain dictionaries."""
    return [
        {"id": 1, "name": "Ursula Le Guin"},
        {"id": 2, "name": "Octavia Butler"},
    ]
