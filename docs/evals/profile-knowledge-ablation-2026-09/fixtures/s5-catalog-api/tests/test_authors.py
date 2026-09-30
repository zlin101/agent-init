# pyright: reportMissingImports=false
"""Tests for the catalog API."""

import asyncio

import httpx

from app.main import app


def test_list_authors():
    async def run():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.get("/authors")

    resp = asyncio.run(run())
    assert resp.status_code == 200
    assert len(resp.json()) == 2
