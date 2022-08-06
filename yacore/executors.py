import asyncio
import functools
import os
from concurrent.futures import ThreadPoolExecutor

from cock import Option, build_options_from_dict
from facet import ServiceMixin

from yacore.injector import inject, register

try:
    CPU_COUNT = len(os.sched_getaffinity(0))
except AttributeError:
    CPU_COUNT = os.cpu_count() or 1
if CPU_COUNT is None:
    # TODO: think of more elegant logic here
    CPU_COUNT = 4

executors_options = build_options_from_dict({
    "executors": {
        "io_threads_count": Option(default=32, type=int),
        # https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor
        "cpu_threads_count": Option(default=min(32, CPU_COUNT + 4), type=int),
    },
})


def blocking_io_function(f):
    @functools.wraps(f)
    @inject
    async def wrapper(*args, executors, **kwargs):
        return await executors.blocking_io_call(f, *args, **kwargs)
    return wrapper


def blocking_cpu_function(f):
    @functools.wraps(f)
    @inject
    async def wrapper(*args, executors, **kwargs):
        return await executors.blocking_cpu_call(f, *args, **kwargs)
    return wrapper


class Executors(ServiceMixin):

    def __init__(self, io_threads_count, cpu_threads_count):
        self.io_threads_count = io_threads_count
        self.cpu_threads_count = cpu_threads_count

        self.io_executor = None
        self.cpu_executor = None
        self.loop = None

    async def start(self):
        self.io_executor = ThreadPoolExecutor(max_workers=self.io_threads_count)
        self.cpu_executor = ThreadPoolExecutor(max_workers=self.cpu_threads_count)
        self.loop = asyncio.get_running_loop()

    async def stop(self):
        self.io_executor.shutdown()
        self.cpu_executor.shutdown()

    async def _blocking_call(self, executor, f, *args, **kwargs):
        bound = functools.partial(f, *args, **kwargs)
        return await self.loop.run_in_executor(executor, bound)

    async def blocking_io_call(self, f, *args, **kwargs):
        return await self._blocking_call(self.io_executor, f, *args, **kwargs)

    async def blocking_cpu_call(self, f, *args, **kwargs):
        return await self._blocking_call(self.cpu_executor, f, *args, **kwargs)


@register(name="executors", singleton=True)
@inject
def executors_from_config(config):
    return Executors(
        io_threads_count=config.executors_io_threads_count,
        cpu_threads_count=config.executors_cpu_threads_count,
    )
