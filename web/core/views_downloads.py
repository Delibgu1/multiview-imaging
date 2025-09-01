# core/views_downloads.py
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from django.conf import settings
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
from catalogo.models import Dataset

def _s3():
    return boto3.client(
        "s3",
        endpoint_url=settings.S3_ENDPOINT_URL,
        aws_access_key_id=settings.S3_ACCESS_KEY,
        aws_secret_access_key=settings.S3_SECRET_KEY,
        region_name=getattr(settings, "S3_REGION", "us-east-1"),
        config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
    )

@require_GET
@login_required
def presign_download(request):
    key = request.GET.get("key")
    if not key:
        return HttpResponseBadRequest("key required")

    # (opcional) restringir a prefixos conhecidos do projeto
    allowed_prefixes = ("uploads/", "datasets/")
    if not key.startswith(allowed_prefixes):
        return HttpResponseForbidden("invalid key")

    # exigir que a key exista em um Dataset cadastrado
    if not Dataset.objects.filter(s3_key=key).exists():
        return HttpResponseForbidden("forbidden")

    try:
        url = _s3().generate_presigned_url(
            ClientMethod="get_object",
            Params={
                "Bucket": settings.S3_BUCKET,
                "Key": key,
                # força download com nome amigável
                "ResponseContentDisposition": f'attachment; filename="{key.split("/")[-1]}"',
            },
            ExpiresIn=3600,  # 1 hora
        )
    except ClientError as e:
        return JsonResponse({"error": "presign_failed", "detail": str(e)}, status=400)

    return JsonResponse({"url": url})
