import requests
from services.lms_api import LmsApiClient


def health() -> str:
    """Check backend availability by calling GET /items/."""
    try:
        items = LmsApiClient.get_items()
        return f"Backend is healthy. {len(items)} items available."
    except requests.ConnectionError as e:
        return f"Backend error: {e}. Check that the services are running."
    except requests.HTTPError as e:
        return f"Backend error: HTTP {e.response.status_code} {e.response.reason}. The backend service may be down."
    except Exception as e:
        return f"Backend error: {e}"
