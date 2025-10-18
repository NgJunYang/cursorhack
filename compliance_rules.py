"""
Compliance Rules Module for AI Compliance Copilot
Contains MAS 626 AML/CFT, PDPA, and other Singapore financial regulations.
"""

from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class ComplianceRule:
    """Represents a compliance rule with its requirements and checks."""
    id: str
    title: str
    category: str
    severity: int  # 1-5 scale
    description: str
    requirements: List[str]
    keywords: List[str]
    mas_reference: str = ""
    pdpa_reference: str = ""

# MAS 626 AML/CFT Rules
MAS_626_RULES = [
    ComplianceRule(
        id="mas_626_cdd_001",
        title="Customer Due Diligence (CDD) Requirements",
        category="AML/CFT",
        severity=5,
        description="Financial institutions must conduct CDD on all customers before establishing business relationships",
        requirements=[
            "Verify customer identity using reliable documents",
            "Identify beneficial owners of legal entities",
            "Understand the nature and purpose of the business relationship",
            "Conduct ongoing monitoring of the business relationship"
        ],
        keywords=["customer identification", "identity verification", "beneficial owner", "CDD", "due diligence"],
        mas_reference="MAS 626 Section 4.1"
    ),
    ComplianceRule(
        id="mas_626_edd_001",
        title="Enhanced Due Diligence (EDD) for High-Risk Customers",
        category="AML/CFT",
        severity=5,
        description="Enhanced due diligence must be applied to high-risk customers including PEPs",
        requirements=[
            "Obtain senior management approval for high-risk relationships",
            "Conduct enhanced monitoring of transactions",
            "Obtain additional information about source of funds",
            "Conduct more frequent reviews of the relationship"
        ],
        keywords=["enhanced due diligence", "PEP", "politically exposed person", "high risk", "EDD"],
        mas_reference="MAS 626 Section 4.2"
    ),
    ComplianceRule(
        id="mas_626_suspicious_001",
        title="Suspicious Transaction Reporting",
        category="AML/CFT",
        severity=5,
        description="Financial institutions must report suspicious transactions to the Suspicious Transaction Reporting Office",
        requirements=[
            "Report suspicious transactions within 15 days of detection",
            "Maintain confidentiality of STRs",
            "Provide complete and accurate information",
            "Follow up on additional information requests"
        ],
        keywords=["suspicious transaction", "STR", "suspicious activity", "reporting", "STRO"],
        mas_reference="MAS 626 Section 5.1"
    ),
    ComplianceRule(
        id="mas_626_record_001",
        title="Record Keeping Requirements",
        category="AML/CFT",
        severity=4,
        description="Financial institutions must maintain records for at least 5 years",
        requirements=[
            "Maintain customer identification records",
            "Keep transaction records for 5 years",
            "Store records in a readily retrievable format",
            "Ensure records are accessible to MAS upon request"
        ],
        keywords=["record keeping", "5 years", "customer records", "transaction records", "retention"],
        mas_reference="MAS 626 Section 6.1"
    ),
    ComplianceRule(
        id="mas_626_risk_001",
        title="Risk Assessment and Management",
        category="AML/CFT",
        severity=4,
        description="Financial institutions must implement comprehensive risk assessment frameworks",
        requirements=[
            "Conduct regular risk assessments",
            "Implement risk-based controls",
            "Review and update risk assessments annually",
            "Document risk management processes"
        ],
        keywords=["risk assessment", "risk management", "risk-based", "controls", "framework"],
        mas_reference="MAS 626 Section 3.1"
    )
]

