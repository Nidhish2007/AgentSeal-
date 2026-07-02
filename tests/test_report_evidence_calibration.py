from agentseal.report import write_html
from agentseal.schemas import AuditConfig, AuditReport, AuditSummary, ContaminationEvidence, InstanceRisk, MatchType, RiskLevel


def _report_with_date_unknown_independent_hits():
    risks = []
    evidence = []
    for i, hits in enumerate([21, 19, 17], start=1):
        instance_id = f"facebook__zstd-{i}"
        risks.append(InstanceRisk(
            instance_id=instance_id,
            repo="facebook/zstd",
            risk=RiskLevel.CRITICAL,
            patch_exposure=1.0,
            independent_hits=hits,
            ngram_overlap_8=1.0,
            merge_date=None,
        ))
        evidence.append(ContaminationEvidence(
            instance_id=instance_id,
            match_type=MatchType.INDEPENDENT_SOURCE_HIT,
            source_url=f"https://github.com/example/repo/blob/abc/file{i}.c#L1-L2",
            source_repo="example/repo",
            similarity=1.0,
            source_kind="github_code_search_verified",
            verification_status="exact_changed_lines",
        ))
    risks.append(InstanceRisk(
        instance_id="facebook__zstd-zero",
        repo="facebook/zstd",
        risk=RiskLevel.HIGH,
        patch_exposure=1.0,
        independent_hits=0,
        ngram_overlap_8=1.0,
        merge_date=None,
    ))
    return AuditReport(
        config=AuditConfig(benchmark="multi-swe-bench", sample_size=0, model_cutoff="2024-03-15"),
        summary=AuditSummary(
            total_instances=len(risks),
            instances_with_patch_exposure=len(risks),
            patch_exposure_rate=1.0,
            critical_count=3,
            high_count=1,
            contamination_rate=1.0,
        ),
        instance_risks=risks,
        evidence=evidence,
    )


def test_html_keeps_missing_temporal_alignment_unknown(tmp_path):
    html = write_html(_report_with_date_unknown_independent_hits(), tmp_path / "report.html").read_text(encoding="utf-8")

    assert "Temporal alignment unavailable" in html
    assert "pre-cutoff corpus rate is unknown" in html
    assert "pre-cutoff contamination rate is 0%" not in html
    assert "The remaining 0 are publicly available now" not in html


def test_html_surfaces_single_repo_concentration_and_excludes_zero_hit_deep_dive(tmp_path):
    html = write_html(_report_with_date_unknown_independent_hits(), tmp_path / "report.html").read_text(encoding="utf-8")

    assert "concentrated entirely in facebook/zstd" in html
    assert "facebook__zstd-zero" not in html
