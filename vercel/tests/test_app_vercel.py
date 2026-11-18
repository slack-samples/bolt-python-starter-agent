import importlib
import json
import time
from unittest.mock import AsyncMock, patch

import pytest
from slack_bolt.context.async_context import AsyncBoltContext
from slack_sdk.signature import SignatureVerifier
from vercel.blob import BlobNotFoundError


@pytest.fixture(scope="module")
def app_vercel():
    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setenv("SLACK_SIGNING_SECRET", "test-secret")
        monkeypatch.setenv("SLACK_CLIENT_ID", "111.222")
        monkeypatch.setenv("SLACK_CLIENT_SECRET", "test-client-secret")
        monkeypatch.setenv("SLACK_BOT_TOKEN", "xoxb-fallback")
        yield importlib.import_module("app_vercel")


async def post_event(handler, body: str, signature: str | None = None) -> dict:
    timestamp = str(int(time.time()))
    if signature is None:
        signature = SignatureVerifier("test-secret").generate_signature(
            timestamp=timestamp, body=body
        )
    scope = {
        "type": "http",
        "method": "POST",
        "path": "/slack/events",
        "query_string": b"",
        "headers": [
            (b"content-type", b"application/json"),
            (b"x-slack-request-timestamp", timestamp.encode()),
            (b"x-slack-signature", signature.encode()),
        ],
    }
    sent = []

    async def receive():
        return {"type": "http.request", "body": body.encode(), "more_body": False}

    async def send(message):
        sent.append(message)

    await handler(scope, receive, send)
    return {"status": sent[0]["status"], "body": sent[1]["body"]}


class TestAppVercel:
    @pytest.mark.asyncio
    async def test_answers_url_verification(self, app_vercel):
        response = await post_event(
            app_vercel.handler,
            json.dumps({"type": "url_verification", "challenge": "abc"}),
        )

        assert response["status"] == 200
        assert b"abc" in response["body"]

    @pytest.mark.asyncio
    async def test_rejects_bad_signature(self, app_vercel):
        response = await post_event(
            app_vercel.handler,
            json.dumps({"type": "url_verification", "challenge": "abc"}),
            signature="v0=bad",
        )

        assert response["status"] == 401

    @pytest.mark.asyncio
    async def test_falls_back_to_bot_token(self, app_vercel):
        with (
            patch("vercel.blob.get_blob", AsyncMock(side_effect=BlobNotFoundError())),
            patch(
                "slack_sdk.web.async_client.AsyncWebClient.auth_test",
                AsyncMock(
                    return_value={
                        "team_id": "T1",
                        "user_id": "UBOT",
                        "bot_id": "B1",
                    }
                ),
            ),
        ):
            result = await app_vercel.oauth_settings.authorize(
                context=AsyncBoltContext(),
                enterprise_id=None,
                team_id="T1",
                user_id="U1",
            )

        assert result.bot_token == "xoxb-fallback"
        assert result.bot_user_id == "UBOT"
