"""One-time setup: create (or update) the SimpleAgent agent and its environment.

Run this once, and again whenever you change prompts/system_prompt.md or the
tools in config.py. It stores the IDs in .simpleagent.json so chat.py can reuse
them instead of creating a new agent on every run.

    python -m simpleagent.setup_agent
"""

import anthropic

from simpleagent.config import AGENT_NAME, MODEL, TOOLS, load_state, load_system_prompt, save_state


def main() -> None:
    client = anthropic.Anthropic()
    state = load_state()
    system_prompt = load_system_prompt()

    if "environment_id" not in state:
        environment = client.beta.environments.create(
            name="simpleagent-env",
            config={
                "type": "cloud",
                "networking": {
                    "type": "limited",
                    "allow_package_managers": True,
                    "allow_mcp_servers": True,
                },
            },
        )
        state["environment_id"] = environment.id
        print(f"Created environment {environment.id}")
    else:
        print(f"Using environment {state['environment_id']}")

    if "agent_id" not in state:
        agent = client.beta.agents.create(
            name=AGENT_NAME,
            model=MODEL,
            system=system_prompt,
            tools=TOOLS,
        )
        print(f"Created agent {agent.id} (version {agent.version})")
    else:
        current = client.beta.agents.retrieve(state["agent_id"])
        agent = client.beta.agents.update(
            state["agent_id"],
            version=current.version,
            model=MODEL,
            system=system_prompt,
            tools=TOOLS,
        )
        print(f"Updated agent {agent.id} (now version {agent.version})")

    state["agent_id"] = agent.id
    save_state(state)
    print("Saved IDs to .simpleagent.json. Start chatting with: python -m simpleagent.chat")


if __name__ == "__main__":
    main()
