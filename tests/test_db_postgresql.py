import time
from unittest.mock import AsyncMock, patch

import pytest

from yacore.db.postgresql.postgresql import (
    DatabaseMigrator,
    DbPostgresql,
    Migration,
    MigrationError,
    db_postgresql_from_config,
    migrate_using_config,
)


@pytest.mark.asyncio
async def test_database_connection(database):
    async with database.get_connection() as conn:
        await conn.execute("CREATE TABLE test ()")
        await conn.execute("DROP TABLE test")


@pytest.mark.asyncio
async def test_database_connection_timed_out(db_postgresql_service_url, unused_tcp_port):
    bad_url = db_postgresql_service_url.with_port(unused_tcp_port)
    failing_db = DbPostgresql(bad_url, conn_attempts=10, conn_interval=0.1)
    with pytest.raises(RuntimeError) as exc:
        start = time.perf_counter()
        async with failing_db:
            pass

    delta = time.perf_counter() - start
    assert delta == pytest.approx(1.0, abs=0.05)
    assert str(exc.value) == "Can't connect to db, attempts gone"


@pytest.mark.asyncio
async def test_database_connection_failed(db_postgresql_service_url):
    failing_db = DbPostgresql(db_postgresql_service_url.with_host("nonexisting"), conn_interval=0.001)
    with pytest.raises(Exception):
        async with failing_db:
            pass


def test_database_from_config(core_config):
    database_name = core_config.db_postgresql_database
    core_config["db_postgresql_database"] = None
    # database name should be specified explicitly
    with pytest.raises(ValueError):
        db_postgresql_from_config()

    core_config["db_postgresql_database"] = database_name
    database = db_postgresql_from_config()
    assert str(database.url) == "postgresql://user:password@some_host:2345/some_database"


async def case(database, current: str | None, target: str | None, expected: str, expected_calls: list[int]):
    calls = []
    migrations = [
        Migration("002", "001", AsyncMock(side_effect=lambda _: calls.append(2))),
        Migration("001", None, AsyncMock(side_effect=lambda _: calls.append(1))),
        Migration("003", "002", AsyncMock(side_effect=lambda _: calls.append(3))),
    ]
    if current is not None:
        async with database.get_connection() as conn:
            await conn.execute("CREATE TABLE IF NOT EXISTS revision (id TEXT PRIMARY KEY)")
            await conn.execute("INSERT INTO revision VALUES ($1)", current)

    with patch.object(DatabaseMigrator, "load_modules", return_value=migrations):
        migrator = DatabaseMigrator("")
        async with database.get_connection() as conn:
            await migrator.migrate(conn, target=target)
            revision = await conn.fetchval("SELECT id FROM revision")

    assert calls == expected_calls
    assert revision == expected


@pytest.mark.asyncio
async def test_migrator_empty_to_head(database):
    await case(
        database, current=None, target=None,
        expected="003", expected_calls=[1, 2, 3]
    )


@pytest.mark.asyncio
async def test_migrator_partial_to_head(database):
    await case(
        database, current="001", target=None,
        expected="003", expected_calls=[2, 3]
    )


@pytest.mark.asyncio
async def test_migrator_empty_to_target(database):
    await case(
        database, current=None, target="002",
        expected="002", expected_calls=[1, 2]
    )


@pytest.mark.asyncio
async def test_migrator_unknown_current(database):
    with pytest.raises(MigrationError):
        await case(
            database, current="000", target=None,
            expected="", expected_calls=[]
        )


@pytest.mark.asyncio
async def test_migrator_current_ahead_of_target(database):
    with pytest.raises(MigrationError):
        await case(
            database, current="003", target="002",
            expected="", expected_calls=[]
        )


@pytest.mark.asyncio
async def test_migrator_current_at_target(database):
    await case(
        database, current="002", target="002",
        expected="002", expected_calls=[]
    )
    await database.clear_schema()
    await case(
        database, current="003", target=None,
        expected="003", expected_calls=[]
    )


def test_migrator_collect_multiple_revisions():
    migrations = [
        Migration("002", "001", AsyncMock()),
        Migration("001", None, AsyncMock()),
        Migration("001", "002", AsyncMock()),
    ]
    with patch.object(DatabaseMigrator, "load_modules", return_value=migrations):
        migrator = DatabaseMigrator("")
        with pytest.raises(MigrationError):
            migrator.collect_migrations()


def test_migrator_collect_multiple_depend_on():
    migrations = [
        Migration("002", "001", AsyncMock()),
        Migration("001", None, AsyncMock()),
        Migration("003", "001", AsyncMock()),
    ]
    with patch.object(DatabaseMigrator, "load_modules", return_value=migrations):
        migrator = DatabaseMigrator("")
        with pytest.raises(MigrationError):
            migrator.collect_migrations()


def test_migrator_collect_no_head():
    migrations = [
        Migration("002", "001", AsyncMock()),
        Migration("001", "000", AsyncMock()),
        Migration("003", "002", AsyncMock()),
    ]
    with patch.object(DatabaseMigrator, "load_modules", return_value=migrations):
        migrator = DatabaseMigrator("")
        with pytest.raises(MigrationError):
            migrator.collect_migrations()


def test_migrator_collect_broken_chain():
    migrations = [
        Migration("002", "000", AsyncMock()),
        Migration("001", None, AsyncMock()),
        Migration("003", "002", AsyncMock()),
    ]
    with patch.object(DatabaseMigrator, "load_modules", return_value=migrations):
        migrator = DatabaseMigrator("")
        with pytest.raises(MigrationError):
            migrator.collect_migrations()


@pytest.mark.asyncio
async def test_migrate_using_config(core_config, database):
    migrations = [Migration("001", None, AsyncMock())]

    script_location = core_config.db_postgresql_migration_script_location
    core_config["db_postgresql_migration_script_location"] = None
    # script location name should be specified explicitly
    with pytest.raises(ValueError):
        await migrate_using_config(core_config, database)

    core_config["db_postgresql_migration_script_location"] = script_location
    with patch.object(DatabaseMigrator, "load_modules", return_value=migrations):
        await migrate_using_config(core_config, database)
