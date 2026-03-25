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
    def _get(cls, path: str, params: dict = None) -> dict | list:
        resp = requests.get(
            f"{cls._base_url()}{path}",
            params=params,
            headers=cls._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    @classmethod
    def _post(cls, path: str, json_body: dict = None) -> dict:
        resp = requests.post(
            f"{cls._base_url()}{path}",
            json=json_body or {},
            headers=cls._headers(),
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

    @classmethod
    def get_items(cls) -> list[dict]:
        """GET /items/ — labs and tasks."""
        return cls._get("/items/")

    @classmethod
    def get_learners(cls) -> list[dict]:
        """GET /learners/ — enrolled students."""
        return cls._get("/learners/")

    @classmethod
    def get_scores(cls, lab: str) -> dict:
        """GET /analytics/scores?lab= — score distribution."""
        return cls._get("/analytics/scores", {"lab": lab})

    @classmethod
    def get_pass_rates(cls, lab: str) -> list[dict]:
        """GET /analytics/pass-rates?lab= — per-task averages."""
        return cls._get("/analytics/pass-rates", {"lab": lab})

    @classmethod
    def get_timeline(cls, lab: str) -> dict:
        """GET /analytics/timeline?lab= — submissions per day."""
        return cls._get("/analytics/timeline", {"lab": lab})

    @classmethod
    def get_groups(cls, lab: str) -> list[dict]:
        """GET /analytics/groups?lab= — per-group performance."""
        return cls._get("/analytics/groups", {"lab": lab})

    @classmethod
    def get_top_learners(cls, lab: str, limit: int = 5) -> list[dict]:
        """GET /analytics/top-learners?lab=&limit= — top N learners."""
        return cls._get("/analytics/top-learners", {"lab": lab, "limit": limit})

    @classmethod
    def get_completion_rate(cls, lab: str) -> dict:
        """GET /analytics/completion-rate?lab= — completion percentage."""
        return cls._get("/analytics/completion-rate", {"lab": lab})

    @classmethod
    def trigger_sync(cls) -> dict:
        """POST /pipeline/sync — trigger ETL sync."""
        return cls._post("/pipeline/sync")
