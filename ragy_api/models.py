from pydantic import BaseModel, Field
from typing import Optional


class WebSearchRequest(BaseModel):
    query: str = Field(..., description="Search query")


class SearchResult(BaseModel):
    title: str
    url: str
    raw_content: str


class WebSearchResponse(BaseModel):
    query: str
    results: list[SearchResult]


class ExtractRequest(BaseModel):
    query: str = Field(..., description="Extraction query")
    collection_name: str = Field(..., description="Collection to search")
    top_k: int = Field(10, description="Number of results")


class CollectionsResponse(BaseModel):
    collections: list[str]


class IndexCreateRequest(BaseModel):
    query: str = Field(..., description="Search query for index")
    collection_name: str = Field(..., description="Collection name")
    num_days: int = Field(365, description="Number of days to index")


class IndexStatusResponse(BaseModel):
    collection_name: str
    exists: bool
    total_docs: int


class CollectionInfo(BaseModel):
    name: str
    count: int
    sample_data: list[dict]


class DatabaseContentResponse(BaseModel):
    collections: list[CollectionInfo]


class CollectionDetailResponse(BaseModel):
    name: str
    count: int
    sample_data: list[dict]


class MessageResponse(BaseModel):
    message: str


class HealthResponse(BaseModel):
    status: str
    database: str
    embedding_model: str
    scheduler: str


class EmbeddingInfoResponse(BaseModel):
    model: str
    dimensions: int
    max_seq_length: int
    context_window: str


class EmbedRequest(BaseModel):
    text: str = Field(..., description="Text to embed")


class EmbedResponse(BaseModel):
    embedding: list[float]
    dimensions: int


class JobInfo(BaseModel):
    id: str
    name: str
    next_run: Optional[str]


class SchedulerJobsResponse(BaseModel):
    jobs: list[JobInfo]


class TriggerRequest(BaseModel):
    collection_name: str = Field(..., description="Collection to update")


class ProgressUpdate(BaseModel):
    status: str
    progress: float
    message: str


class JobCreateRequest(BaseModel):
    query: str = Field(..., description="Search query")
    collection_name: str = Field(..., description="Target collection")
    interval_type: str = Field(..., description="minute, hour, day, week, month, year")
    interval_amount: int = Field(..., description="Interval amount (e.g., 5)")


class JobCreateResponse(BaseModel):
    job_id: int
    apscheduler_job_id: str
    query: str
    collection_name: str
    interval_type: str
    interval_amount: int
    message: str


class UserJobInfo(BaseModel):
    job_id: int
    apscheduler_job_id: str
    query: str
    collection_name: str
    interval_type: str
    interval_amount: int
    next_run: Optional[str]
    run_count: int
    error_count: int
    last_success: Optional[str]


class UserJobsResponse(BaseModel):
    jobs: list[UserJobInfo]
