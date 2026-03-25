import requests
from services.lms_api import LmsApiClient


def scores(lab_name: str = None) -> str:
    """Return per-task pass rates for a given lab."""
    if not lab_name:
        return "Please specify a lab name, e.g., /scores lab-04"

    try:
        data = LmsApiClient.get_pass_rates(lab_name)
        if not data:
            return f"No scores found for {lab_name}. Check that the lab slug is correct (e.g., lab-01, lab-04)."

        # Format lab display name from slug: lab-04 -> Lab 04
        lab_display = lab_name.replace("lab-", "Lab ").replace("lab", "Lab")

        lines = [f"Pass rates for {lab_display}:"]
        for task in data:
            name = task.get("task") or task.get("title") or task.get("name", "Unknown")
            rate = task.get("pass_rate", task.get("average", 0))
            attempts = task.get("attempts", task.get("total", 0))
            lines.append(f"- {name}: {rate:.1f}% ({attempts} attempts)")
        return "\n".join(lines)
    except requests.ConnectionError as e:
        return f"Backend error: {e}. Check that the services are running."
    except requests.HTTPError as e:
        return f"Backend error: HTTP {e.response.status_code} {e.response.reason}. The backend service may be down."
    except Exception as e:
        return f"Backend error: {e}"
