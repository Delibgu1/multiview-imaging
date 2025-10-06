# multiview/multiview_imaging/web/projetos/models.py (fixed)
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from django.db import models
from django.urls import reverse

class Projeto(models.Model):
    # --- enums ---
    class CameraTipo(models.TextChoices):
        RGB = "RGB", "RGB"
        MS = "MS", "Multiespectral"
        RGB_MS = "RGB_MS", "RGB + Multiespectral"

    class GeoRef(models.TextChoices):
        NONE = "NONE", "Sem RTK/PPK"
        RTK_FIXED = "RTK_FIXED", "RTK (Fix)"
        RTK_FLOAT = "RTK_FLOAT", "RTK (Float)"
        PPK = "PPK", "PPK"

    class Status(models.TextChoices):
        DEFINICOES = "DEFINICOES", "Em definições"
        AGUARDANDO_UPLOAD = "AGUARDANDO_UPLOAD", "Aguardando upload"
        PROCESSANDO = "PROCESSANDO", "Processando"
        CONCLUIDO = "CONCLUIDO", "Concluído"
        FALHOU = "FALHOU", "Falhou"

    # --- dono / identificação ---
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="projetos",
    )
    nome = models.CharField("Nome do projeto", max_length=200)
    descricao = models.TextField("Descrição (opcional)", blank=True)

    # --- metadados do voo ---
    data_voo = models.DateField("Data do voo", null=True, blank=True)
    plataforma = models.CharField("Plataforma (drone)", max_length=120, blank=True)
    camera_modelo = models.CharField("Modelo da câmera", max_length=120, blank=True)
    camera_tipo = models.CharField(
        "Tipo de câmera",
        max_length=10,
        choices=CameraTipo.choices,
        default=CameraTipo.RGB,
    )
    georef = models.CharField(
        "Georreferenciamento",
        max_length=12,
        choices=GeoRef.choices,
        default=GeoRef.NONE,
    )
    epsg = models.CharField(
        "EPSG",
        max_length=32,
        blank=True,
        help_text='Ex.: "EPSG:31983"',
    )
    altura_voo_m = models.FloatField("Altura de voo (m)", null=True, blank=True)
    gsd_cm = models.FloatField("GSD (cm/pixel)", null=True, blank=True)
    overlap_frontal = models.PositiveSmallIntegerField(
        "Overlap frontal (%)",
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="0–100%",
    )
    overlap_lateral = models.PositiveSmallIntegerField(
        "Overlap lateral (%)",
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="0–100%",
    )

    # --- GCP ---
    usa_gcp = models.BooleanField("Usa GCP", default=False)
    gcp_csv = models.FileField(
        "Arquivo GCP (CSV/TXT)",
        upload_to="gcps/",
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=["csv", "txt"])],
        help_text="Cabeçalho típico: label, x, y, z, lon, lat, alt (ou conforme template).",
    )

    # --- produtos desejados ---
    prod_ortomosaico = models.BooleanField("Ortomosaico", default=True)
    prod_dsm = models.BooleanField("DSM", default=False)
    prod_dtm = models.BooleanField("DTM", default=False)
    prod_nuvem_pts = models.BooleanField("Nuvem de pontos", default=False)
    prod_contornos = models.BooleanField("Curvas de nível", default=False)

    # --- opções avançadas ---
    config = models.JSONField("Opções avançadas", default=dict, blank=True)

    # --- status ---
    status = models.CharField("Status", max_length=24, choices=Status.choices, default=Status.DEFINICOES)

    # --- metadados ---
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-criado_em"]
        indexes = [
            models.Index(fields=["owner", "criado_em"]),
        ]

    def __str__(self) -> str:
        return f"{self.nome} ({self.owner})"

    def get_absolute_url(self):
        return reverse("projetos:detail", kwargs={"pk": self.pk})

    def get_upload_url(self):
        return reverse("projetos:upload", kwargs={"pk": self.pk})

    # helpers/constantes Quadro 1
    FORMATOS_VALIDOS = {"GPKG", "SHP", "GEOJSON", "GEOTIFF", "COG"}

    @staticmethod
    def _norm_epsg(value: str) -> str:
        if not value:
            return ""
        v = (value or "").strip().upper()
        if v.startswith("EPSG:"):
            return v
        if v.isdigit():
            return f"EPSG:{v}"
        if ":" in v:
            left, right = v.split(":", 1)
            if right.strip().isdigit():
                return f"EPSG:{right.strip()}"
        return v  # clean() valida
    # END


    def clean(self):
        from django.core.exceptions import ValidationError

        errors = {}
        # (1) sua regra de GCP (mantida)
        if self.usa_gcp and not self.gcp_csv:
            errors["gcp_csv"] = "Informe o arquivo CSV/TXT com os pontos de controle (GCP)."

        # (2) Quadro 1 SEMPRE avaliado (fora do if acima)
        q1 = (self.config or {}).get("q1") or {}

        # 2.1) CRS padrão
        crs_padrao = q1.get("crs_padrao") or self.epsg or ""
        crs_padrao = self._norm_epsg(crs_padrao)
        if crs_padrao and not crs_padrao.upper().startswith("EPSG:"):
            errors["epsg"] = 'CRS inválido. Use "EPSG:####".'
        self.epsg = crs_padrao  # mantém compat com legado

        # 2.2) Sensores
        sensores = q1.get("sensores") or {}
        any_sensor = any(bool(sensores.get(k)) for k in ("rgb", "ms", "thermal", "rgb_ms"))
        if q1 and not any_sensor:
            errors["config"] = "Selecione pelo menos um tipo de câmera/sensor."

        # 2.3) Produtos × sensores
        produtos = q1.get("produtos") or {}
        raster = produtos.get("raster") or []
        if "LST" in raster and not bool(sensores.get("thermal")):
            errors["config"] = "'Produto térmico (LST)' requer sensor Térmico."
        if ("IV" in raster) and not (sensores.get("rgb") or sensores.get("ms") or sensores.get("rgb_ms")):
            errors["config"] = "'Índices de Vegetação' requer RGB e/ou Multiespectral."

        # 2.4) Formatos
        formatos = q1.get("formatos") or []
        tem_prod = bool(raster or (produtos.get("vetor") or []))
        if tem_prod and not formatos:
            errors["config"] = "Escolha pelo menos um formato de entrega."
        for f in formatos:
            if f and f.upper() not in self.FORMATOS_VALIDOS:
                errors["config"] = f"Formato inválido: {f}"

        # 2.5) Vetoriais do cliente
        vet = q1.get("vetores_cliente") or {}
        if vet.get("usar"):
            modo = (vet.get("modo") or "").upper()
            if modo == "OUTRO":
                epsg_cli = self._norm_epsg(vet.get("epsg") or "")
                if not (epsg_cli and epsg_cli.upper().startswith("EPSG:")):
                    errors["config"] = 'Informe o EPSG dos vetores do cliente no formato "EPSG:####".'
                else:
                    vet["epsg"] = epsg_cli
            q1["vetores_cliente"] = vet

        if errors:
            raise ValidationError(errors)

        cfg = self.config or {}
        if q1:
            cfg["q1"] = q1
            self.config = cfg
        # END

    # helper para parâmetros do processamento/WebODM
    # START — to_processing_options com Quadro 1
    def to_processing_options(self) -> dict:
        q1 = (self.config or {}).get("q1") or {}
        sensores = q1.get("sensores") or {}
        produtos = q1.get("produtos") or {}
        vet = q1.get("vetores_cliente") or {}

        return {
            "camera_tipo": self.camera_tipo,  # compat legado
            "georef": self.georef,  # compat legado
            "epsg": self.epsg or None,  # normalizado em clean()
            "altura_voo_m": self.altura_voo_m,
            "gsd_cm": self.gsd_cm,
            "overlap_frontal": self.overlap_frontal,
            "overlap_lateral": self.overlap_lateral,
            "usa_gcp": self.usa_gcp,
            "gcp_csv": self.gcp_csv.name if self.gcp_csv else None,

            # Produtos legados (seu bloco atual)
            "produtos": {
                "ortomosaico": self.prod_ortomosaico,
                "dsm": self.prod_dsm,
                "dtm": self.prod_dtm,
                "nuvem_pts": self.prod_nuvem_pts,
                "contornos": self.prod_contornos,
                # NOVO: produtos do Quadro 1 (se vierem)
                "raster_extras": produtos.get("raster") or [],
                "vetor_extras": produtos.get("vetor") or [],
            },

            # NOVO: escolhas do Quadro 1 (para o pipeline)
            "q1": {
                "finalidade": q1.get("finalidade") or None,
                "objetivo_especifico": q1.get("objetivo_especifico") or None,
                "formatos": q1.get("formatos") or [],
                "sensores": {
                    "rgb": bool(sensores.get("rgb")),
                    "ms": bool(sensores.get("ms")),
                    "thermal": bool(sensores.get("thermal")),
                    "rgb_ms": bool(sensores.get("rgb_ms")),
                },
                "vetores_cliente": {
                    "usar": bool(vet.get("usar")),
                    "modo": vet.get("modo") or None,
                    "epsg": vet.get("epsg") or None,
                },
            },

            "config": self.config or {},  # mantém tudo
        }
    # END