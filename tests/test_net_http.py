import pytest
from fastapi import Body, HTTPException
from httpx import HTTPStatusError

from yacore.net.http import NetHttpServer


@pytest.mark.asyncio
async def test_healthcheck(web_client):
    response = await web_client.get("healthcheck")
    data = response.json()
    assert data == {
        "ok": True,
        "name": "test_name",
        "version": "version",
        "build_info": "test-build-info",
    }


async def handler(value: str = Body(..., embed=True)):
    if value == "error":
        raise ZeroDivisionError
    elif value == "exception":
        raise HTTPException(status_code=443, detail="plain http exception")
    return {"value": value}


@pytest.mark.asyncio
async def test_handler_success(web_client, web_server: NetHttpServer):
    web_server.add_post("/handle", handler)

    response = await web_client.post("handle", json={"value": "string"})
    assert response.status_code == 200
    data = response.json()
    assert data == {"value": "string"}


@pytest.mark.asyncio
async def test_handler_validation_error(web_client, web_server: NetHttpServer):
    web_server.add_post("/handle", handler)

    response = await web_client.post("handle")
    assert response.status_code == 422
    data = response.json()
    assert data["code"] == "common.validation_error"
    data = data["data"]
    assert len(data) == 1
    expected = {
        "loc": ["body", "value"],
        "msg": "Field required",
        "type": "missing",
    }
    for k, v in expected.items():
        assert data[0][k] == v


@pytest.mark.asyncio
async def test_handler_error(web_client, web_server: NetHttpServer):
    web_server.add_post("/handle", handler)

    response = await web_client.post("handle", json={"value": "error"})
    assert response.status_code == 500
    data = response.json()
    assert data == {
        "code": "common.internal_server_error",
        "message": "Internal server error",
        "data": None,
    }


@pytest.mark.asyncio
async def test_handler_exception(web_client, web_server: NetHttpServer):
    web_server.add_post("/handle", handler)

    response = await web_client.post("handle", json={"value": "exception"})
    assert response.status_code == 443
    data = response.json()
    assert data == {
        "code": "common.http_error",
        "message": "plain http exception",
        "data": None,
    }


@pytest.mark.asyncio
async def test_handler_return_none(web_client, web_server: NetHttpServer):
    async def handler():
        return

    web_server.add_get("/handle", handler)
    response = await web_client.get("handle")
    assert response.status_code == 200
    data = response.json()
    assert data is None


@pytest.mark.asyncio
async def test_handler_return_list(web_client, web_server: NetHttpServer):
    async def handler():
        return [1, 2, 3]

    web_server.add_get("/handle", handler)
    response = await web_client.get("handle")
    assert response.status_code == 200
    data = response.json()
    assert data == [1, 2, 3]


@pytest.mark.asyncio
async def test_handler_unpack_json(web_client, web_server: NetHttpServer):
    web_server.add_post("/handle", handler)

    web_client.unpack_json = True
    data = await web_client.post("handle", json={"value": "string"})
    assert data == {"value": "string"}

    response = await web_client.post("handle", json={"value": "string"}, raw=True)
    data = response.json()
    assert data == {"value": "string"}

    data = await web_client.post("handle", json={"value": "error"})
    assert data == {
        "code": "common.internal_server_error",
        "message": "Internal server error",
        "data": None,
    }

    web_client.raise_for_status = True
    with pytest.raises(HTTPStatusError):
        await web_client.post("handle", json={"value": "error"})

    response = await web_client.post("handle", json={"value": "error"}, raw=True)
    assert response.status_code == 500
