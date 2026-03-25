import requests
from services.lms_api import LmsApiClient


def labs() -> str:
    """List all labs from the backend."""
    try:
        items = LmsApiClient.get_items()
        lab_items = [item for item in items if item.get("type") == "lab"]
        if not lab_items:
            return "No labs found."
        lines = ["Available labs:"]
        for lab in lab_items:
            title = lab.get("title", lab.get("slug", "Unknown"))
            lines.append(f"- {title}")
        return "\n".join(lines)
    except requests.ConnectionError as e:
        return f"Backend error: {e}. Check that the services are running."
    except requests.HTTPError as e:
        return f"Backend error: HTTP {e.response.status_code} {e.response.reason}. The backend service may be down."
    except Exception as e:
        return f"Backend error: {e}"
