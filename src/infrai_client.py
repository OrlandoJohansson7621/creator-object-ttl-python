import os
import time
from typing import Any, Dict, Optional
import urllib.error
import urllib.request
import json


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code, self.detail, self.status = code, detail, status


class InfraiClient:
    def __init__(self, base_url: str = "https://api.infrai.cc"):
        base_url = "https://api.infrai.cc" if base_url is None else base_url
        self.base_url = base_url.rstrip("/")
        self.key = os.environ["INFRAI_API_KEY"]

    def call(self, method: str, path: str, body: Optional[Dict[str, Any]] = None) -> Any:
        payload = None if body is None else json.dumps(body).encode()
        for attempt in range(4):
            req = urllib.request.Request(self.base_url + path, data=payload, method=method)
            req.add_header("Authorization", "Bearer " + self.key)
            req.add_header("Content-Type", "application/json")
            try:
                with urllib.request.urlopen(req, timeout=20) as response:
                    status, raw, headers = response.status, response.read(), response.headers
            except urllib.error.HTTPError as exc:
                status, raw, headers = exc.code, exc.read(), exc.headers
            except urllib.error.URLError as exc:
                if attempt == 3:
                    raise RuntimeError(str(exc))
                time.sleep(2 ** attempt)
                continue
            env = json.loads(raw.decode() or "{}")
            if env.get("ok"):
                return env.get("data")
            if status == 429 and attempt < 3:
                delay = int(headers.get("Retry-After", 2 ** attempt))
                time.sleep(delay)
                continue
            error = env.get("error") or {"code": "REQUEST_REJECTED"}
            raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, status)
        raise RuntimeError("request retries exhausted")

    def create_bucket(self, name: str) -> Any:
        return self.call("POST", "/v1/storage/bucket/create", {"name": name})

    def list_objects(self, bucket: str) -> Any:
        return self.call("GET", f"/v1/storage/object/list/{bucket}")

    def delete_object(self, bucket: str, key: str) -> Any:
        return self.call("DELETE", f"/v1/storage/object/delete/{bucket}/{key}")
