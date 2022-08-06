import asyncio
import math
import time

import pytest

from yacore.executors import blocking_cpu_function, blocking_io_function


@pytest.mark.asyncio
async def test_io_executor_two_threads(executors):
    start = time.perf_counter()
    await asyncio.gather(
        executors.blocking_io_call(time.sleep, 0.1),
        executors.blocking_io_call(time.sleep, 0.1),
    )
    delta = time.perf_counter() - start
    assert math.isclose(delta, 0.1, rel_tol=0.25)


@pytest.mark.asyncio
async def test_cpu_executor_one_thread(executors):
    start = time.perf_counter()
    await asyncio.gather(
        executors.blocking_cpu_call(time.sleep, 0.1),
        executors.blocking_cpu_call(time.sleep, 0.1),
    )
    delta = time.perf_counter() - start
    assert math.isclose(delta, 0.2, rel_tol=0.25)


@pytest.mark.asyncio
async def test_io_decorator(executors):
    sleep = blocking_io_function(time.sleep)
    start = time.perf_counter()
    await asyncio.gather(sleep(0.1), sleep(0.1))
    delta = time.perf_counter() - start
    assert math.isclose(delta, 0.1, rel_tol=0.25)


@pytest.mark.asyncio
async def test_cpu_decorator(executors):
    sleep = blocking_cpu_function(time.sleep)
    start = time.perf_counter()
    await asyncio.gather(sleep(0.1), sleep(0.1))
    delta = time.perf_counter() - start
    assert math.isclose(delta, 0.2, rel_tol=0.25)
