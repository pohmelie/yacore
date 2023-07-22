import asyncio
from typing import Any

from cock import Option, build_options_from_dict
from facet import ServiceMixin
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from hypercorn.asyncio import serve
from hypercorn.config import Config
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException

from yacore.injector import inject, register

ACCESS_LOG_DEFAULT_FORMAT = '%(h)s %(l)s %(l)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

net_http_options = build_options_from_dict({
    "net-http": {
        "host": Option(default="0.0.0.0"),
        "port": Option(default=80, type=int),
        "healthcheck_name": Option(default="noname"),
        "access_log_format": Option(default=ACCESS_LOG_DEFAULT_FORMAT),
        "hide_methods_description_route": Option(is_flag=True),
        "build_info": Option(default="noinfo"),
    },
})


class HealthCheck(BaseModel):
    ok: bool
    name: str
    version: str
    build_info: str


def _api_error(status_code: int, code: str, message: str | None = None, data: Any | None = None):
    return JSONResponse(
        status_code=status_code,
        content={
            "code": code,
            "message": message,
            "data": data,
        },
    )


class NetHttpServer(ServiceMixin):

    def __init__(self, host=None, port=80, *, healthcheck_name="noname", version="unknown",
                 build_info="noinfo", access_log_format=ACCESS_LOG_DEFAULT_FORMAT,
                 hide_methods_description_route=False):
        self.host = host
        self.port = port
        self.healthcheck = HealthCheck(
            ok=True,
            name=healthcheck_name,
            version=version,
            build_info=build_info,
        )

        self.app = None
        self.hypercorn_config = Config.from_mapping(
            bind=f"{host}:{port}",
            access_log_format=access_log_format,
            graceful_timeout=0,
        )
        self.hide_methods_description_route = hide_methods_description_route

    async def start(self):
        # if someone want to customize app creation via subclass
        if self.app is None:
            if self.hide_methods_description_route:
                self.app = FastAPI(openapi_url=None, docs_url=None, redoc_url=None)
            else:
                self.app = FastAPI()
        self.app.add_exception_handler(Exception, self.error_handler)
        self.app.add_exception_handler(StarletteHTTPException, self.exception_handler)
        self.app.add_exception_handler(RequestValidationError, self.validation_handler)
        self.add_get("/healthcheck", self.get_healthcheck)
        self.add_task(serve(
            self.app,
            self.hypercorn_config,
            shutdown_trigger=asyncio.Future,  # no signal handling
        ))

    def add_route(self, *args, **kwargs):
        self.app.add_api_route(*args, **kwargs)

    def add_get(self, *args, **kwargs):
        self.add_route(*args, methods=["get"], **kwargs)

    def add_post(self, *args, **kwargs):
        self.add_route(*args, methods=["post"], **kwargs)

    async def error_handler(self, request, exc: Exception):
        return _api_error(
            status_code=500,
            code="common.internal_server_error",
            message="Internal server error",
        )

    async def exception_handler(self, request, exc: StarletteHTTPException):
        return _api_error(
            status_code=exc.status_code,
            code="common.http_error",
            message=exc.detail,
        )

    async def validation_handler(self, request, exc: RequestValidationError):
        return _api_error(
            status_code=422,
            code="common.validation_error",
            message=str(exc),
            data=exc.errors(),
        )

    async def get_healthcheck(self) -> HealthCheck:
        return self.healthcheck


@register(name="net_http_server", singleton=True)
@inject
def net_http_server_from_config(config, version):
    return NetHttpServer(
        host=config.net_http_host,
        port=config.net_http_port,
        healthcheck_name=config.get("net_http_healthcheck_name", "noname"),
        version=version,
        build_info=config.get("net_http_build_info", "noinfo"),
        access_log_format=config.get("net_http_access_log_format", ACCESS_LOG_DEFAULT_FORMAT),
        hide_methods_description_route=config.net_http_hide_methods_description_route,
    )
