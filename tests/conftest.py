import pytest
import pytest_asyncio
from cock import Config

from yacore.db.postgresql import DbPostgresql
from yacore.executors import executors_from_config
from yacore.injector import injector, register
from yacore.log.loguru import configure_logging_from_config
from yacore.net.http import NetHttpClient, net_http_server_from_config


@pytest.fixture(autouse=True)
def core_config(unused_tcp_port):
    cfg = Config({
        "net_http_port": unused_tcp_port,
        "net_http_host": "127.0.0.1",
        "net_http_healthcheck_name": "test_name",
        "net_http_build_info": "test-build-info",
        "net_http_hide_methods_description_route": False,
        "log_level": "debug",
        "executors_io_threads_count": 2,
        "executors_cpu_threads_count": 1,
        "db_postgresql_host": "some_host",
        "db_postgresql_port": 2345,
        "db_postgresql_user": "user",
        "db_postgresql_password": "password",
        "db_postgresql_database": "some_database",
        "db_postgresql_connection_attempts": 500,
        "db_postgresql_connection_interval": 0.001,
        "db_postgresql_pool_min_size": 0,
        "db_postgresql_pool_max_size": 100500,
        "db_postgresql_migration_script_location": "some.location",
        "db_postgresql_migration_target_revision": None,
    })
    register(lambda: "version", name="version")
    register(lambda: cfg, name="config")
    return cfg


@pytest.fixture(autouse=True)
def configure_logging(core_config):
    configure_logging_from_config()


@pytest_asyncio.fixture
async def web_server(core_config):
    async with net_http_server_from_config() as ws:
        yield ws


@pytest_asyncio.fixture
async def web_client(web_server, core_config):
    async with NetHttpClient(
            host=core_config.net_http_host,
            port=core_config.net_http_port,
            timeout=5) as wc:
        yield wc


@pytest_asyncio.fixture
async def executors(core_config):
    async with executors_from_config() as ex:
        register(lambda: ex, name="executors")
        yield ex
        injector.delete("executors")


@pytest.fixture(scope="session")
def db_postgresql_container_version():
    return "postgres:14-alpine"


@pytest_asyncio.fixture
async def database(db_postgresql_service_url):
    async with DbPostgresql(db_postgresql_service_url) as db:
        yield db
        await db.clear_schema()
