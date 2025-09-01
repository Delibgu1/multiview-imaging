
from django.db import models
from django.conf import settings
from django.db.models import Q


class Dataset(models.Model):
    STATUS = [
        ("new", "Novo"),
        ("ready", "Pronto"),
        ("error", "Erro"),
    ]

    # Dono do dataset (escopo de listagem/download)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="datasets",
        null=True,   # manter True por enquanto para não quebrar dados antigos
        blank=True,
        help_text="Usuário responsável por este dataset.",
    )

    nome          = models.CharField(max_length=200)
    descricao     = models.TextField(blank=True)
    s3_key        = models.CharField(
        "Objeto S3/MinIO",
        max_length=500,
        blank=True,
        db_index=True,
        help_text="Caminho/prefixo no bucket (ex.: uploads/ano/arquivo.tif).",
    )
    tamanho_b     = models.BigIntegerField("Tamanho (bytes)", null=True, blank=True)
    crs           = models.CharField(max_length=64, blank=True)
    bounds        = models.CharField(max_length=255, blank=True)  # bbox "minx,miny,maxx,maxy"
    status        = models.CharField(max_length=20, choices=STATUS, default="new")
    criado_em     = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-criado_em"]
        indexes = [
            models.Index(fields=["owner", "criado_em"]),
            models.Index(fields=["status"]),
            models.Index(fields=["s3_key"]),
        ]
        constraints = [
            # Evita duplicidade de s3_key por usuário (ignora chave vazia)
            models.UniqueConstraint(
                fields=["owner", "s3_key"],
                name="uniq_dataset_owner_key",
                condition=~Q(s3_key=""),
            ),
        ]

    def __str__(self):
        return self.nome or self.filename

    @property
    def filename(self) -> str:
        if not self.s3_key:
            return ""
        return self.s3_key.rsplit("/", 1)[-1]

    @property
    def tamanho_humano(self) -> str:
        """Tamanho legível (só para exibir no template)."""
        b = self.tamanho_b or 0
        for unit in ("bytes", "KB", "MB", "GB", "TB"):
            if b < 1024.0 or unit == "TB":
                return f"{b:,.0f} {unit}".replace(",", ".")
            b /= 1024.0

    def can_be_accessed_by(self, user) -> bool:
        """Permissão simples: staff vê tudo; caso contrário, só o owner."""
        return bool(user and (user.is_staff or self.owner_id == user.id))


class Job(models.Model):
    TIPO = [
        ("cog", "Gerar COG"),
        ("thumb", "Gerar Thumbnail"),
        ("tiler", "Publicar no Tiler"),
        ("odm", "Processar no ODM"),
    ]
    STATUS = [
        ("queued", "Na fila"),
        ("running", "Executando"),
        ("done", "Concluído"),
        ("error", "Erro"),
    ]

    dataset       = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name="jobs")
    tipo          = models.CharField(max_length=20, choices=TIPO)
    status        = models.CharField(max_length=20, choices=STATUS, default="queued")
    criado_em     = models.DateTimeField(auto_now_add=True)
    iniciado_em   = models.DateTimeField(null=True, blank=True)
    finalizado_em = models.DateTimeField(null=True, blank=True)
    log           = models.TextField(blank=True)

    class Meta:
        ordering = ["-criado_em"]
        indexes = [
            models.Index(fields=["dataset", "status"]),
            models.Index(fields=["criado_em"]),
        ]

    def __str__(self):
        return f"{self.dataset} • {self.tipo} • {self.status}"
