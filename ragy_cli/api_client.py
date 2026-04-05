import requests
from typing import Generator
import json
from ragy_api.config import settings


class APIClient:
    def __init__(self, base_url: str | None = None):
        if base_url is None:
            base_url = f"http://localhost:{settings.API_PORT}"
        self.base_url = base_url
        self.api_prefix = "/api/v1"

    def search_web(self, query: str) -> dict:
        response = requests.post(
            f"{self.base_url}{self.api_prefix}/search/web",
            json={"query": query}
        )
        response.raise_for_status()
        return response.json()

    def extract_data(self, query: str, collection: str, top_k: int = 10) -> Generator:
        with requests.post(
            f"{self.base_url}{self.api_prefix}/extract/data",
            json={"query": query, "collection_name": collection, "top_k": top_k},
            stream=True
        ) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if line and line.startswith(b"data: "):
                    data = json.loads(line[6:])
                    yield data

    def create_index(self, query: str, collection: str,
                    save_full_data: bool = True, num_days: int = 365) -> Generator:
        with requests.post(
            f"{self.base_url}{self.api_prefix}/index/create",
            json={
                "query": query,
                "collection_name": collection,
                "save_full_data": save_full_data,
                "num_days": num_days
            },
            stream=True
        ) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if line and line.startswith(b"data: "):
                    data = json.loads(line[6:])
                    yield data

    def list_collections(self) -> list[str]:
        response = requests.get(f"{self.base_url}{self.api_prefix}/extract/collections")
        response.raise_for_status()
        return response.json()["collections"]

    def get_database_content(self) -> dict:
        response = requests.get(f"{self.base_url}{self.api_prefix}/database/content")
        response.raise_for_status()
        return response.json()

    def get_collection(self, name: str) -> dict:
        response = requests.get(f"{self.base_url}{self.api_prefix}/database/collection/{name}")
        response.raise_for_status()
        return response.json()

    def delete_collection(self, name: str) -> dict:
        response = requests.delete(f"{self.base_url}{self.api_prefix}/database/collection/{name}")
        response.raise_for_status()
        return response.json()

    def get_index_status(self, collection: str) -> dict:
        response = requests.get(f"{self.base_url}{self.api_prefix}/index/status/{collection}")
        response.raise_for_status()
        return response.json()

    def health_check(self) -> dict:
        response = requests.get(f"{self.base_url}{self.api_prefix}/system/health")
        response.raise_for_status()
        return response.json()

    def get_embedding_info(self) -> dict:
        response = requests.get(f"{self.base_url}{self.api_prefix}/system/embedding/info")
        response.raise_for_status()
        return response.json()

    def get_scheduler_jobs(self) -> dict:
        response = requests.get(f"{self.base_url}{self.api_prefix}/system/scheduler/jobs")
        response.raise_for_status()
        return response.json()

    def get_database_stats(self) -> dict:
        response = requests.get(f"{self.base_url}{self.api_prefix}/database/stats")
        response.raise_for_status()
        return response.json()
