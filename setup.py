from pathlib import Path

from setuptools import find_packages, setup

PACKAGE_ROOT = Path(__file__).parent
VERSION = PACKAGE_ROOT / "yacore" / "version.txt"


extras_require = {
    "dev": ["ruff", "pytest", "pytest-asyncio", "pytest-cov", "testcontainers"],
    "db.postgresql": ["asyncpg", "yarl"],
    "log.loguru": ["loguru"],
    "log.std": ["pyyaml"],
    "net.http": ["async-timeout", "fastapi >= 0.89.0", "httpx", "hypercorn", "yarl"],
}

extras_dev = set()
for requirements in extras_require.values():
    extras_dev |= set(requirements)

extras_require["dev"] = list(extras_dev)

setup(
    name="yacore",
    version=VERSION.read_text().strip(),
    packages=find_packages(include=["yacore*"]),
    package_data={
        "": ["*.txt"],
    },
    python_requires=">= 3.11",
    install_requires=[
        "cock >= 0.11.0",
        "facet >= 0.9.1",
        "giveme",
    ],
    extras_require=extras_require,
    entry_points={
        "pytest11": [
            "yacore-db-postgresql = yacore.db.postgresql.fixtures",
        ],
    },

    url="https://github.com/pohmelie/yacore",
    author="pohmelie",
    author_email="multisosnooley@gmail.com",
    description="yet another core library",
    long_description=Path("readme.md").read_text(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
    license="MIT",
    license_file="license.txt",
)
