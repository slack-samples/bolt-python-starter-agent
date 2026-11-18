import asyncio
from collections.abc import Awaitable, Callable

from slack_bolt.lazy_listener.async_internals import to_runnable_function
from slack_bolt.lazy_listener.asyncio_runner import AsyncioLazyListenerRunner
from slack_bolt.request.async_request import AsyncBoltRequest
from vercel.functions import wait_until


class WaitUntilLazyListenerRunner(AsyncioLazyListenerRunner):
    """Run each lazy listener as a task that keeps the Vercel Function alive.

    Outside of Vercel, wait_until does nothing and the task runs on the loop.
    """

    def start(
        self, function: Callable[..., Awaitable[None]], request: AsyncBoltRequest
    ) -> None:
        task = asyncio.ensure_future(
            to_runnable_function(
                internal_func=function,
                logger=self.logger,
                request=request,
            )
        )
        wait_until(task)
