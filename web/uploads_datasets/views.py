
# uploads_datasets/views.py
import json
from datetime import datetime

from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.utils.text import slugify
from django.views.decorators.csrf import csrf_exempt

from .s3_utils import presign_post


def upload_page(request):
    """
    Renderiza a página de upload com informações básicas (bucket e base pública).
    Fallbacks: AWS_*, depois S3_*, depois settings.S3 (se existir).
    """
    bucket = (
        getattr(settings, "AWS_STORAGE_BUCKET_NAME", None)
        or getattr(settings, "S3_BUCKET", None)
        or (getattr(settings, "S3", {}).get("bucket") if hasattr(settings, "S3") else None)
    )

    public_url_base = (
        getattr(settings, "S3_BROWSER_ENDPOINT", None)
        or getattr(settings, "S3_PUBLIC_URL", None)
        or (getattr(settings, "S3", {}).get("public_url") if hasattr(settings, "S3") else None)
    )

    return render(
        request,
        "uploads_datasets/upload.html",
        {"bucket": bucket, "public_url_base": public_url_base},
    )


@csrf_exempt
def presign(request):
    """
    Retorna URL e fields para upload direto ao S3/MinIO.
    Body: { filename, content_type }
    """
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")

    try:
        data = json.loads(request.body.decode("utf-8"))
        filename = data.get("filename") or ""
        content_type = data.get("content_type") or "application/octet-stream"
    except Exception:
        filename = request.POST.get("filename", "")
        content_type = request.POST.get("content_type", "application/octet-stream")

    if not filename:
        return HttpResponseBadRequest("filename obrigatório")

    # Gere keys começando com 'uploads/' para bater com a policy do presign_post()
    name_slug = slugify(filename.rsplit(".", 1)[0])[:80] or "arquivo"
    ext = ("." + filename.rsplit(".", 1)[1]) if "." in filename else ""
    now = datetime.utcnow()
    key = f"uploads/{now:%Y/%m}/{now:%d_%H%M%S}_{name_slug}{ext}"

    signed = presign_post(key, content_type)

    # Formato esperado pelo frontend: { key, presigned: { url, fields } }
    return JsonResponse({"key": key, "presigned": signed})


@csrf_exempt
def complete(request):
    """
    Após upload no S3/MinIO, cria o Dataset e agenda um Job de processamento.
    Body: { "key": "", "filename": "", "size": <int> }
    """
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        return HttpResponseBadRequest("json inválido")

    key = payload.get("key")
    filename = payload.get("filename")
    size = payload.get("size")

    if not key or not filename:
        return HttpResponseBadRequest("key e filename obrigatórios")

    # Importa aqui para evitar problemas de import quando apenas testando upload
    from catalogo.models import Dataset, Job

    ds = Dataset.objects.create(
        nome=filename,
        descricao="Upload via web",
        s3_key=key,
        tamanho_b=size or None,
        status="new",
    )
    Job.objects.create(dataset=ds, tipo="cog", status="queued")

    return JsonResponse({"ok": True, "dataset_id": ds.id})
