import asyncio
import importlib
import logging
import time
from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from importlib import resources
from typing import Any

import asyncpg
from asyncpg import Connection
from asyncpg.pool import Pool, PoolAcquireContext
from cock import Option, build_options_from_dict
from facet import ServiceMixin
from yarl import URL

from yacore.injector import inject, register

db_postgresql_options = build_options_from_dict({
    "db-postgresql": {
        "host": Option(default="db"),
        "port": Option(default=5432, type=int),
        "user": Option(default="postgres"),
        "password": Option(default="admin"),
        "database": Option(default=None),
        "connection": {
            "attempts": Option(default=60, type=int),
            "interval": Option(default=1.0, type=float),
        },
        "pool": {
            "min-size": Option(default=2, type=int),
            "max-size": Option(default=10, type=int),
        },
        "migration": {
            "script-location": Option(default=None),
            "target-revision": Option(default=None),
        },
    }
})

logger = logging.getLogger(__name__)


class DbPostgresql(ServiceMixin):

    def __init__(self, connection_url: URL, conn_attempts: int = 60, conn_interval: float = 1.0,
                 pool_min_size: int = 2, pool_max_size: int = 10):
        self._url = connection_url.with_scheme("postgresql")
        self._attempts = conn_attempts
        self._interval = conn_interval
        self._pool_min_size = pool_min_size
        self._pool_max_size = pool_max_size

        self._pool: Pool | None = None

    async def start(self):
        for _ in range(self._attempts):
            start = time.monotonic()
            try:
                self._pool = await self._create_pool()
            except (OSError,
                    asyncio.TimeoutError,
                    asyncpg.PostgresError):
                t = max(0.0, start + self._interval - time.monotonic())
                await asyncio.sleep(t)
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.error("Cannot connect to database", exc_info=True)
                raise
            else:
                logger.debug("Successfully connected to database")
                break
        else:
            raise RuntimeError("Can't connect to db, attempts gone")

    async def _create_pool(self) -> Pool:
        return await asyncpg.create_pool(
            dsn=str(self._url), min_size=self._pool_min_size, max_size=self._pool_max_size,
            timeout=self._interval
        )

    async def stop(self):
        await self._pool.close()
        self._pool = None

    def get_connection(self) -> PoolAcquireContext:
        return self._pool.acquire()

    @property
    def url(self) -> URL:
        return self._url

    @property
    def pool(self) -> Pool:
        return self._pool

    async def clear_schema(self):
        async with self.get_connection() as conn:
            await conn.execute("DROP SCHEMA public CASCADE")
            await conn.execute("CREATE SCHEMA public")

    async def migrate(self, migration_script_location: str, migration_target_revision: str | None = None):
        migrator = DatabaseMigrator(migration_script_location)
        async with self.get_connection() as conn:
            await migrator.migrate(conn, target=migration_target_revision)


@register(name="db_postgresql", singleton=True)
@inject
def db_postgresql_from_config(config):
    url = URL.build(
        host=config.db_postgresql_host, port=config.db_postgresql_port,
        user=config.db_postgresql_user, password=config.db_postgresql_password,
    )
    if not config.db_postgresql_database:
        raise ValueError("db_postgresql_database should be specified explicitly")
    else:
        url = url.with_path(config.db_postgresql_database)

    return DbPostgresql(
        connection_url=url,
        conn_attempts=config.db_postgresql_connection_attempts,
        conn_interval=config.db_postgresql_connection_interval,
        pool_min_size=config.db_postgresql_pool_min_size,
        pool_max_size=config.db_postgresql_pool_max_size,
    )


@dataclass(frozen=True)
class Migration:
    revision: str
    depends_on: str | None
    migrate: Callable[[Connection], Coroutine]

    @classmethod
    def from_module(cls, module: Any):
        return cls(module.revision, module.depends_on, module.migrate)


class MigrationError(Exception):
    pass


class DatabaseMigrator:
    def __init__(self, script_location: str):
        self._script_location = script_location

    async def migrate(self, conn: Connection, *, target: str | None = None):
        migrations = self.collect_migrations()

        await conn.execute("CREATE TABLE IF NOT EXISTS revision (id TEXT PRIMARY KEY)")
        current = await conn.fetchval("SELECT id FROM revision")

        target_text = target or "<head>"
        current_text = current or "<empty>"
        logger.info("Database is initially at %s, target revision is %s", current_text, target_text)

        if current:
            while migrations:
                discarded_rev = migrations.pop(0).revision
                if discarded_rev == current:
                    break
                if discarded_rev == target:
                    raise MigrationError(f"Current revision {current} is ahead of target revision {target}")
            else:
                raise MigrationError(f"Cannot find current revision {current} in migration files")

        if not migrations or (current == target and target is not None):
            logger.info("No migrations applied")
            return

        async with conn.transaction():
            for migration in migrations:
                logger.info("Migrating database to %s...", migration.revision)
                await migration.migrate(conn)
                if migration.revision == target:
                    break

            q = "UPDATE revision SET id = $1" if current else "INSERT INTO revision VALUES ($1)"
            await conn.execute(q, migration.revision)

        logger.info("Database is migrated to %s", migration.revision)

    def collect_migrations(self) -> list[Migration]:
        collected_revs: set[str] = set()
        prerequisites: dict[str | None, Migration] = {}
        result: list[Migration] = []
        for migration in self.load_modules():
            if migration.depends_on in prerequisites:
                raise MigrationError(f"Multiple revisions depend on {migration.depends_on}")
            prerequisites[migration.depends_on] = migration

            if migration.revision in collected_revs:
                raise MigrationError(f"Found multiple revisions {migration.revision}")
            collected_revs.add(migration.revision)

        list_head = prerequisites.pop(None, None)
        if list_head is None:
            raise MigrationError("Cannot find first migration in chain")
        result.append(list_head)

        while prerequisites:
            last_rev = result[-1].revision
            dependent_rev = prerequisites.pop(last_rev, None)
            if dependent_rev is None:
                raise MigrationError(f"Migration chain is broken after {last_rev}")
            result.append(dependent_rev)

        return result

    def load_modules(self) -> list[Migration]:
        result = []
        for path in resources.files(self._script_location).iterdir():
            if path.suffix == ".py" and path.stem != "__init__":
                module = importlib.import_module(f"{self._script_location}.{path.stem}")
                result.append(Migration.from_module(module))
        return result


@inject
async def migrate_using_config(config, db_postgresql):
    if not config.db_postgresql_migration_script_location:
        raise ValueError("db_postgresql_migration_script_location should be specified explicitly")

    async with db_postgresql:
        await db_postgresql.migrate(
            config.db_postgresql_migration_script_location,
            config.db_postgresql_migration_target_revision,
        )
