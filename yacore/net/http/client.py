from async_timeout import timeout
from facet import ServiceMixin
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient
from yarl import URL


class NetHttpClient(ServiceMixin):

    def __init__(self, host, port=80, timeout=600.0, scheme="http", unpack_json=False, raise_for_status=False):
        self.base_url = URL.build(scheme=scheme, host=host, port=port)
        self.timeout = timeout
        self.unpack_json = unpack_json
        self.raise_for_status = raise_for_status
        self.client = None

    async def start(self):
        self.client = AsyncClient()
        return self

    async def stop(self):
        await self.client.aclose()

    async def request(self, suburl: str, method: str = "POST", raw=False, json=None, **extra):
        url = self.base_url / suburl
        if json is not None:
            json = jsonable_encoder(json)
        async with timeout(self.timeout):
            response = await self.client.request(method, str(url), json=json, **extra)
            if raw:
                return response
            if self.raise_for_status:
                response.raise_for_status()
            if not self.unpack_json:
                return response
            return response.json()

    async def get(self, suburl: str, **extra):
        return await self.request(suburl, method="GET", **extra)

    async def post(self, suburl: str, **extra):
        return await self.request(suburl, method="POST", **extra)
