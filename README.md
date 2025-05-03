- .env ファイルを作成し、下記を入力
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
$ docker compose down
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
$ docker compose run --rm web uv run manage.py createsuperuser --noinput

# ダミーデータの登録
$ docker compose run --rm web uv run manage.py register_fake_blog_model --num 100

# OpenSearch のインデックス作成, 検索
$ docker compose run --rm web uv run manage.py init_index
```

```sh
# ruff の実行
$ docker compose run --rm web uv run ruff check . --fix
$ docker compose run --rm web uv run ruff format .
```

```sh
# app 追加
$ docker compose run --rm web uv run django-admin startapp search

# マイグレーション
$ docker compose run --rm web uv run manage.py makemigrations blog
$ docker compose run --rm web uv run manage.py migrate

# ダミーデータの登録
$ docker compose run --rm web uv run manage.py register_fake_blog_model --num 100

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

- [OpenSearch Version](https://docs.opensearch.org/docs/latest/version-history/)
- [OpenSearch DashBoard Version](https://github.com/opensearch-project/OpenSearch-Dashboards/releases)
- [analysis-sudachi](https://github.com/WorksApplications/elasticsearch-sudachi/releases/)
- [Sudachi-Dict](https://github.com/WorksApplications/SudachiDict/releases)
- [Elasticsearch / OpenSearch Sudachi プラグイン チュートリアル](https://github.com/WorksApplications/elasticsearch-sudachi/blob/develop/docs/tutorial.md)
- [OpenSearch Python Client Documentation](https://opensearch-project.github.io/opensearch-py/index.html)
- [opensearch-project/opensearch-py](https://github.com/opensearch-project/opensearch-py)
- 下記のDockerfileの記述を使用した
  - [krayinc/opensearch:2.17.1-sudachi-ingest-attachment](https://hub.docker.com/layers/krayinc/opensearch/2.17.1-sudachi-ingest-attachment/images/sha256-724966037bde19ced8fbc04dfbe1f78d7ef6363f3f7b1f19dfdcc1b8525107d3)
  - [opensearchproject/opensearch:2.17.1](https://hub.docker.com/layers/opensearchproject/opensearch/2.17.1/images/sha256-7d961ff222c267093b7b95fc2e397d31a06a42b6f3c42ee67fc5788417a274bf)
