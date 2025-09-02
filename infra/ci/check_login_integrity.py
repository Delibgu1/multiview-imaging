#!/usr/bin/env python3
import sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]

# Descobrir onde está o app "core": web/core (preferido) ou core (fallback)
CANDIDATES = [ROOT / "web" / "core", ROOT / "core"]
APP = next((p for p in CANDIDATES if (p / "templates").exists() and (p / "static").exists()), None)

errors = []
if APP is None:
  errors.append(f"Não encontrei o app 'core' em {CANDIDATES}.")
  print("Login integrity check FAILED:")
  for e in errors: print(" -", e)
  sys.exit(1)

paths = {
  "base_public": APP / "templates" / "core" / "base_public.html",
  "login": APP / "templates" / "core" / "login.html",
  "footer": APP / "templates" / "core" / "partials" / "footer.html",
  "site_css": APP / "static" / "core" / "css" / "site.css",
  "auth_css": APP / "static" / "core" / "css" / "auth.css",
}

# Tokens de cores obrigatórias no site.css
required_css_tokens = {
  "site_css": ["#72A348", "#00371C", "#80CB2E"],
  "auth_css": [],
}

# Linhas obrigatórias no rodapé
required_footer_lines = [
  "Plataforma de Processamento de Imagens Multiview",
  "v0.1.0 - suporte.multiview@com.br",
  "Todos os Direitos Reservados",
]

# Imagens obrigatórias (aceita variações de nome/case)
img_dir = APP / "static" / "core" / "img"
img_sets = {
  "logo_mv": ["Logo-multiview.png", "logo-multiview.png", "logo_multiview.png", "logo_multiview_verde.png", "Logo_Multiview_verde.png"],
  "logo_sin": ["Logo-sinergica.png", "logo-sinergica.png", "logo_sinergica.png"],
  "slogan": ["slogan.png"],
}

def ensure_exists(p):
  if not p.exists():
    errors.append(f"Missing file: {p}")

# Arquivos base
for _, p in paths.items():
  ensure_exists(p)

# Cores no CSS
for key, tokens in required_css_tokens.items():
  p = paths[key]
  if p.exists():
    data = p.read_text(encoding="utf-8", errors="ignore")
    for t in tokens:
      if t not in data:
        errors.append(f"Missing token '{t}' in {p}")

# Rodapé
foot = paths["footer"]
if foot.exists():
  data = foot.read_text(encoding="utf-8", errors="ignore")
  for line in required_footer_lines:
    if line not in data:
      errors.append(f"Missing footer line in footer.html: '{line}'")

# Imagens (aceitando qualquer uma das variações)
for label, candidates in img_sets.items():
  if not any((img_dir / name).exists() for name in candidates):
    errors.append(f"Missing image asset for {label}: tente um de {candidates} em {img_dir}")

if errors:
  print("Login integrity check FAILED:")
  for e in errors: print(" -", e)
  sys.exit(1)
else:
  print("Login integrity check PASSED.")