# PDPA Rules
PDPA_RULES = [
    ComplianceRule(
        id="pdpa_consent_001",
        title="Consent Management",
        category="PDPA",
        severity=4,
        description="Organizations must obtain valid consent before collecting personal data",
        requirements=[
            "Obtain clear and specific consent",
            "Inform individuals of purpose of collection",
            "Allow withdrawal of consent",
            "Maintain consent records"
        ],
        keywords=["consent", "personal data", "collection", "purpose", "withdrawal"],
        pdpa_reference="PDPA Section 15"
    ),
    ComplianceRule(
        id="pdpa_purpose_001",
        title="Purpose Limitation",
        category="PDPA",
        severity=4,
        description="Personal data must be collected for specific, legitimate purposes",
        requirements=[
            "Specify purpose of data collection",
            "Use data only for stated purposes",
            "Obtain consent for additional uses",
            "Document purpose limitations"
        ],
        keywords=["purpose limitation", "legitimate purpose", "data use", "specific purpose"],
        pdpa_reference="PDPA Section 18"
    ),
    ComplianceRule(
        id="pdpa_accuracy_001",
        title="Data Accuracy and Completeness",
        category="PDPA",
        severity=3,
        description="Organizations must ensure personal data is accurate and complete",
        requirements=[
            "Verify accuracy of personal data",
            "Update data when necessary",
            "Correct inaccurate data promptly",
            "Implement data quality controls"
        ],
        keywords=["data accuracy", "data completeness", "data quality", "verification", "correction"],
        pdpa_reference="PDPA Section 20"
    ),
    ComplianceRule(
        id="pdpa_retention_001",
        title="Data Retention and Disposal",
        category="PDPA",
        severity=4,
        description="Personal data must not be retained longer than necessary",
        requirements=[
            "Establish retention periods",
            "Implement secure disposal methods",
            "Document retention policies",
            "Regular review of retained data"
        ],
        keywords=["data retention", "data disposal", "retention period", "secure disposal"],
        pdpa_reference="PDPA Section 25"
    ),
    ComplianceRule(
        id="pdpa_breach_001",
        title="Data Breach Notification",
        category="PDPA",
        severity=5,
        description="Organizations must notify PDPC of data breaches within 72 hours",
        requirements=[
            "Notify PDPC within 72 hours",
            "Assess impact of breach",
            "Notify affected individuals if necessary",
            "Implement remedial measures"
        ],
        keywords=["data breach", "notification", "72 hours", "PDPC", "breach response"],
        pdpa_reference="PDPA Section 26"
    ),
    ComplianceRule(
        id="pdpa_crossborder_001",
        title="Cross-Border Data Transfer",
        category="PDPA",
        severity=4,
        description="Cross-border transfers must comply with PDPA requirements",
        requirements=[
            "Ensure adequate protection in destination country",
            "Obtain consent for cross-border transfers",
            "Implement appropriate safeguards",
            "Document transfer agreements"
        ],
        keywords=["cross-border", "data transfer", "international", "safeguards", "protection"],
        pdpa_reference="PDPA Section 26"
    )
]

# Cross-Border Transaction Rules
CROSS_BORDER_RULES = [
    ComplianceRule(
        id="cbt_monitoring_001",
        title="Cross-Border Transaction Monitoring",
        category="Cross-Border",
        severity=4,
        description="Financial institutions must monitor cross-border transactions for compliance",
        requirements=[
            "Implement transaction monitoring systems",
            "Flag unusual cross-border patterns",
            "Conduct enhanced due diligence",
            "Report suspicious cross-border activities"
        ],
        keywords=["cross-border", "transaction monitoring", "unusual patterns", "enhanced due diligence"],
        mas_reference="MAS 626 Section 4.3"
    ),
    ComplianceRule(
        id="cbt_reporting_001",
        title="Cross-Border Transaction Reporting",
        category="Cross-Border",
        severity=4,
        description="Certain cross-border transactions must be reported to authorities",
        requirements=[
            "Report large cross-border transactions",
            "Maintain transaction records",
            "Comply with reporting thresholds",
            "Submit reports within required timeframes"
        ],
        keywords=["cross-border reporting", "large transactions", "reporting threshold", "transaction records"],
        mas_reference="MAS 626 Section 5.2"
    )
]

# Sanctions Compliance Rules
SANCTIONS_RULES = [
    ComplianceRule(
        id="sanctions_screening_001",
        title="Sanctions and Watchlist Screening",
        category="Sanctions",
        severity=5,
        description="Financial institutions must screen against sanctions and watchlists",
        requirements=[
            "Screen customers against sanctions lists",
            "Screen transactions against watchlists",
            "Implement real-time screening",
            "Maintain updated sanctions databases"
        ],
        keywords=["sanctions", "watchlist", "screening", "OFAC", "UN sanctions"],
        mas_reference="MAS 626 Section 4.4"
    )
]

# Combine all rules
ALL_COMPLIANCE_RULES = MAS_626_RULES + PDPA_RULES + CROSS_BORDER_RULES + SANCTIONS_RULES

def get_rules_by_category(category: str) -> List[ComplianceRule]:
    """Get compliance rules by category."""
    return [rule for rule in ALL_COMPLIANCE_RULES if rule.category == category]

def get_rules_by_severity(min_severity: int) -> List[ComplianceRule]:
    """Get compliance rules with minimum severity level."""
    return [rule for rule in ALL_COMPLIANCE_RULES if rule.severity >= min_severity]

