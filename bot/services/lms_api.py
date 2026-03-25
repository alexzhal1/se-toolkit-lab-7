"""Client for the LMS backend API."""

import requests
from config import Config


class LmsApiClient:
    """Thin wrapper around the LMS REST API."""

    @staticmethod
    def _headers() -> dict:
        return {"Authorization": f"Bearer {Config.LMS_API_KEY}"}

    @staticmethod
    def _base_url() -> str:
        return (Config.LMS_API_URL or "http://localhost:42002").rstrip("/")

    @classmethod
    def get_items(cls) -> list[dict]:
        """GET /items/ — returns labs and tasks."""
        resp = requests.get(f"{cls._base_url()}/items/", headers=cls._headers(), timeout=10)
        resp.raise_for_status()
        return resp.json()

    @classmethod
    def get_pass_rates(cls, lab: str) -> list[dict]:
        """GET /analytics/pass-rates?lab=<lab> — per-task pass rates."""
        resp = requests.get(
            f"{cls._base_url()}/analytics/pass-rates",
            params={"lab": lab},
            headers=cls._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()
