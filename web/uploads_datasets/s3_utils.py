
# uploads_datasets/s3_utils.py
import os
import boto3
from botocore.config import Config
from django.conf import settings


def _get_setting(attr_name, env_name=None, default=None):
    """
    PRIORIDADE: 1) variável de ambiente  2) settings.<attr_name>  3) default
    """
    # 1) ENV primeiro
    val = os.getenv(env_name or attr_name)
    if val:
        return val
    # 2) settings depois
    if hasattr(settings, attr_name):
        return getattr(settings, attr_name)
    # 3) default
    return default



def s3_client():
    # Defaults seguros para seu ambiente local
    endpoint = _get_setting("S3_ENDPOINT_URL", "S3_ENDPOINT_URL", "http://127.0.0.1:9000")
    access   = _get_setting("S3_ACCESS_KEY", "S3_ACCESS_KEY", "multiview")
    secret   = _get_setting("S3_SECRET_KEY", "S3_SECRET_KEY", "senha_123")
    region   = _get_setting("S3_REGION", "S3_REGION", "us-east-1")

    return boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=access,
        aws_secret_access_key=secret,
        region_name=region,
        config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
    )


def presign_post(key: str, content_type: str):
    """
    Presign para MinIO/S3:
      - sem ACL
      - Content-Type com starts-with
      - URL de POST para o navegador (S3_BROWSER_ENDPOINT + /<bucket>)
    """
    bucket = getattr(settings, "S3_BUCKET", "multiview-data")

    conditions = [
        ["starts-with", "$key", "uploads/"],
        ["starts-with", "$Content-Type", ""],
        ["content-length-range", 0, 1073741824],  # até 1 GiB (ajuste se quiser)
        {"bucket": getattr(settings, "S3_BUCKET", "multiview-data")},
    ]
    fields = {
        # vazio de propósito (vamos só copiar o que o boto3 devolver)
    }

    client = s3_client()
    presigned = client.generate_presigned_post(
        Bucket=bucket,
        Key=key,
        Fields=fields,
        Conditions=conditions,
        ExpiresIn=3600,
    )

    browser_ep = _get_setting("S3_BROWSER_ENDPOINT", "S3_BROWSER_ENDPOINT", "http://127.0.0.1:9000").rstrip("/")
    presigned["url"] = f"{browser_ep}/{bucket}"

    # DEBUG: devolve também bucket/endpoint para conferirmos
    presigned["_debug_bucket"] = bucket
    presigned["_debug_browser_ep"] = browser_ep
    return presigned
