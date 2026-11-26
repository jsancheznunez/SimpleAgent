"""Offline tests for the chat loop. They use a fake client, so no API key is needed.

    python -m unittest discover tests
"""

import io
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace as NS
from unittest import mock

from simpleagent import chat


class FakeStream:
    def __init__(self, events):
        self.events = events

    def __enter__(self):
        return iter(self.events)

    def __exit__(self, *exc):
        return False


def fake_client(events):
    sent = []
    client = mock.Mock()
    client.beta.sessions.events.stream.return_value = FakeStream(events)
    client.beta.sessions.events.send.side_effect = lambda **kw: sent.extend(kw["events"])
    return client, sent


def text_message(text):
    return NS(type="agent.message", content=[NS(type="text", text=text)])


def idle(reason="end_turn"):
    return NS(type="session.status_idle", stop_reason=NS(type=reason))


class RunTurnTests(unittest.TestCase):
    def test_prints_reply_and_stops_when_idle(self):
        client, sent = fake_client([text_message("Hello!"), idle(), text_message("never shown")])
        out = io.StringIO()
        with redirect_stdout(out):
            chat.run_turn(client, "sesn_1", "Hi")
        self.assertIn("Hello!", out.getvalue())
        self.assertNotIn("never shown", out.getvalue())
        self.assertEqual(sent[0]["type"], "user.message")
        self.assertEqual(sent[0]["content"][0]["text"], "Hi")

    def test_asks_before_paused_tool_call(self):
        tool = NS(type="agent.tool_use", id="sevt_9", name="bash",
                  input={"command": "ls"}, evaluated_permission="ask")
        client, sent = fake_client([tool, idle("requires_action"), text_message("Done"), idle()])
        out = io.StringIO()
        with redirect_stdout(out), mock.patch("builtins.input", return_value="y"):
            chat.run_turn(client, "sesn_1", "List files")
        self.assertEqual(sent[1], {"type": "user.tool_confirmation",
                                   "tool_use_id": "sevt_9", "result": "allow"})
        self.assertIn("Done", out.getvalue())

    def test_denies_tool_call_by_default(self):
        tool = NS(type="agent.tool_use", id="sevt_9", name="bash",
                  input={"command": "rm -rf /tmp/x"}, evaluated_permission="ask")
        client, sent = fake_client([tool, idle()])
        with redirect_stdout(io.StringIO()), mock.patch("builtins.input", return_value=""):
            chat.run_turn(client, "sesn_1", "Clean up")
        self.assertEqual(sent[1]["result"], "deny")


if __name__ == "__main__":
    unittest.main()
