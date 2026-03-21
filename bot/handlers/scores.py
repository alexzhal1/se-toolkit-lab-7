def scores(lab_name: str = None) -> str:
    """Placeholder: return score for a lab."""
    if not lab_name:
        return "❌ Please specify a lab name, e.g., /scores lab-04"
    # TODO: Task 2 - fetch score from LMS API
    return f"📊 Score for {lab_name}: 100% (placeholder)"
