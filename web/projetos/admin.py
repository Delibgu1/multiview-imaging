

from django.contrib import admin
from .models import Projeto

@admin.register(Projeto)
class ProjetoAdmin(admin.ModelAdmin):
    list_display = ("id", "nome", "owner", "camera_tipo", "georef", "criado_em")
    list_filter = ("camera_tipo", "georef", "criado_em")
    search_fields = ("nome", "owner__username")


