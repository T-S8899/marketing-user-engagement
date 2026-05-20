from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen


TERMINAL_STATUSES = {"SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"}


class ApifyClientError(RuntimeError):
    """Raised when an Apify API request fails."""


@dataclass(frozen=True)
class ApifyRun:
    id: str
    status: str
    dataset_id: str
    raw: dict[str, Any]


class ApifyClient:
    def __init__(self, token: str, base_url: str = "https://api.apify.com/v2") -> None:
        self.token = token
        self.base_url = base_url.rstrip("/")

    def start_run(self, actor_id: str, actor_input: dict[str, Any]) -> ApifyRun:
        actor_ref = quote(actor_id, safe="")
        payload = self._request(
            "POST",
            f"/acts/{actor_ref}/runs",
            query={"token": self.token},
            body=actor_input,
        )
        return self._parse_run(payload)

    def get_run(self, run_id: str) -> ApifyRun:
        payload = self._request("GET", f"/actor-runs/{quote(run_id, safe='')}", query={"token": self.token})
        return self._parse_run(payload)

    def wait_for_run(self, run_id: str, poll_seconds: int = 5, timeout_seconds: int = 600) -> ApifyRun:
        deadline = time.monotonic() + timeout_seconds
        while True:
            run = self.get_run(run_id)
            if run.status in TERMINAL_STATUSES:
                return run
            if time.monotonic() >= deadline:
                raise ApifyClientError(f"Timed out waiting for Apify run {run_id}. Last status: {run.status}")
            time.sleep(poll_seconds)

    def fetch_dataset_items(self, dataset_id: str) -> list[dict[str, Any]]:
        payload = self._request(
            "GET",
            f"/datasets/{quote(dataset_id, safe='')}/items",
            query={"token": self.token, "clean": "true", "format": "json"},
            expect_wrapped_data=False,
        )
        if not isinstance(payload, list):
            raise ApifyClientError(f"Dataset {dataset_id} did not return a JSON list.")
        return [item for item in payload if isinstance(item, dict)]

    def _request(
        self,
        method: str,
        path: str,
        query: dict[str, Any] | None = None,
        body: dict[str, Any] | None = None,
        expect_wrapped_data: bool = True,
    ) -> Any:
        query_string = f"?{urlencode(query or {})}" if query else ""
        url = f"{self.base_url}{path}{query_string}"
        data = json.dumps(body or {}).encode("utf-8") if body is not None else None
        request = Request(url, data=data, method=method, headers={"Content-Type": "application/json"})
        try:
            with urlopen(request, timeout=60) as response:
                response_payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            details = exc.read().decode("utf-8", errors="replace")
            raise ApifyClientError(f"Apify HTTP {exc.code}: {details}") from exc
        except URLError as exc:
            raise ApifyClientError(f"Apify network error: {exc.reason}") from exc

        if expect_wrapped_data:
            data_payload = response_payload.get("data") if isinstance(response_payload, dict) else None
            if not isinstance(data_payload, dict):
                raise ApifyClientError(f"Unexpected Apify response shape for {path}.")
            return data_payload
        return response_payload

    @staticmethod
    def _parse_run(payload: dict[str, Any]) -> ApifyRun:
        run_id = str(payload.get("id", "")).strip()
        if not run_id:
            raise ApifyClientError("Apify run response did not include an id.")
        return ApifyRun(
            id=run_id,
            status=str(payload.get("status", "")).strip(),
            dataset_id=str(payload.get("defaultDatasetId", "")).strip(),
            raw=payload,
        )
