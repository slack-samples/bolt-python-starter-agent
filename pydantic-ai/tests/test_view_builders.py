from listeners.views.app_home_builder import build_app_home_view
from listeners.views.feedback_builder import build_feedback_blocks


def test_build_feedback_blocks():
    blocks = build_feedback_blocks()

    assert len(blocks) > 0
    # The block should contain a feedback action
    block_dict = blocks[0].to_dict()
    action_ids = [e["action_id"] for e in block_dict["elements"]]
    assert "feedback" in action_ids


def test_build_app_home_view_default():
    """Default args (app.py mode) — no MCP status section."""
    view = build_app_home_view()

    assert view["type"] == "home"

    # Should have a header and a section
    block_types = [b["type"] for b in view["blocks"]]
    assert "header" in block_types
    assert "section" in block_types

    # No MCP status section
    section_texts = [
        b["text"]["text"] for b in view["blocks"] if b["type"] == "section"
    ]
    assert not any("Slack MCP Server" in t for t in section_texts)


def test_build_app_home_view_connect():
    """install_url provided — shows disconnected status with install link."""
    view = build_app_home_view(install_url="https://example.com/slack/install")

    section_texts = [
        b["text"]["text"] for b in view["blocks"] if b["type"] == "section"
    ]
    mcp_section = next(t for t in section_texts if "Slack MCP Server" in t)
    assert "disconnected" in mcp_section
    assert "https://example.com/slack/install" in mcp_section


def test_build_app_home_view_connected():
    """is_connected=True — shows connected status."""
    view = build_app_home_view(is_connected=True)

    section_texts = [
        b["text"]["text"] for b in view["blocks"] if b["type"] == "section"
    ]
    mcp_section = next(t for t in section_texts if "Slack MCP Server" in t)
    assert "connected" in mcp_section
