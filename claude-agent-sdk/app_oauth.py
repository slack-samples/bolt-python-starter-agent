import logging
import os

from dotenv import load_dotenv
from slack_bolt.async_app import AsyncApp
from slack_sdk.web.async_client import AsyncWebClient

from listeners import register_listeners
from oauth import oauth_settings

load_dotenv(dotenv_path=".env", override=False)

logging.basicConfig(level=logging.DEBUG)

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
