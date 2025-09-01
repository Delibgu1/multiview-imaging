# multiview/multiview_imaging/web/projetos/forms.py (fixed)
import re
from django import forms
from .models import Projeto

EPSG_RE = re.compile(r"^EPSG:\d{4,6}$", re.IGNORECASE)

class ProjetoForm(forms.ModelForm):
    class Meta:
        model = Projeto
        fields = [
            "nome", "descricao",
            "data_voo", "plataforma", "camera_modelo", "camera_tipo",
            "georef", "epsg", "altura_voo_m", "gsd_cm",
            "overlap_frontal", "overlap_lateral",
            "usa_gcp", "gcp_csv",
            "prod_ortomosaico", "prod_dsm", "prod_dtm",
            "prod_nuvem_pts", "prod_contornos",
        ]
        widgets = {
            "data_voo": forms.DateInput(attrs={"type": "date"}),
            "descricao": forms.Textarea(attrs={"rows": 3}),
            "overlap_frontal": forms.NumberInput(attrs={"min": 0, "max": 100}),
            "overlap_lateral": forms.NumberInput(attrs={"min": 0, "max": 100}),
        }

    def clean(self):
        cleaned = super().clean()

        # 1) GCP consistência
        if cleaned.get("usa_gcp") and not cleaned.get("gcp_csv"):
            self.add_error("gcp_csv", "Informe o arquivo CSV/TXT com os GCPs.")
        if not cleaned.get("usa_gcp"):
            cleaned["gcp_csv"] = None

        # 2) EPSG formato
        epsg = (cleaned.get("epsg") or "").strip()
        if epsg and not EPSG_RE.match(epsg):
            self.add_error("epsg", 'Use o formato EPSG:#### (ex.: "EPSG:31983").')

        # 3) Recomendações de overlap
        front = cleaned.get("overlap_frontal")
        if front is not None and front < 50:
            self.add_error("overlap_frontal", "Mínimo recomendado: 50% (ideal ≥ 70%).")

        lateral = cleaned.get("overlap_lateral")
        if lateral is not None and lateral < 50:
            self.add_error("overlap_lateral", "Mínimo recomendado: 50% (ideal ≥ 60%).")

        # 4) Se usar RTK/PPK, incentive ter EPSG
        georef = cleaned.get("georef")
        if georef in (
            Projeto.GeoRef.RTK_FIXED,
            Projeto.GeoRef.RTK_FLOAT,
            Projeto.GeoRef.PPK,
        ) and not epsg:
            self.add_error("epsg", "Preencha o EPSG quando usar RTK/PPK.")

        return cleaned
