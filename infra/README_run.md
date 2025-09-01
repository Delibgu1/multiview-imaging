## 3) `infra/README_run.md`
```md
# Rodando em DEV

1) `cd infra && docker compose up -d --build`
2) Acesse o MinIO em http://localhost:9001 (admin/adminadmin) e crie o bucket `multiview-data`.
3) `docker compose exec web python manage.py migrate`
4) `docker compose exec web python manage.py createsuperuser`
5) App: http://localhost:8000 | TiTiler: http://localhost:8081
```