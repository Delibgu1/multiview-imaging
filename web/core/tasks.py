from celery import shared_task

@shared_task(queue='photogrammetry')
def run_odm_job(job_id: int):
    # TODO: carregar o Job, criar projeto no ClusterODM, anexar imagens e acompanhar status
    return {"job_id": job_id, "status": "queued"}