def search_rules_by_keywords(text: str) -> List[ComplianceRule]:
    """Search compliance rules by keywords in the text."""
    text_lower = text.lower()
    matching_rules = []
    
    for rule in ALL_COMPLIANCE_RULES:
        for keyword in rule.keywords:
            if keyword.lower() in text_lower:
                matching_rules.append(rule)
                break
    
    return matching_rules

def get_rule_by_id(rule_id: str) -> ComplianceRule:
    """Get a specific compliance rule by ID."""
    for rule in ALL_COMPLIANCE_RULES:
        if rule.id == rule_id:
            return rule
    raise ValueError(f"Rule with ID {rule_id} not found")

def generate_compliance_prompt(text: str, filename: str) -> str:
    """Generate a comprehensive compliance analysis prompt."""
    
    # Get relevant rules based on text content
    relevant_rules = search_rules_by_keywords(text)
    
    # Categorize rules
    mas_rules = [rule for rule in relevant_rules if rule.category == "AML/CFT"]
    pdpa_rules = [rule for rule in relevant_rules if rule.category == "PDPA"]
    cross_border_rules = [rule for rule in relevant_rules if rule.category == "Cross-Border"]
    sanctions_rules = [rule for rule in relevant_rules if rule.category == "Sanctions"]
    
    prompt = f"""
Analyze the following financial/legal document for compliance issues with Singapore MAS 626 AML/CFT, PDPA, and cross-border regulations. Return a JSON response with this exact structure:

{{
  "summary": "Executive summary of the document and key compliance findings",
  "overall_risk": 75.5,
  "flags": [
    {{
      "title": "Missing Customer Due Diligence Documentation",
      "severity": 4,
      "why_it_matters": "MAS 626 requires comprehensive CDD for all customers to prevent money laundering",
      "recommendation": "Implement proper CDD procedures including identity verification and beneficial owner identification",
      "evidence": [
        {{
          "page": 1,
          "quote": "Customer information appears incomplete..."
        }}
      ]
    }}
  ]
}}

**Focus Areas for Analysis:**

**MAS 626 AML/CFT Compliance:**
- Customer Due Diligence (CDD) requirements
- Enhanced Due Diligence (EDD) for high-risk customers  
- Suspicious transaction reporting obligations
- Record keeping requirements (5 years minimum)
- Risk assessment and management frameworks
- Politically Exposed Persons (PEPs) screening
- Sanctions and watchlist screening
- Cross-border transaction monitoring
- Cash transaction reporting thresholds

**PDPA (Personal Data Protection Act) Compliance:**
- Consent management and withdrawal mechanisms
- Data collection purpose limitation
- Data accuracy and completeness requirements
- Data retention and disposal policies
- Cross-border data transfer restrictions
- Data breach notification obligations (72 hours)
- Individual rights (access, correction, withdrawal)
- Data protection officer requirements
- Privacy impact assessments

**Cross-Border Transaction Compliance:**
- Transaction monitoring and reporting requirements
- Enhanced due diligence for international transactions
- Sanctions compliance across jurisdictions
- Regulatory reporting obligations

**Specific Rules to Check:**
"""
    
    if mas_rules:
        prompt += "\n**MAS 626 AML/CFT Rules:**\n"
        for rule in mas_rules[:5]:  # Limit to top 5 most relevant
            prompt += f"- {rule.title}: {rule.description}\n"
    
    if pdpa_rules:
        prompt += "\n**PDPA Rules:**\n"
        for rule in pdpa_rules[:5]:
            prompt += f"- {rule.title}: {rule.description}\n"
    
    if cross_border_rules:
        prompt += "\n**Cross-Border Rules:**\n"
        for rule in cross_border_rules[:3]:
            prompt += f"- {rule.title}: {rule.description}\n"
    
    if sanctions_rules:
        prompt += "\n**Sanctions Rules:**\n"
        for rule in sanctions_rules[:3]:
            prompt += f"- {rule.title}: {rule.description}\n"
    
    prompt += f"""

Document: {filename}
Content:
{text}

**Instructions:**
1. Identify specific compliance violations or risks
2. Provide evidence with page numbers and quotes
3. Assign severity scores (1-5) based on regulatory impact
4. Give actionable recommendations for remediation
5. Calculate overall risk score (0-100) based on findings

Return only valid JSON, no additional text.
"""
    
    return prompt