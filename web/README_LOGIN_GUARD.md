# Repo Hardening
- CI bloqueia mudanças no login sem o label 'approved:login-change'.
- Checker valida cores, textos e logos obrigatórios.
- .gitignore do infra protege .env e dados de runtime.
- Compose override move dados do MinIO para volume nomeado.
