import json
from app import analyze_chunks, ReportOut


def test_analyze_chunks_schema(monkeypatch):
    # Provide a fake Groq response to avoid external calls
    sample = {
        "summary": "This document contains potential cross-border and AML risks.",
        "overall_risk": 60.0,
        "flags": [
            {
                "title": "Cross-Border Transactions",
                "severity": 4,
                "why_it_matters": "May trigger additional KYC/AML checks.",
                "recommendation": "Implement enhanced due diligence.",
                "evidence": [{"page": 2, "quote": "Payments routed via multiple jurisdictions."}],
            }
        ],
    }

    def fake_call_groq_json(chunk: str, retry: int = 2):
        return json.loads(json.dumps(sample))

    monkeypatch.setattr("app.call_groq_json", fake_call_groq_json)

    chunks = [
        "Client engages in cross-border remittances between Singapore and non-FATF countries.",
        "Funds are commingled across multiple entities and offshore accounts.",
    ]

    report = analyze_chunks(chunks)

    # Validate against Pydantic schema
    parsed = ReportOut(**report)

    assert parsed.summary
    assert 0.0 <= parsed.overall_risk <= 100.0
    assert len(parsed.flags) >= 1
    assert 1 <= parsed.flags[0].severity <= 5
    for f in parsed.flags:
        for ev in f.evidence:
            assert len(ev.quote) <= 600
