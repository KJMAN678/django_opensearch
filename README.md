```sh
$ docker compose up -d

# OpenSearch DashBoard
http://localhost:5601/app/home#/

# Django
http://localhost:8000/
```

```sh
# スーパーユーザーの作成
$ docker compose run --rm web uv run manage.py createsuperuser

# app 追加
$ docker compose run --rm web uv run django-admin startapp blog

# マイグレーション
$ docker compose run --rm web uv run manage.py makemigrations config
$ docker compose run --rm web uv run manage.py migrate
```

```sh
# Django プロジェクト作成(初回のみ。作成済み)
$ cd web
$ uv run django-admin startproject config .
$ cd ..
```
