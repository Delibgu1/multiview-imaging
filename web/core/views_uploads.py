import os
import uuid
import mimetypes
import boto3
from django.conf import settings
from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt   # <-- já estava? garanta que está
from botocore.config import Config

def _s3_client():
    return boto3.client(
        "s3",
        endpoint_url=settings.S3_ENDPOINT_URL,  # ex.: http://minio:9000 (REDE DO DOCKER)
        aws_access_key_id=settings.S3_ACCESS_KEY,
        aws_secret_access_key=settings.S3_SECRET_KEY,
        region_name=getattr(settings, "S3_REGION", "us-east-1"),
        config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
    )

def _browser_endpoint() -> str:
    be = os.getenv("S3_BROWSER_ENDPOINT") or ""
    if be:
        return be.rstrip("/")
    legacy = os.getenv("S3_PUBLIC_URL", "").rstrip("/")
    if legacy:
        return legacy
    return settings.S3["endpoint"].replace("minio:9000", "localhost:9000").rstrip("/")

def _guess_content_type(filename: str) -> str:
    ctype = mimetypes.guess_type(filename)[0]
    return ctype or "application/octet-stream"

def _build_key(filename: str) -> str:
    return f"uploads/{uuid.uuid4().hex}_{filename}"

@csrf_exempt
def presign(request: HttpRequest):
    # 1) nome do arquivo e tipo
    filename = request.GET.get("filename") or f"upload-{uuid.uuid4().hex}"
    content_type = _guess_content_type(filename)

    # 2) key precisa respeitar um prefixo conhecido p/ "starts-with"
    key = _build_key(filename)  # ex.: uploads/<uuid>_<filename>
    prefix = "uploads/"

    # 3) client S3 (MinIO)
    s3 = _s3_client()
    bucket = settings.S3["bucket"]

    # 4) NÃO fixe Content-Type exato; aceite qualquer (evita 403 por mismatch).
    #    NÃO use ACL aqui (MinIO recente normalmente não aceita ACL).
    conditions = [
        ["starts-with", "$key", prefix],
        ["starts-with", "$Content-Type", ""],
    ]
    fields = {
        "success_action_status": "201",  # opcional: retorna 201 no upload ok
    }

    presigned = s3.generate_presigned_post(
        Bucket=bucket,
        Key=key,
        Fields=fields,
        Conditions=conditions,
        ExpiresIn=3600,
    )

    # 5) A URL do POST tem que ser a do navegador (localhost), não "minio:9000"
    browser_ep = _browser_endpoint().rstrip("/")
    presigned["url"] = f"{browser_ep}/{bucket}"

    # 6) Retorno enxuto p/ o front
    return JsonResponse({
        "url": presigned["url"],
        "fields": presigned["fields"],
        "key": key,
        "content_type_hint": content_type,
        "debug": {
            "bucket": bucket,
            "endpoint_url_backend": settings.S3_ENDPOINT_URL,
            "browser_endpoint": _browser_endpoint(),
            "access_key_used": settings.S3_ACCESS_KEY,
        },
    })
