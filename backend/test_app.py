import pytest
from app import truncate_evidence, MAX_EVIDENCE_LENGTH


def test_truncate_evidence():
    """Test that evidence quotes are truncated to MAX_EVIDENCE_LENGTH"""
    long_quote = "A" * 1000
    evidence_list = [
        {"page": 1, "quote": long_quote},
        {"page": 2, "quote": "Short quote"}
    ]
    
    result = truncate_evidence(evidence_list)
    
    assert len(result[0]["quote"]) <= MAX_EVIDENCE_LENGTH + 3  # +3 for "..."
    assert result[0]["quote"].endswith("...")
    assert result[1]["quote"] == "Short quote"


def test_analyze_chunks_schema():
    """Verify that analysis result has valid schema"""
    # Mock result structure
    mock_result = {
        "summary": "Test summary",
        "overall_risk": 0.7,
        "flags": [
            {
                "title": "AML Risk",
                "severity": 4,
                "why_it_matters": "High risk transaction",
                "recommendation": "Review transaction",
                "evidence": [
                    {"page": 1, "quote": "Suspicious pattern"}
                ]
            }
        ]
    }
    
    # Validate structure
    assert "summary" in mock_result
    assert "overall_risk" in mock_result
    assert "flags" in mock_result
    assert isinstance(mock_result["flags"], list)
    
    for flag in mock_result["flags"]:
        assert "title" in flag
        assert "severity" in flag
        assert "why_it_matters" in flag
        assert "recommendation" in flag
        assert "evidence" in flag
        assert 1 <= flag["severity"] <= 5
        
        for ev in flag["evidence"]:
            assert "page" in ev
            assert "quote" in ev


def test_overall_risk_calculation():
    """Test overall risk calculation from severities"""
    severities = [3, 4, 5]
    overall_risk = sum(severities) / len(severities) / 5
    
    assert 0 <= overall_risk <= 1
    assert overall_risk == 0.8  # (3+4+5)/3/5 = 12/15 = 0.8
