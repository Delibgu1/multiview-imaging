
# catalogo/views.py
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render
from .models import Dataset

@login_required()
def index(request):
    """
    Lista datasets:
      - staff/superuser: vê todos
      - usuário comum: vê apenas os próprios (owner=request.user)
    Suporta busca (?q=) por nome/descrição/s3_key e paginação (?page=&per_page=).
    """
    qs = Dataset.objects.all() if request.user.is_staff else Dataset.objects.filter(owner=request.user)

    q = (request.GET.get("q") or "").strip()
    if q:
        qs = qs.filter(
            Q(nome__icontains=q) | Q(descricao__icontains=q) | Q(s3_key__icontains=q)
        )

    qs = (
        qs.order_by("-criado_em")
          .select_related("owner")
          .only("id", "nome", "descricao", "s3_key", "tamanho_b", "status", "criado_em", "owner")
    )

    try:
        per_page = min(max(int(request.GET.get("per_page", 25)), 1), 100)
    except ValueError:
        per_page = 25

    paginator = Paginator(qs, per_page)
    page_obj = paginator.get_page(request.GET.get("page") or 1)

    return render(
        request,
        "catalogo/index.html",
        {
            "datasets": page_obj,   # seu template já itera sobre isso
            "page_obj": page_obj,
            "is_staff": request.user.is_staff,
            "query": q,
            "per_page": per_page,
        },
    )
