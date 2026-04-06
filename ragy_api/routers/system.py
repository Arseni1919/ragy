from fastapi import APIRouter, BackgroundTasks, HTTPException
from ragy_api.models import (
    HealthResponse,
    EmbeddingInfoResponse,
    SchedulerJobsResponse,
    TriggerRequest,
    MessageResponse,
    EmbedRequest,
    EmbedResponse,
    JobInfo,
    JobCreateRequest,
    JobCreateResponse,
    UserJobInfo,
    UserJobsResponse
)
from ragy_api.dependencies import get_db_client, get_embedding_model
from conn_emb_hugging_face.client import get_query_embedding, get_document_embedding


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
        "context_window": "~512 tokens"
    }


@router.post("/embedding/encode", response_model=EmbedResponse)
async def encode_text(request: EmbedRequest):
    embedding = get_document_embedding(request.text)
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


@router.post("/scheduler/jobs/create", response_model=JobCreateResponse)
async def create_scheduled_job(request: JobCreateRequest):
    from ragy_api.scheduler import create_user_job

    valid_intervals = ['minute', 'hour', 'day', 'week', 'month', 'year']
    if request.interval_type not in valid_intervals:
        raise HTTPException(status_code=400, detail=f"Invalid interval type. Must be one of: {valid_intervals}")

    if request.interval_amount < 1:
        raise HTTPException(status_code=400, detail="Interval amount must be at least 1")

    result = create_user_job(
        query=request.query,
        collection_name=request.collection_name,
        interval_type=request.interval_type,
        interval_amount=request.interval_amount,
        source=request.source
    )

    interval_desc = f"every {request.interval_amount} {request.interval_type}{'s' if request.interval_amount > 1 else ''}"
    result['message'] = f"Job created: will run {interval_desc}"

    return result


@router.get("/scheduler/jobs/user", response_model=UserJobsResponse)
async def get_user_jobs():
    from ragy_api.scheduler import scheduler, job_metadata_store

    metadata_jobs = job_metadata_store.list_jobs()
    jobs = []

    for meta in metadata_jobs:
        apscheduler_job = scheduler.get_job(meta['apscheduler_job_id'])
        next_run = str(apscheduler_job.next_run_time) if apscheduler_job and apscheduler_job.next_run_time else None

        jobs.append(UserJobInfo(
            job_id=meta['id'],
            apscheduler_job_id=meta['apscheduler_job_id'],
            query=meta['query'],
            collection_name=meta['collection_name'],
            interval_type=meta['interval_type'],
            interval_amount=meta['interval_amount'],
            source=meta['source'],
            next_run=next_run,
            run_count=meta['run_count'],
            error_count=meta['error_count'],
            last_success=meta['last_success']
        ))

    return {"jobs": jobs}


@router.delete("/scheduler/jobs/delete/{job_id}", response_model=MessageResponse)
async def delete_scheduled_job(job_id: int):
    from ragy_api.scheduler import delete_user_job

    try:
        delete_user_job(job_id)
        return {"message": f"Job {job_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
