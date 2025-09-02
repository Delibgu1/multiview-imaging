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
