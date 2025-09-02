
# 1) Cria as pastas necessárias
mkdir .github\workflows -Force | Out-Null
mkdir infra\ci -Force | Out-Null

# 2) Workflow do GitHub Actions (bloqueia alterações no login sem label)
@"
name: Login Guard

on:
  pull_request:
    paths:
      - 'core/templates/core/base_public.html'
      - 'core/templates/core/login.html'
      - 'core/templates/core/partials/footer.html'
      - 'core/static/core/css/site.css'
      - 'core/static/core/css/auth.css'
      - 'core/static/core/img/**'

jobs:
  guard:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Fail unless approved label is present
        uses: mheap/github-action-required-labels@v3
        with:
          mode: exactly
          count: 1
          labels: |
            approved:login-change

      - name: Run integrity checks (colors, text, assets)
        run: python infra/ci/check_login_integrity.py
"@ | Set-Content -Encoding UTF8 .github\workflows\login-guard.yml

# 3) Checker de integridade (cores/textos/assets obrigatórios)
@"
#!/usr/bin/env python3
import sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
paths = {
  "base_public": ROOT / "core" / "templates" / "core" / "base_public.html",
  "login": ROOT / "core" / "templates" / "core" / "login.html",
  "footer": ROOT / "core" / "templates" / "core" / "partials" / "footer.html",
  "site_css": ROOT / "core" / "static" / "core" / "css" / "site.css",
  "auth_css": ROOT / "core" / "static" / "core" / "css" / "auth.css",
}
errors = []

required_css_tokens = {
  "site_css": ["#72A348", "#00371C", "#80CB2E"],
  "auth_css": [],
}
required_footer_lines = [
  "Plataforma de Processamento de Imagens Multiview",
  "v0.1.0 - suporte.multiview@com.br",
  "Todos os Direitos Reservados",
]
required_images = [
  ROOT / "core" / "static" / "core" / "img" / "Logo-multiview.png",
  ROOT / "core" / "static" / "core" / "img" / "Logo-sinergica.png",
  ROOT / "core" / "static" / "core" / "img" / "slogan.png",
]

def ensure_exists(p):
  if not p.exists():
    errors.append(f"Missing file: {p}")

for _, p in paths.items():
  ensure_exists(p)

for key, tokens in required_css_tokens.items():
  p = paths[key]
  if p.exists():
    data = p.read_text(encoding="utf-8", errors="ignore")
    for t in tokens:
      if t not in data:
        errors.append(f"Missing token '{t}' in {p}")

foot = paths["footer"]
if foot.exists():
  data = foot.read_text(encoding="utf-8", errors="ignore")
  for line in required_footer_lines:
    if line not in data:
      errors.append(f"Missing footer line in footer.html: '{line}'")

for img in required_images:
  if not img.exists():
    errors.append(f"Missing image asset: {img}")

if errors:
  print("Login integrity check FAILED:")
  for e in errors: print(" -", e)
  sys.exit(1)
else:
  print("Login integrity check PASSED.")
"@ | Set-Content -Encoding UTF8 infra\ci\check_login_integrity.py

# 4) .gitignore dentro de infra (evita .env e dados de runtime)
@"
.env
*.env
minio-data/
*-data/
*.log
*.pid
*.sock
tmp/
"@ | Set-Content -Encoding UTF8 infra\.gitignore

# 5) docker-compose.override.yml (mantém seu compose e usa volume nomeado p/ dados do MinIO)
@"
version: "3.9"
services:
  minio:
    volumes:
      - minio_data:/data
volumes:
  minio_data:
    driver: local
"@ | Set-Content -Encoding UTF8 infra\docker-compose.override.yml

# 6) README curto
@"
# Repo Hardening
- CI bloqueia mudanças no login sem o label 'approved:login-change'.
- Checker valida cores, textos e logos obrigatórios.
- .gitignore do infra protege .env e dados de runtime.
- Compose override move dados do MinIO para volume nomeado.
"@ | Set-Content -Encoding UTF8 README_LOGIN_GUARD.md
