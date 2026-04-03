from fastapi import APIRouter, BackgroundTasks
from ragy_api.models import (
    HealthResponse,
    EmbeddingInfoResponse,
    SchedulerJobsResponse,
    TriggerRequest,
    MessageResponse,
    EmbedRequest,
    EmbedResponse,
    JobInfo
)
from ragy_api.dependencies import get_db_client, get_embedding_model
from conn_emb_hugging_face.client import get_embedding


router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    try:
        db_client = get_db_client()
        db_client.heartbeat()
        db_status = "ok"
    except:
        db_status = "error"

    try:
        model, model_name = get_embedding_model()
        emb_status = "ok"
    except:
        emb_status = "error"

    from ragy_api.scheduler import scheduler
    scheduler_status = "running" if scheduler and scheduler.running else "stopped"

    overall_status = "healthy" if all([
        db_status == "ok",
        emb_status == "ok"
    ]) else "degraded"

    return {
        "status": overall_status,
        "database": db_status,
        "embedding_model": emb_status,
        "scheduler": scheduler_status
    }


@router.get("/embedding/info", response_model=EmbeddingInfoResponse)
async def get_embedding_info():
    model, model_name = get_embedding_model()
    return {
        "model": model_name,
        "dimensions": model.get_sentence_embedding_dimension(),
        "max_seq_length": model.max_seq_length,
        "context_window": "~256 tokens (~190-200 words)"
    }


@router.post("/embedding/encode", response_model=EmbedResponse)
async def encode_text(request: EmbedRequest):
    embedding = get_embedding(request.text)
    return {
        "embedding": embedding,
        "dimensions": len(embedding)
    }


@router.get("/scheduler/jobs", response_model=SchedulerJobsResponse)
async def get_scheduler_jobs():
    from ragy_api.scheduler import scheduler

    if not scheduler or not scheduler.running:
        return {"jobs": []}

    jobs = []
    for job in scheduler.get_jobs():
        jobs.append(JobInfo(
            id=job.id,
            name=job.name,
            next_run=str(job.next_run_time) if job.next_run_time else None
        ))

    return {"jobs": jobs}


@router.post("/scheduler/trigger", response_model=MessageResponse)
async def trigger_scheduler_update(request: TriggerRequest, background_tasks: BackgroundTasks):
    from ragy_api.scheduler import trigger_manual_update

    background_tasks.add_task(trigger_manual_update, request.collection_name)
    return {"message": f"Update triggered for collection '{request.collection_name}'"}
