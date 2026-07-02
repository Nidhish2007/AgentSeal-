import inspect
import os

import agentseal.github_auth as github_auth
from agentseal.tui import AgentSealApp


def test_hf_token_rejects_non_hf_text(monkeypatch):
    app = AgentSealApp()
    messages: list[str] = []
    monkeypatch.setattr(app, "_log", lambda text: messages.append(str(text)))
    monkeypatch.delenv("HF_TOKEN", raising=False)

    app._set_and_persist_hf_token("not actually a huggingface token")

    assert "HF_TOKEN" not in os.environ
    assert any("Rejected" in msg for msg in messages)


def test_auto_audit_worker_opens_html_report():
    source = inspect.getsource(AgentSealApp._cmd_auto)

    assert "open_in_browser(html_path.resolve())" in source


def test_worker_ui_call_does_not_raise_when_textual_runtime_is_unavailable(monkeypatch):
    app = AgentSealApp()
    called = []

    monkeypatch.setattr(app, "call_from_thread", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("no app")))

    app._safe_call(lambda value: called.append(value), "ok")

    assert called == ["ok"]


def test_hf_auth_layer_ignores_invalid_env_and_file(monkeypatch, tmp_path):
    token_file = tmp_path / "hf_token"
    token_file.write_text("not-a-token", encoding="utf-8")
    monkeypatch.setattr(github_auth, "_HF_TOKEN_FILE", token_file)
    monkeypatch.setenv("HF_TOKEN", "definitely-not-valid")
    monkeypatch.delenv("HUGGING_FACE_HUB_TOKEN", raising=False)

    assert github_auth.get_hf_token() is None
    assert not github_auth.has_hf_token()


def test_reasoning_log_is_bounded_for_large_audits(monkeypatch):
    app = AgentSealApp()
    writes = []

    class FakeLog:
        def write(self, value):
            writes.append(str(value))

    monkeypatch.setattr(app, "query_one", lambda *a, **k: FakeLog())

    for i in range(app.MAX_REASONING_LINES + 50):
        app._log_reasoning(f"line {i}")

    assert len(writes) <= app.MAX_REASONING_LINES + 2
    assert app._reasoning_dropped > 0
