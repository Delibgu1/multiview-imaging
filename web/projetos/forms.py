# multiview/multiview_imaging/web/projetos/forms.py (fixed)
# projetos/forms.py
import re
import json
from django import forms
from .models import Projeto

# Regex para validar string EPSG:#####
EPSG_RE = re.compile(r"^EPSG:\d{4,6}$", re.IGNORECASE)


class ProjetoForm(forms.ModelForm):
    class Meta:
        model = Projeto
        fields = "__all__"

    # Helpers defensivos
    def _has_field(self, name: str) -> bool:
        return name in self.fields

    def _get(self, cleaned, name, default=None):
        return cleaned.get(name, default)

    def clean(self):
        """
        Validações consolidadas, com checagens condicionais
        para não falhar quando algum campo não existir no form.
        """
        cleaned = super().clean()


        # ------------------------------------------------------------------
        # 1) Oficial: exigir responsável técnico + POS/PEC (se os campos existirem)
        # ------------------------------------------------------------------
        finalidade = self._get(cleaned, "objetivo_finalidade")
        if finalidade == "oficial":
            req_fields = ["rt_nome", "rt_conselho", "rt_art", "pos_metodo", "pec_meta"]
            missing = []
            for f in req_fields:
                if self._has_field(f) and not self._get(cleaned, f):
                    missing.append(f)
            if missing:
                raise forms.ValidationError(
                    "Campos obrigatórios (Oficial) ausentes: " + ", ".join(missing)
                )

        # ------------------------------------------------------------------
        # 2) CRS × UTM coerentes
        #    - se CRS é UTM: exigir utm_zona
        #    - se CRS não é UTM: utm_zona deve ficar vazio
        # ------------------------------------------------------------------
        if self._has_field("crs_saida"):
            crs = self._get(cleaned, "crs_saida")
        else:
            crs = None

        utm = self._get(cleaned, "utm_zona") if self._has_field("utm_zona") else None

        if crs in {"SIRGAS_UTM", "WGS84_UTM"}:
            if self._has_field("utm_zona") and not utm:
                self.add_error("utm_zona", "Informe a zona UTM para o CRS selecionado.")
        else:
            # Se não for um CRS UTM, desencoraje preencher a zona
            if self._has_field("utm_zona") and utm:
                self.add_error("utm_zona", "Zona UTM só é válida quando o CRS de saída é UTM.")

        # ------------------------------------------------------------------
        # 3) GCPs quando selecionado e finalidade = oficial
        #    - campo 'voo_gnss' deve existir; se 'GCP' ou 'RTK_GCP' exigir 'voo_gcps_file'
        # ------------------------------------------------------------------
        if self._has_field("voo_gnss"):
            gnss = self._get(cleaned, "voo_gnss")
            needs_gcp = gnss in {"GCP", "RTK_GCP"}
            if finalidade == "oficial" and needs_gcp and self._has_field("voo_gcps_file"):
                if not self._get(cleaned, "voo_gcps_file"):
                    self.add_error("voo_gcps_file", "Envie o arquivo de GCPs para projetos oficiais.")

        # ------------------------------------------------------------------
        # 4) Faixas numéricas: overlaps e relação DEM/Ortho
        # ------------------------------------------------------------------
        def check_range(field, lo, hi, label=None):
            if not self._has_field(field):
                return
            val = self._get(cleaned, field)
            if val is None:
                return
            try:
                fval = float(val)
            except (TypeError, ValueError):
                self.add_error(field, f"{label or field}: valor inválido.")
                return
            if not (lo <= fval <= hi):
                self.add_error(field, f"{label or field} deve estar entre {lo} e {hi}.")

        check_range("overlap_frontal", 0, 100, "Overlap frontal (%)")
        check_range("overlap_lateral", 0, 100, "Overlap lateral (%)")

        # DEM >= Ortho (se ambos existirem e tiverem valor)
        if self._has_field("cfg_ortho_cm") and self._has_field("cfg_dem_cm"):
            ortho = self._get(cleaned, "cfg_ortho_cm")
            dem = self._get(cleaned, "cfg_dem_cm")
            try:
                if ortho not in (None, "") and dem not in (None, ""):
                    if float(dem) < float(ortho):
                        self.add_error(
                            "cfg_dem_cm",
                            "Resolução do DEM deve ser ≥ resolução do ortomosaico."
                        )
            except (TypeError, ValueError):
                # Se algum não for numérico, o próprio field já deve acusar; não duplicar erro aqui.
                pass

        # ------------------------------------------------------------------
        # 5) EPSG no formato 'EPSG:####' (se houver campo 'epsg')
        # ----------------------------------------------------------------__
        if self._has_field("epsg"):
            epsg = (self._get(cleaned, "epsg") or "").strip()
            if epsg and not EPSG_RE.match(epsg):
                self.add_error("epsg", 'Use o formato EPSG:#### (ex.: "EPSG:31983").')

        # ------------------------------------------------------------------
        # 6) Recomendações mínimas de overlap (não bloqueia, mas pode virar erro leve)
        #    Caso prefira obrigatório, troque por add_error como acima.
        # ------------------------------------------------------------------
        if self._has_field("overlap_frontal"):
            front = self._get(cleaned, "overlap_frontal")
            try:
                if front is not None and float(front) < 50:
                    # Aviso "forte": se quiser bloquear, substitua por add_error.
                    self.add_error("overlap_frontal", "Mínimo recomendado: 50% (ideal ≥ 70%).")
            except (TypeError, ValueError):
                pass

        if self._has_field("overlap_lateral"):
            lateral = self._get(cleaned, "overlap_lateral")
            try:
                if lateral is not None and float(lateral) < 50:
                    self.add_error("overlap_lateral", "Mínimo recomendado: 50% (ideal ≥ 60%).")
            except (TypeError, ValueError):
                pass

        # START — aceitar q1_json vindo do front (hidden)
        # Se o template do Quadro 1 enviar um input hidden "q1_json" com o payload,
        # guardamos em instance.config["q1"] para o models.clean() validar.
        try:
            q1_raw = self.data.get("q1_json")
            if q1_raw:
                q1 = json.loads(q1_raw)
                cfg = self.instance.config or {}
                cfg["q1"] = q1
                self.instance.config = cfg
        except Exception:
            # se vier quebrado, o models.clean() vai acusar 'config'
            pass
        # END


        return cleaned
