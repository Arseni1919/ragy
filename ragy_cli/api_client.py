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

    def search_yfinance(self, query: str, max_results: int = 5) -> dict:
        response = requests.post(
            f"{self.base_url}{self.api_prefix}/search/yfinance",
            json={"query": query, "max_results": max_results}
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
                    num_days: int = 365) -> Generator:
        with requests.post(
            f"{self.base_url}{self.api_prefix}/index/create",
            json={
                "query": query,
                "collection_name": collection,
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

    def get_collection_distribution(self, name: str) -> dict:
        response = requests.get(f"{self.base_url}{self.api_prefix}/database/collection/{name}/distribution")
        response.raise_for_status()
        return response.json()

    def get_sample_document(self, collection_name: str, index: int) -> dict:
        response = requests.get(f"{self.base_url}{self.api_prefix}/database/collection/{collection_name}/sample/{index}")
        response.raise_for_status()
        return response.json()

    def get_head_documents(self, collection_name: str, limit: int = 5) -> dict:
        response = requests.get(f"{self.base_url}{self.api_prefix}/database/collection/{collection_name}/head", params={"limit": limit})
        response.raise_for_status()
        return response.json()

    def get_tail_documents(self, collection_name: str, limit: int = 5) -> dict:
        response = requests.get(f"{self.base_url}{self.api_prefix}/database/collection/{collection_name}/tail", params={"limit": limit})
        response.raise_for_status()
        return response.json()

    def create_scheduled_job(self, query: str, collection: str, interval_type: str, interval_amount: int, source: str = "tavily") -> dict:
        response = requests.post(
            f"{self.base_url}{self.api_prefix}/system/scheduler/jobs/create",
            json={
                "query": query,
                "collection_name": collection,
                "interval_type": interval_type,
                "interval_amount": interval_amount,
                "source": source
            }
        )
        response.raise_for_status()
        return response.json()

    def get_user_jobs(self) -> dict:
        response = requests.get(f"{self.base_url}{self.api_prefix}/system/scheduler/jobs/user")
        response.raise_for_status()
        return response.json()

    def delete_scheduled_job(self, job_id: int) -> dict:
        response = requests.delete(f"{self.base_url}{self.api_prefix}/system/scheduler/jobs/delete/{job_id}")
        response.raise_for_status()
        return response.json()
    def extract_all_for_xray(self, query: str, collection: str) -> dict:
        """Get all documents with scores for xray visualization"""
        response = requests.post(
            f"{self.base_url}{self.api_prefix}/extract/all",
            json={"query": query, "collection_name": collection, "top_k": 10}
        )
        response.raise_for_status()
        return response.json()

    def upload_csv(self, file_path: str, collection_name: str) -> dict:
        with open(file_path, 'rb') as f:
            files = {'file': (file_path, f, 'text/csv')}
            data = {'collection_name': collection_name}
            response = requests.post(
                f"{self.base_url}{self.api_prefix}/upload/csv",
                files=files,
                data=data
            )
            response.raise_for_status()
            return response.json()
