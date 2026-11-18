import asyncio
import logging
from unittest.mock import patch

import pytest
from slack_bolt.request.async_request import AsyncBoltRequest

from wait_until_runner import WaitUntilLazyListenerRunner

test_logger = logging.getLogger(__name__)


class TestWaitUntilLazyListenerRunner:
    def setup_method(self):
        self.runner = WaitUntilLazyListenerRunner(test_logger)
        self.request = AsyncBoltRequest(body="{}", headers={})
        self.finished = asyncio.Event()

    async def lazy_function(self):
        self.finished.set()

    @pytest.mark.asyncio
    async def test_runner_hands_task_to_wait_until(self):
        with patch("wait_until_runner.wait_until") as fake_wait_until:
            self.runner.start(function=self.lazy_function, request=self.request)

        fake_wait_until.assert_called_once()
        task = fake_wait_until.call_args.args[0]
        assert isinstance(task, asyncio.Task)
        await task
        assert self.finished.is_set()

    @pytest.mark.asyncio
    async def test_runner_runs_without_vercel_context(self):
        self.runner.start(function=self.lazy_function, request=self.request)

        await asyncio.wait_for(self.finished.wait(), timeout=1)
