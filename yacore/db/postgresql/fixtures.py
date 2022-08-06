import asyncio
from contextlib import contextmanager

import asyncpg
import pytest
from testcontainers.core.container import DockerContainer
from yarl import URL


def pytest_addoption(parser):
    parser.addoption("--yacore-db-postgresql-local-url", default=None,
                     help="Use a local postgresql database or up from a docker container")


@pytest.fixture(scope="session")
def db_postgresql_local_url(request):
    return request.config.getoption("--yacore-db-postgresql-local-url")


def _wait_db_ready(db_url: URL, attempts=10, interval=1):
    async def waiter():
        for _ in range(attempts):
            try:
                conn = await asyncpg.connect(str(db_url))
            except (OSError,
                    asyncio.TimeoutError,
                    asyncpg.PostgresError):
                await asyncio.sleep(interval)
            else:
                await conn.close()
                break
        else:
            raise RuntimeError("Can't connect to db, attempts gone")

    asyncio.run(waiter())


@pytest.fixture(scope="session")
def db_postgresql_service_url_factory():

    @contextmanager
    def factory(container_version, local_db_dsn) -> URL:
        container = None

        if local_db_dsn:
            db_url = URL(local_db_dsn)
        else:
            internal_port = 5432
            user = "test"
            password = "test"
            container = DockerContainer(container_version)
            container.with_env("POSTGRES_USER", user)
            container.with_env("POSTGRES_PASSWORD", password)
            container.with_exposed_ports(internal_port)
            container.start()

            host = container.get_container_host_ip()
            port = container.get_exposed_port(internal_port)
            db_url = URL.build(scheme="postgresql", host=host, port=int(port), user=user, password=password)

        try:
            _wait_db_ready(db_url)
            yield db_url
        finally:
            if container is not None:
                container.stop()

    return factory


@pytest.fixture(scope="session")
def db_postgresql_service_url(db_postgresql_service_url_factory,
                              db_postgresql_container_version,
                              db_postgresql_local_url) -> URL:
    with db_postgresql_service_url_factory(db_postgresql_container_version, db_postgresql_local_url) as db_url:
        yield db_url
