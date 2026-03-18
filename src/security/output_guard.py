import re

def check_output(output_text: str) -> tuple[bool, str]:
    """Check output for sensitive data leakage and quality issues."""
    if not output_text or not output_text.strip():
        return False, "Blocked: empty output"

    text_lower = output_text.lower()

    # Check for system prompt leakage
    leakage_patterns = [
        "you are a financial analyst",  # Your system prompt leaking
        "adhere to the following rules",
        "source restriction:",
        "system prompt",
        "openai_api_key",
        "sk-",  # API key pattern
    ]

    for pattern in leakage_patterns:
        if pattern in text_lower:
            return False, "Blocked: potential system information leakage"

    # Check for PII patterns
    email_pattern = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', output_text)
    phone_pattern = re.findall(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', output_text)
    
    if email_pattern or phone_pattern:
        return False, "Blocked: PII detected in output"

    # Check for excessive length
    if len(output_text) > 15000:
        return False, "Blocked: output too long"

    return True, "Passed output check"