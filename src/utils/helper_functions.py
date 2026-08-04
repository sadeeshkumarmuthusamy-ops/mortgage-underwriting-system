from typing import Any, Dict, List

def sanitize_pii(data: Dict[str, Any]) -> Dict[str, Any]:
    """Remove or redact personally identifiable information.

    Args:
        data: Raw application data

    Returns:
        Sanitized data safe for LLM processing
    """
    sanitized = data.copy()

    # Redact SSN (keep last 4 digits)
    if 'ssn' in sanitized:
        ssn = sanitized['ssn']
        sanitized['ssn'] = f"***-**-{ssn[-4:]}" if len(ssn) >= 4 else "***-**-XXXX"

    # Replace full names with placeholders
    if 'name' in sanitized:
        sanitized['name'] = "[APPLICANT_NAME]"

    # Redact addresses
    if 'address' in sanitized:
        sanitized['address'] = "[ADDRESS]"

    # Mask phone numbers
    if 'phone' in sanitized:
        phone = sanitized['phone']
        sanitized['phone'] = f"***-***-{phone[-4:]}" if len(phone) >= 4 else "***-***-XXXX"

    return sanitized

def detect_bias_signals(analysis: str, applicant_data: Dict[str, Any]) -> List[str]:
    """Check for potential Fair Lending Act violations.

    Args:
        analysis: Agent's analysis text
        applicant_data: Applicant information

    Returns:
        List of detected bias flags
    """
    flags = []

    # Protected characteristics that shouldn't influence decisions
    protected_terms = [
        'race', 'color', 'religion', 'national origin',
        'sex', 'marital status', 'age', 'gender',
        'disability', 'familial status'
    ]

    # Check if analysis mentions protected characteristics
    analysis_lower = analysis.lower()
    for term in protected_terms:
        if term in analysis_lower:
            flags.append(f"Analysis mentions protected characteristic: {term}")

    # Check for zip code-based discrimination
    if 'zip' in applicant_data or 'zipcode' in applicant_data:
        if 'neighborhood' in analysis_lower or 'area' in analysis_lower:
            flags.append("Potential geographic bias - review for Fair Lending compliance")

    return flags
