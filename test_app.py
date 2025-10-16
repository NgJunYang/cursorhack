import pytest
import json
from unittest.mock import Mock, patch
from app import analyze_chunks, extract_text_from_pdf, AnalysisResult, ComplianceFlag, Evidence

def test_analyze_chunks_valid_response():
    """Test that analyze_chunks produces valid schema with mock Groq response."""
    
    # Mock Groq response
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = json.dumps({
        "summary": "Test document analysis completed",
        "overall_risk": 75.5,
        "flags": [
            {
                "title": "Cross-Border Transaction Risk",
                "severity": 4,
                "why_it_matters": "This transaction involves multiple jurisdictions",
                "recommendation": "Conduct thorough due diligence",
                "evidence": [
                    {
                        "page": 1,
                        "quote": "Transaction involves entities in US, EU, and Singapore with different regulatory requirements."
                    }
                ]
            }
        ]
    })
    
    with patch('app.groq_client') as mock_groq:
        mock_groq.chat.completions.create.return_value = mock_response
        
        result = analyze_chunks("Test document content", "test.pdf")
        
        # Validate result structure
        assert isinstance(result, AnalysisResult)
        assert isinstance(result.summary, str)
        assert isinstance(result.overall_risk, float)
        assert 0 <= result.overall_risk <= 100
        assert isinstance(result.flags, list)
        
        # Validate flags structure
        for flag in result.flags:
            assert isinstance(flag, ComplianceFlag)
            assert isinstance(flag.title, str)
            assert 1 <= flag.severity <= 5
            assert isinstance(flag.why_it_matters, str)
            assert isinstance(flag.recommendation, str)
            assert isinstance(flag.evidence, list)
            
            # Validate evidence structure
            for evidence in flag.evidence:
                assert isinstance(evidence, Evidence)
                assert isinstance(evidence.page, int)
                assert isinstance(evidence.quote, str)
                assert len(evidence.quote) <= 600

def test_analyze_chunks_missing_overall_risk():
    """Test that overall_risk is calculated from severity when missing."""
    
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = json.dumps({
        "summary": "Test analysis",
        "flags": [
            {
                "title": "Test Issue",
                "severity": 3,
                "why_it_matters": "Test reason",
                "recommendation": "Test recommendation",
                "evidence": []
            },
            {
                "title": "Another Issue",
                "severity": 5,
                "why_it_matters": "Another reason",
                "recommendation": "Another recommendation",
                "evidence": []
            }
        ]
    })
    
    with patch('app.groq_client') as mock_groq:
        mock_groq.chat.completions.create.return_value = mock_response
        
        result = analyze_chunks("Test content", "test.pdf")
        
        # Should calculate overall_risk as average severity / 5 * 100
        expected_risk = ((3 + 5) / 2) / 5 * 100  # 80.0
        assert result.overall_risk == expected_risk

def test_analyze_chunks_invalid_json():
    """Test handling of invalid JSON response."""
    
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "This is not valid JSON"
    
    with patch('app.groq_client') as mock_groq:
        mock_groq.chat.completions.create.return_value = mock_response
        
        with pytest.raises(Exception):  # Should raise an exception
            analyze_chunks("Test content", "test.pdf")

def test_analyze_chunks_quote_truncation():
    """Test that quotes are truncated to 600 characters."""
    
    long_quote = "A" * 700  # 700 character quote
    
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = json.dumps({
        "summary": "Test analysis",
        "overall_risk": 50.0,
        "flags": [
            {
                "title": "Test Issue",
                "severity": 3,
                "why_it_matters": "Test reason",
                "recommendation": "Test recommendation",
                "evidence": [
                    {
                        "page": 1,
                        "quote": long_quote
                    }
                ]
            }
        ]
    })
    
    with patch('app.groq_client') as mock_groq:
        mock_groq.chat.completions.create.return_value = mock_response
        
        result = analyze_chunks("Test content", "test.pdf")
        
        # Quote should be truncated to 600 characters
        assert len(result.flags[0].evidence[0].quote) == 600

def test_analyze_chunks_severity_bounds():
    """Test that severity is clamped to 1-5 range."""
    
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = json.dumps({
        "summary": "Test analysis",
        "overall_risk": 50.0,
        "flags": [
            {
                "title": "Low Severity",
                "severity": 0,  # Below minimum
                "why_it_matters": "Test reason",
                "recommendation": "Test recommendation",
                "evidence": []
            },
            {
                "title": "High Severity",
                "severity": 10,  # Above maximum
                "why_it_matters": "Test reason",
                "recommendation": "Test recommendation",
                "evidence": []
            }
        ]
    })
    
    with patch('app.groq_client') as mock_groq:
        mock_groq.chat.completions.create.return_value = mock_response
        
        result = analyze_chunks("Test content", "test.pdf")
        
        # Severity should be clamped
        assert result.flags[0].severity == 1  # Clamped to minimum
        assert result.flags[1].severity == 5  # Clamped to maximum

def test_analyze_chunks_overall_risk_bounds():
    """Test that overall_risk is clamped to 0-100 range."""
    
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = json.dumps({
        "summary": "Test analysis",
        "overall_risk": 150.0,  # Above maximum
        "flags": []
    })
    
    with patch('app.groq_client') as mock_groq:
        mock_groq.chat.completions.create.return_value = mock_response
        
        result = analyze_chunks("Test content", "test.pdf")
        
        # Overall risk should be clamped to 100
        assert result.overall_risk == 100.0

if __name__ == "__main__":
    pytest.main([__file__])