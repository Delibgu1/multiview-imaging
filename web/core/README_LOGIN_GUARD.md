# Repo Hardening

- **Login Guard**: CI blocks any change to login templates/CSS/images unless PR has label `approved:login-change`.
- **Integrity Check**: `infra/ci/check_login_integrity.py` verifies colors/text/assets.
- **Infra .gitignore**: prevents committing `.env` and runtime data (`minio-data/`).
- **Compose override**: `infra/docker-compose.override.yml` switches MinIO to a named volume without touching your current compose.
