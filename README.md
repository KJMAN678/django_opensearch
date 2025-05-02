.env ファイル作成
```sh
OPENSEARCH_INITIAL_ADMIN_PASSWORD=hoge
DJANGO_SUPERUSER_USERNAME=hoge
DJANGO_SUPERUSER_EMAIL=hoge@hoge.com
DJANGO_SUPERUSER_PASSWORD=hoge
```

```sh
# コンテナ立上げ
$ docker compose up -d

# コンテナの再作成
$ docker compose build --no-cache

# キャッシュ削除
$ docker builder prune -f

# OpenSearch DashBoard
http://localhost:5601/app/home#/

# Django 検索画面
http://localhost:8000/blog/
http://localhost:8000/admin/
```

```sh
$ docker compose run --rm web uv run manage.py migrate

# スーパーユーザーの作成
$ docker compose run --rm web uv run manage.py createsuperuser --no-input

# ダミーデータの登録
$ docker compose run --rm web uv run manage.py register_fake_blog_model --num 10

# OpenSearch のインデックス作成, 検索
$ docker compose run --rm web uv run manage.py init_index

# app 追加
$ docker compose run --rm web uv run django-admin startapp search

# マイグレーション
$ docker compose run --rm web uv run manage.py makemigrations blog
$ docker compose run --rm web uv run manage.py migrate
```

```sh
# ruff の実行
$ docker compose run --rm web uv run ruff check . --fix
$ docker compose run --rm web uv run ruff format .
```

```sh
# ダミーデータの登録
$ docker compose run --rm web uv run manage.py register_fake_blog_model --num 10

# OpenSearch のインデックス作成, 検索
$ docker compose run --rm web uv run manage.py init_index
$ docker compose run --rm web uv run manage.py search
```

```sh
# Django プロジェクト作成(初回のみ。作成済み)
$ cd web
$ uv run django-admin startproject config .
$ cd ..
```
