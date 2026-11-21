import asyncio
import json
import logging
import os
from collections.abc import Awaitable, Callable
from pathlib import Path

from slack_bolt.adapter.asgi.async_handler import AsyncSlackRequestHandler
from slack_bolt.async_app import AsyncApp
from slack_bolt.authorization.authorize_result import AuthorizeResult
from slack_bolt.lazy_listener.async_internals import to_runnable_function
from slack_bolt.lazy_listener.asyncio_runner import AsyncioLazyListenerRunner
from slack_bolt.oauth.async_oauth_settings import AsyncOAuthSettings
from slack_bolt.request.async_request import AsyncBoltRequest
from slack_sdk.web.async_client import AsyncWebClient
from vercel.functions import wait_until

from listeners import register_listeners
from oauth import BlobInstallationStore, RuntimeCacheOAuthStateStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# OAuth settings
# ---------------------------------------------------------------------------

_manifest = json.loads((Path(__file__).parent / "manifest.json").read_text())
BOT_SCOPES = _manifest["oauth_config"]["scopes"]["bot"]
USER_SCOPES = _manifest["oauth_config"]["scopes"]["user"]

installation_store = BlobInstallationStore()

state_store = RuntimeCacheOAuthStateStore()

oauth_settings = AsyncOAuthSettings(
    client_id=os.environ.get("SLACK_CLIENT_ID"),
    client_secret=os.environ.get("SLACK_CLIENT_SECRET"),
    scopes=BOT_SCOPES,
    user_scopes=USER_SCOPES,
    installation_store=installation_store,
    state_store=state_store,
)

# ---------------------------------------------------------------------------
# Bot-token fallback for pre-OAuth first-run experience
# ---------------------------------------------------------------------------
# When SLACK_BOT_TOKEN is set, Bolt clears it because oauth_settings is
# present. This wrapper lets the bot token serve as a fallback so App Home
# (with the OAuth install URL) and basic bot operations work before anyone
# has completed the OAuth flow.

_fallback_bot_token = os.environ.get("SLACK_BOT_TOKEN")

if _fallback_bot_token:
    _original_authorize = oauth_settings.authorize

    async def _authorize_with_fallback_bot_token(
        *,
        context,
        enterprise_id,
        team_id,
        user_id,
        actor_enterprise_id=None,
        actor_team_id=None,
        actor_user_id=None,
    ):
        result = await _original_authorize(
            context=context,
            enterprise_id=enterprise_id,
            team_id=team_id,
            user_id=user_id,
            actor_enterprise_id=actor_enterprise_id,
            actor_team_id=actor_team_id,
            actor_user_id=actor_user_id,
        )
        if result is not None:
            return result

        logger.info(
            "No OAuth installation found (team=%s); falling back to SLACK_BOT_TOKEN",
            team_id,
        )
        try:
            fallback_client = AsyncWebClient(
                base_url=os.environ.get("SLACK_API_URL", "https://slack.com/api"),
                token=_fallback_bot_token,
            )
            auth_test = await fallback_client.auth_test()
            return AuthorizeResult.from_auth_test_response(
                auth_test_response=auth_test,
                bot_token=_fallback_bot_token,
            )
        except Exception:
            logger.exception("Fallback bot token auth.test failed")
            return None

    oauth_settings.authorize = _authorize_with_fallback_bot_token


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


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = AsyncApp(
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
    token=os.environ.get("SLACK_BOT_TOKEN"),
    client=AsyncWebClient(
        base_url=os.environ.get("SLACK_API_URL", "https://slack.com/api"),
        token=os.environ.get("SLACK_BOT_TOKEN"),
    ),
    oauth_settings=oauth_settings,
    process_before_response=True,
)

register_listeners(app)

app.listener_runner.lazy_listener_runner = WaitUntilLazyListenerRunner(app.logger)

handler = AsyncSlackRequestHandler(app)
