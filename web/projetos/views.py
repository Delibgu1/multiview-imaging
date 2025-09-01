# multiview/multiview_imaging/web/projetos/views.py
import os
import mimetypes
from uuid import uuid4

import boto3
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_GET
from django.views.generic import ListView, CreateView, DetailView, UpdateView

from .forms import ProjetoForm
from .models import Projeto

# --- Desativa catálogo por padrão para evitar crashes por GDAL/PostGIS ---
Dataset = None


# ---------- Listagem (CBV) ----------
class ProjetoListView(LoginRequiredMixin, ListView):
    login_url = "login"
    model = Projeto
    template_name = "projetos/list.html"
    context_object_name = "projetos"
    paginate_by = 20

    def get_queryset(self):
        return Projeto.objects.filter(owner=self.request.user).order_by("-criado_em")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["uploads_antigos"] = []
        return ctx


# ---------- Create (Configurações/Definições) ----------
class ProjetoCreateView(LoginRequiredMixin, CreateView):
    """
    Página de Configurações/Definições do Projeto (antes do upload).
    Ao salvar, define status AGUARDANDO_UPLOAD e redireciona para /projetos/<id>/upload/
    """
    login_url = "login"
    model = Projeto
    form_class = ProjetoForm
    template_name = "projetos/definicoes_form.html"
    # Mantemos por consistência; não será usado pq sobrescrevemos form_valid
    success_url = reverse_lazy("projetos:index")

    def form_valid(self, form):
        projeto = form.save(commit=False)
        projeto.owner = self.request.user
        projeto.status = Projeto.Status.AGUARDANDO_UPLOAD
        projeto.save()
        form.save_m2m()
        messages.success(self.request, "Projeto criado. Prossiga com o upload das imagens.")
        # Redireciona pelo nome da rota (alinhado com seu urls.py)
        return redirect("projetos:upload", pk=projeto.pk)


# ---------- Detail (CBV) ----------
class ProjetoDetailView(LoginRequiredMixin, DetailView):
    login_url = "login"
    model = Projeto
    template_name = "projetos/detail.html"

    def get_queryset(self):
        return Projeto.objects.filter(owner=self.request.user)


class ProjetoUpdateView(LoginRequiredMixin, UpdateView):
    login_url = "login"
    model = Projeto
    form_class = ProjetoForm
    template_name = "projetos/definicoes_form.html"
    success_url = reverse_lazy("projetos:index")


# ---------- CSV GCP (modelo) ----------
GCP_CSV_EXEMPLO = (
    "label,x,y,z,lon,lat,alt,pixel_x,pixel_y\n"
    "GCP01,123456.789,7654321.123,245.67,-47.123456,-15.123456,245.67,5321,4123\n"
    "GCP02,123466.111,7654331.555,246.02,-47.123999,-15.123999,246.02,1388,2230\n"
)

@login_required
def gcp_modelo_csv(_request):
    resp = HttpResponse(GCP_CSV_EXEMPLO, content_type="text/csv; charset=utf-8")
    resp["Content-Disposition"] = 'attachment; filename="gcp_modelo.csv"'
    return resp


# ---------- Upload (página) ----------
@login_required
def upload(request, pk):
    projeto = get_object_or_404(Projeto, pk=pk, owner=request.user)
    context = {
        "projeto": projeto,
        "s3_bucket": os.getenv("S3_BUCKET", ""),
    }
    return render(request, "projetos/upload.html", context)


# ---------- Presign para S3/MinIO ----------
def _s3_client():
    return boto3.client(
        "s3",
        endpoint_url=os.getenv("S3_ENDPOINT_URL") or None,
        aws_access_key_id=os.getenv("S3_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("S3_SECRET_ACCESS_KEY"),
        region_name=os.getenv("S3_REGION_NAME") or None,
    )


@login_required
@require_GET
def upload_presign(request, pk):
    projeto = get_object_or_404(Projeto, pk=pk, owner=request.user)
    filename = request.GET.get("filename")
    if not filename:
        raise Http404("filename é obrigatório")

    content_type = (
        request.GET.get("content_type")
        or mimetypes.guess_type(filename)[0]
        or "application/octet-stream"
    )

    bucket = os.getenv("S3_BUCKET")
    if not bucket:
        return JsonResponse({"error": "S3_BUCKET não configurado"}, status=500)

    key = f"{request.user.id}/projetos/{projeto.pk}/raw/{uuid4().hex}/{filename}"
    s3 = _s3_client()
    MAX_SIZE = 2 * 1024 * 1024 * 1024  # 2GB

    presigned = s3.generate_presigned_post(
        Bucket=bucket,
        Key=key,
        Fields={"Content-Type": content_type},
        Conditions=[
            {"Content-Type": content_type},
            ["content-length-range", 0, MAX_SIZE],
        ],
        ExpiresIn=3600,
    )

    try:
        download_url = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket, "Key": key},
            ExpiresIn=3600,
        )
    except Exception:
        download_url = None

    return JsonResponse(
        {
            "url": presigned["url"],
            "fields": presigned["fields"],
            "key": key,
            "download_url": download_url,
        }
    )


# ---------- Stubs para ações de associação/remoção ----------
@login_required
def upload_associar(request, pk):
    return JsonResponse({"status": "ok", "action": "associar", "pk": pk})


@login_required
def upload_remover(request, pk):
    return JsonResponse({"status": "ok", "action": "remover", "pk": pk})
