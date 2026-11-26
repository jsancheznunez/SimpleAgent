# SimpleAgent

A simple general-purpose AI agent that understands instructions, answers questions, analyzes information, and helps complete everyday tasks.

SimpleAgent is written in Python and runs on Anthropic's Claude (`claude-opus-5-5`) through
[Claude Managed Agents](https://platform.claude.com/docs/en/managed-agents/overview) (beta).
Anthropic hosts the agent loop and a cloud sandbox where the agent's tools run (shell
commands, reading and writing files). You chat with it from your terminal.

> **Costs and data:** Managed Agents bills session runtime on top of model tokens, and
> keeps session history until you delete it.

## Project layout

| Path | What it is |
|---|---|
| `prompts/system_prompt.md` | The agent's instructions: mission, responsibilities, rules, behavior |
| `simpleagent/config.py` | Model, tools and file paths |
| `simpleagent/setup_agent.py` | One-time setup: creates the agent and its cloud environment |
| `simpleagent/chat.py` | The command-line chat |
| `tests/` | Offline tests (no API key needed) |

## Setup

1. Install Python 3.10 or newer, then the dependency:

   ```bash
   pip install -r requirements.txt
   ```

2. Get an API key at <https://platform.claude.com/> and set it:

   ```bash
   export ANTHROPIC_API_KEY="sk-ant-..."
   ```

3. Create the agent (once):

   ```bash
   python -m simpleagent.setup_agent
   ```

   This saves the agent and environment IDs to `.simpleagent.json`. Run it again after you
   edit `prompts/system_prompt.md` or the tools in `simpleagent/config.py`; it updates the
   same agent instead of creating a new one.

## Chat

```bash
python -m simpleagent.chat
```

Type your request, and type `exit` to quit. If the agent wants to run a tool call that
needs your approval, it shows the call and asks `Allow? [y/N]` (Enter means no).

## Testing

**Offline tests** check the chat logic with a fake API, so they need no key and cost nothing:

```bash
python -m unittest discover tests
```

**Live test** with a real key: run setup, start the chat, and try prompts that exercise
each responsibility in the system prompt, for example:

- "What's the difference between a list and a tuple in Python?" (answers a question)
- "Plan a 3-day study schedule for learning SQL." (breaks a task into steps)
- "Book me a flight." (should ask for the missing details)
- "Create a file with 10 random numbers, then tell me their average." (uses tools and verifies)

You can review every session, including tool calls and cost, in the
[Claude Console](https://platform.claude.com/) under Managed Agents → Sessions.

## Turning on web research

Web search and web fetch are off by default. To let the agent research online, set
`web_search` and `web_fetch` to `"enabled": True` in `simpleagent/config.py`, allow the
sites it needs in the environment's networking, and run `python -m simpleagent.setup_agent`
again.
