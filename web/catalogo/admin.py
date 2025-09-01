
# catalogo/admin.py
from django.contrib import admin
from .models import Dataset, Job

@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ("id", "nome", "owner", "status", "s3_key", "tamanho_b", "criado_em")
    search_fields = ("nome", "s3_key", "owner__username", "owner__email")
    list_filter = ("status",)
    autocomplete_fields = ("owner",)

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("id", "dataset", "tipo", "status", "criado_em")
    list_filter = ("tipo", "status")
    search_fields = ("dataset__nome", "dataset__s3_key")
