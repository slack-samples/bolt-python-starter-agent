from dataclasses import dataclass

from slack_sdk.web.async_client import AsyncWebClient


@dataclass
class AgentDeps:
    client: AsyncWebClient
    user_id: str
    channel_id: str
    thread_ts: str
    message_ts: str
    user_token: str | None = None
