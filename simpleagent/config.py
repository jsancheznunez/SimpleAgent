"""Shared settings and the local file that stores the agent and environment IDs."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SYSTEM_PROMPT_PATH = ROOT / "prompts" / "system_prompt.md"
STATE_PATH = ROOT / ".simpleagent.json"

AGENT_NAME = "SimpleAgent"
MODEL = "claude-opus-5-5"

# Tools the agent can use inside its cloud sandbox (bash, file read/write/edit, ...).
# Web search and web fetch are off by default; set them to True to let the agent
# research online, and also allow the hosts it needs in the environment networking.
TOOLS = [
    {
        "type": "agent_toolset_20260401",
        "default_config": {"enabled": True, "permission_policy": {"type": "auto"}},
        "configs": [
            {"name": "web_fetch", "enabled": False},
            {"name": "web_search", "enabled": False},
        ],
    },
]


def load_system_prompt() -> str:
    return SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")


def load_state() -> dict:
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    return {}


def save_state(state: dict) -> None:
    STATE_PATH.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
