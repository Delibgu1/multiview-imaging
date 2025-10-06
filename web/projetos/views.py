
# multiview/multiview_imaging/web/projetos/views.py
# multiview/multiview_imaging/web/projetos/views.py
from uuid import uuid4
import mimetypes
import os
import json

import boto3
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.views.decorators.http import require_GET
from django.views.generic import CreateView, DetailView, ListView, UpdateView, TemplateView

from .forms import ProjetoForm
from .models import Projeto


# ============================================================================
# Listagem
# ============================================================================
class ProjetoListView(LoginRequiredMixin, ListView):
    login_url = "core:login"
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


# ============================================================================
# Create (Definições/Configurações antes do upload)
# ============================================================================
class ProjetoCreateView(LoginRequiredMixin, CreateView):
    """
    Tela de Configurações/Definições do Projeto.
    Ao salvar, define status AGUARDANDO_UPLOAD e redireciona para /projetos/<id>/upload/
    """
    login_url = "core:login"
    model = Projeto
    form_class = ProjetoForm
    template_name = "projetos/definicoes_form.html"
    success_url = reverse_lazy("projetos:index")  # fallback

    def form_valid(self, form):
        projeto = form.save(commit=False)
        projeto.owner = self.request.user
        projeto.status = Projeto.Status.AGUARDANDO_UPLOAD
        projeto.save()
        form.save_m2m()
        obj = form.save(commit=False)
        cfg = obj.config or {}
        messages.success(self.request, "Projeto criado. Prossiga com o upload das imagens.")
        return redirect("projetos:upload", pk=projeto.pk)

        # Q1 e Q2 vêm como <input type="hidden" name="q1_json" / "q2_json">
        q1 = self.request.POST.get("q1_json", "")
        q2 = self.request.POST.get("q2_json", "")

        # Tenta converter para dict; se não der, guarda bruto
        try:
            cfg["q1"] = json.loads(q1) if q1 else {}
        except Exception:
            cfg["q1_raw"] = q1

        try:
            cfg["q2"] = json.loads(q2) if q2 else {}
        except Exception:
            cfg["q2_raw"] = q2

        # (opcional) espelhar algo em campos do modelo
        # ex.: EPSG padrão do Q1, se você quiser
        if cfg.get("q1", {}).get("crs_padrao"):
            obj.epsg = cfg["q1"]["crs_padrao"]

        obj.config = cfg
        obj.save()
        return super().form_valid(form)


# ============================================================================
# Detail / Update (mantidos simples; expandimos depois)
# ============================================================================
class ProjetoDetailView(LoginRequiredMixin, DetailView):
    login_url = "core:login"
    model = Projeto
    template_name = "projetos/detail.html"

    def get_queryset(self):
        return Projeto.objects.filter(owner=self.request.user)


class ProjetoUpdateView(LoginRequiredMixin, UpdateView):
    login_url = "core:login"
    model = Projeto
    form_class = ProjetoForm
    template_name = "projetos/definicoes_form.html"
    success_url = reverse_lazy("projetos:index")


# ============================================================================
# CSV GCP (modelo)
# ============================================================================
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


# ============================================================================
# Upload (página)
# ============================================================================
@login_required
def upload(request, pk):
    projeto = get_object_or_404(Projeto, pk=pk, owner=request.user)
    context = {
        "projeto": projeto,
        "s3_bucket": os.getenv("S3_BUCKET", ""),
    }
    return render(request, "projetos/upload.html", context)


# ============================================================================
# Presign para S3/MinIO
# ============================================================================
def _s3_client():
    return boto3.client(
        "s3",
        endpoint_url=os.getenv("S3_ENDPOINT_URL") or None,
        aws_access_key_id=os.getenv("S3_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("S3_SECRET_ACCESS_KEY"),
        region_name=os.getenv("S3_REGION_NAME") or None,
    )

# ============================================================================
# Chip - Card com nome do usuário e saldo
# ============================================================================

def objetivo_view(request):
    current_step = 1
    total_steps = 5
    progress_pct = int((current_step / total_steps) * 100)

    ctx = {
        "plano_nome": getattr(getattr(request.user, "profile", None), "plano_nome", "Básico"),
        "saldo_creditos": getattr(request.user, "saldo_creditos", "—"),
        "comprar_creditos_url": reverse("billing:comprar_creditos"),
        "current_step": current_step,
        "total_steps": total_steps,
        "progress_pct": progress_pct,
    }
    return render(request, "projetos/paginas/objetivo.html", ctx)


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
    fields = {"Content-Type": content_type}
    conditions = [
        {"Content-Type": content_type},
        ["content-length-range", 1, MAX_SIZE],
    ]

    presigned = s3.generate_presigned_post(
        Bucket=bucket,
        Key=key,
        Fields=fields,
        Conditions=conditions,
        ExpiresIn=60 * 5,
    )
    return JsonResponse({"upload": presigned, "key": key})




# ============================================================================
# Comprar Créditos
# ============================================================================

class ComprarCreditosView(TemplateView):
    template_name = "projetos/comprar_creditos_placeholder.html"


# ============================================================================
# Objetivos
# ============================================================================

class ObjetivoProjetoView(TemplateView):
    template_name = "projetos/paginas/objetivo.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        current = 1   # passo atual
        total   = 5   # total de passos
        ctx["current_step"] = current
        ctx["total_steps"]  = total
        ctx["progress_pct"] = int(current / total * 100)
        # (opcional: manter compatibilidade com 'step')
        ctx["step"] = current
        return ctx