import json
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from slack_bolt.authorization.authorize_result import AuthorizeResult
from slack_bolt.async_app import AsyncApp
from slack_bolt.oauth.async_oauth_settings import AsyncOAuthSettings
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.oauth.installation_store import FileInstallationStore
from slack_sdk.oauth.state_store import FileOAuthStateStore

from listeners import register_listeners

load_dotenv(dotenv_path=".env", override=False)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# OAuth settings
# ---------------------------------------------------------------------------

_manifest = json.loads(Path("manifest.json").read_text())
BOT_SCOPES = _manifest["oauth_config"]["scopes"]["bot"]
USER_SCOPES = _manifest["oauth_config"]["scopes"]["user"]

installation_store = FileInstallationStore(
    base_dir="./data/installations",
)

state_store = FileOAuthStateStore(
    expiration_seconds=600,
    base_dir="./data/states",
)

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
# When installed via Slack CLI, SLACK_BOT_TOKEN is available but Bolt clears
# it when oauth_settings is present. This wrapper lets the bot token serve as
# a fallback so App Home (with the OAuth install URL) and basic bot operations
# work before anyone has completed the OAuth flow.

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
)

register_listeners(app)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.start(port=port)
