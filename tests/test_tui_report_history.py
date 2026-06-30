from pathlib import Path

from agentseal.tui import AgentSealApp


def test_report_history_scans_auto_report_directory():
    app = AgentSealApp()

    report_dirs = {str(p.expanduser()) for p in app._report_dirs()}

    assert str(Path.home() / ".agentseal" / "reports") in report_dirs

