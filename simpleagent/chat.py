"""Interactive command-line chat with SimpleAgent.

    python -m simpleagent.chat

Each run starts a new session (a fresh cloud sandbox) for the agent created by
setup_agent.py. Type 'exit' or press Ctrl+D to quit.
"""

import json
import sys

import anthropic

from simpleagent.config import load_state

EXIT_WORDS = {"exit", "quit", "bye"}


def ask_approval(event) -> bool:
    """Ask the person at the terminal whether a paused tool call may run."""
    details = json.dumps(getattr(event, "input", {}) or {}, indent=2)
    print(f"\n[SimpleAgent wants to use '{event.name}']\n{details}")
    answer = input("Allow? [y/N] ").strip().lower()
    return answer in {"y", "yes"}


def run_turn(client: anthropic.Anthropic, session_id: str, text: str) -> None:
    """Send one user message and print the agent's reply until it finishes."""
    # Open the stream first so no events are missed, then send the message.
    with client.beta.sessions.events.stream(session_id=session_id) as stream:
        client.beta.sessions.events.send(
            session_id=session_id,
            events=[{"type": "user.message", "content": [{"type": "text", "text": text}]}],
        )
        for event in stream:
            if event.type == "agent.message":
                for block in event.content:
                    if block.type == "text":
                        print(block.text, end="", flush=True)
            elif event.type in ("agent.tool_use", "agent.mcp_tool_use"):
                if getattr(event, "evaluated_permission", None) == "ask":
                    allowed = ask_approval(event)
                    client.beta.sessions.events.send(
                        session_id=session_id,
                        events=[{
                            "type": "user.tool_confirmation",
                            "tool_use_id": event.id,
                            "result": "allow" if allowed else "deny",
                        }],
                    )
                else:
                    print(f"\n[using tool: {event.name}]", flush=True)
            elif event.type == "session.error":
                print(f"\n[error: {getattr(event, 'error', event)}]", file=sys.stderr)
            elif event.type == "session.status_idle":
                stop_reason = getattr(event, "stop_reason", None)
                if getattr(stop_reason, "type", None) != "requires_action":
                    break
            elif event.type == "session.status_terminated":
                print("\n[session ended]")
                raise SystemExit(1)
    print()


def main() -> None:
    state = load_state()
    if "agent_id" not in state or "environment_id" not in state:
        sys.exit("SimpleAgent is not set up yet. Run: python -m simpleagent.setup_agent")

    client = anthropic.Anthropic()
    session = client.beta.sessions.create(
        agent=state["agent_id"],
        environment_id=state["environment_id"],
        title="SimpleAgent chat",
    )
    print(f"SimpleAgent is ready (session {session.id}). Type 'exit' to quit.\n")

    while True:
        try:
            text = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not text:
            continue
        if text.lower() in EXIT_WORDS:
            break
        print("SimpleAgent: ", end="", flush=True)
        try:
            run_turn(client, session.id, text)
        except anthropic.APIError as err:
            print(f"\n[API error: {err}]", file=sys.stderr)


if __name__ == "__main__":
    main()
