from agentseal.auto_discover import (
    BenchmarkInfo,
    _auto_large_jsonl_sample_size,
    _read_jsonl_dataframe_streaming,
    _stream_jsonl_stratified_sample,
)


def test_jsonl_loader_streams_progress_and_skips_bad_lines(tmp_path):
    data_file = tmp_path / "sample.jsonl"
    with data_file.open("w", encoding="utf-8") as f:
        for i in range(1200):
            f.write('{"instance_id":"case-%04d","patch":"diff --git a/x b/x","repo":"org/repo"}\n' % i)
        f.write("{not-json}\n")
        f.write("\n")

    events = []
    df = _read_jsonl_dataframe_streaming(data_file, progress_callback=lambda stage, msg: events.append((stage, msg)))

    assert len(df) == 1200
    assert "instance_id" in df.columns
    assert any("Streaming JSONL" in msg for _, msg in events)
    assert any("Building dataframe" in msg for _, msg in events)
    assert not any("Reading JSONL in chunks" in msg for _, msg in events)


def test_auto_large_jsonl_guard_uses_streamed_sample_by_default(tmp_path, monkeypatch):
    data_file = tmp_path / "large.jsonl"
    data_file.write_text('{"instance_id":"one"}\n', encoding="utf-8")
    info = BenchmarkInfo(
        name="big-bench",
        hf_id="owner/big-bench",
        instances=100,
        audit_type="pr_diff",
        languages=["python"],
    )
    events = []
    monkeypatch.setenv("AGENTSEAL_AUTO_FULL_JSONL_BYTES", "1")
    monkeypatch.setenv("AGENTSEAL_AUTO_DEFAULT_SAMPLE", "7")

    sample_size = _auto_large_jsonl_sample_size(
        data_file,
        info,
        requested_sample_size=0,
        progress_callback=lambda stage, msg: events.append((stage, msg)),
    )

    assert sample_size == 7
    assert any("Large JSONL" in msg and "streaming stratified sample" in msg for _, msg in events)


def test_huge_jsonl_sample_stops_after_requested_rows(tmp_path, monkeypatch):
    data_file = tmp_path / "large.jsonl"
    with data_file.open("w", encoding="utf-8") as f:
        for i in range(100):
            f.write('{"instance_id":"case-%04d","repo":"org/repo","patch":"diff"}\n' % i)
    events = []
    monkeypatch.setenv("AGENTSEAL_AUTO_FULL_JSONL_BYTES", "1")

    df = _stream_jsonl_stratified_sample(
        data_file,
        sample_size=5,
        progress_callback=lambda stage, msg: events.append((stage, msg)),
    )

    assert len(df) == 5
    assert any("from 5 scanned lines" in msg for _, msg in events)
