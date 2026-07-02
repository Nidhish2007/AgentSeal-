import json
from agentseal.report import read_json
from agentseal.schemas import AuditConfig, AuditReport, AuditSummary, InstanceRisk, RiskLevel


def test_read_json_tolerates_float_rounding_above_one(tmp_path):
    report = AuditReport(
        config=AuditConfig(benchmark="rounding"),
        summary=AuditSummary(total_instances=1),
        instance_risks=[InstanceRisk(
            instance_id="one",
            repo="org/repo",
            risk=RiskLevel.CLEAN,
            embedding_similarity=1.0,
        )],
    )
    data = report.model_dump(mode="json")
    data["instance_risks"][0]["embedding_similarity"] = 1.0000000000000002
    path = tmp_path / "report.json"
    path.write_text(json.dumps(data), encoding="utf-8")

    loaded = read_json(path)

    assert loaded.instance_risks[0].embedding_similarity == 1.0
