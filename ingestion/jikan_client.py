import hashlib
import json
import logging
import random
import time
from pathlib import Path
from typing import Any

import httpx

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("JikanClient")

class TokenBucket:
    def __init__(self, rate: float = 3.0, capacity: float = 3.0):
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.monotonic()

    def acquire(self):
        now = time.monotonic()
        delta = now - self.last_update
        self.tokens = min(self.capacity, self.tokens + delta * self.rate)
        self.last_update = now

        if self.tokens < 1.0:
            sleep_time = (1.0 - self.tokens) / self.rate
            time.sleep(sleep_time)
            self.tokens = 0.0
            self.last_update = time.monotonic()
        else:
            self.tokens -= 1.0

class JikanClient:
    def __init__(self, base_url: str = "https://api.jikan.moe/v4", cache_dir: str = ".cache/jikan", rate_limit_rps: float = 3.0):
        self.base_url = base_url.rstrip("/")
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.rate_limiter = TokenBucket(rate=rate_limit_rps, capacity=rate_limit_rps)
        self.client = httpx.Client(timeout=10.0, headers={"User-Agent": "AnimeAnalytics/1.0"})

    def _get_cache_key(self, endpoint: str, params: dict[str, Any] | None = None) -> Path:
        raw_key = f"{endpoint}:{json.dumps(params or {}, sort_keys=True)}"
        key_hash = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()
        return self.cache_dir / f"{key_hash}.json"

    def get(self, endpoint: str, params: dict[str, Any] | None = None, use_cache: bool = True, max_retries: int = 4) -> dict[str, Any] | None:
        endpoint = endpoint.lstrip("/")
        cache_file = self._get_cache_key(endpoint, params)

        if use_cache and cache_file.exists():
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    logger.debug(f"Cache hit for {endpoint}")
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to read cache for {endpoint}: {e}")

        url = f"{self.base_url}/{endpoint}"
        retries = 0

        while retries <= max_retries:
            self.rate_limiter.acquire()
            try:
                response = self.client.get(url, params=params)

                if response.status_code == 200:
                    data = response.json()
                    if use_cache:
                        with open(cache_file, "w", encoding="utf-8") as f:
                            json.dump(data, f, indent=2)
                    return data
                elif response.status_code == 404:
                    logger.warning(f"Resource not found (404): {url}")
                    return None
                elif response.status_code in (429, 500, 502, 503, 504):
                    retries += 1
                    backoff = (2 ** retries) + random.uniform(0.1, 0.5)
                    logger.warning(f"HTTP {response.status_code} for {url}. Retrying in {backoff:.2f}s (Attempt {retries}/{max_retries})")
                    time.sleep(backoff)
                else:
                    logger.error(f"Unexpected HTTP status {response.status_code} for {url}: {response.text}")
                    response.raise_for_status()

            except (httpx.RequestError, httpx.TimeoutException) as exc:
                retries += 1
                backoff = (2 ** retries) + random.uniform(0.1, 0.5)
                logger.warning(f"Network error {exc} for {url}. Retrying in {backoff:.2f}s (Attempt {retries}/{max_retries})")
                time.sleep(backoff)

        logger.error(f"Failed to fetch {url} after {max_retries} retries.")
        return None

    def get_anime_by_id(self, mal_id: int) -> dict[str, Any] | None:
        return self.get(f"anime/{mal_id}")

    def get_anime_search(self, query: str, page: int = 1, limit: int = 10) -> dict[str, Any] | None:
        return self.get("anime", params={"q": query, "page": page, "limit": limit})

    def close(self):
        self.client.close()

if __name__ == "__main__":
    client = JikanClient()
    logger.info("Testing Jikan API Client...")
    result = client.get_anime_by_id(1)  # Cowboy Bebop
    if result and "data" in result:
        logger.info(f"Success! Title: {result['data'].get('title')}")
    client.close()
