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

    def clean(self):
        # se marcou que usa GCP, garanta arquivo
        if self.usa_gcp and not self.gcp_csv:
            from django.core.exceptions import ValidationError
            raise ValidationError({"gcp_csv": "Informe o arquivo CSV/TXT com os pontos de controle (GCP)."})

    # helper para parâmetros do processamento/WebODM
    def to_processing_options(self) -> dict:
        return {
            "camera_tipo": self.camera_tipo,
            "georef": self.georef,
            "epsg": self.epsg or None,
            "altura_voo_m": self.altura_voo_m,
            "gsd_cm": self.gsd_cm,
            "overlap_frontal": self.overlap_frontal,
            "overlap_lateral": self.overlap_lateral,
            "usa_gcp": self.usa_gcp,
            "gcp_csv": self.gcp_csv.name if self.gcp_csv else None,
            "produtos": {
                "ortomosaico": self.prod_ortomosaico,
                "dsm": self.prod_dsm,
                "dtm": self.prod_dtm,
                "nuvem_pts": self.prod_nuvem_pts,
                "contornos": self.prod_contornos,
            },
            "config": self.config or {},
        }
