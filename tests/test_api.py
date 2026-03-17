import pytest
from httpx import ASGITransport, AsyncClient

from fl_platform.main import app


@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_list_agents():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/v1/agents")
        assert resp.status_code == 200
        agents = resp.json()
        assert len(agents) >= 20
        names = [a["name"] for a in agents]
        assert "director.first_assistant" in names


@pytest.mark.asyncio
async def test_get_pipeline_dag():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/v1/pipeline/dag")
        assert resp.status_code == 200
        data = resp.json()
        assert "steps" in data
        assert "agents" in data
