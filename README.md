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

- 下記4つ + 初期化処理を実行するコンテナ再作成のスクリプト
$ source ./container_remake.sh

# コンテナの再作成
$ docker compose down
$ docker compose build
$ docker compose up -d
# キャッシュ削除
$ docker builder prune -f

# OpenSearch DashBoard
http://localhost:5601/app/opensearch-query-workbench#/

$ select * from related_search_word_log;
$ select * from no_order_related_search_word_log;

# Django 検索画面
http://localhost:8000/blog/

http://localhost:8000/admin/
```

```sh
- 下記の4つのスクリプトを実行して初期化する
$ source ./initialize_script.sh

$ docker compose run --rm web uv run manage.py migrate
# スーパーユーザーの作成
$ docker compose run --rm web uv run manage.py createsuperuser --noinput
# ダミーデータの登録
$ docker compose run --rm web uv run manage.py register_fake_blog_model --num 100
# OpenSearch のインデックス作成, 検索
$ docker compose run --rm web uv run manage.py init_index

$ docker compose run --rm web uv run manage.py make_backup
$ docker compose run --rm web uv run manage.py restore_backup
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

$ docker compose run --rm web uv run manage.py make_backup
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

- サジェスト
  - [Elasticsearchで関連キーワード機能がどれだけ低コストで実装できるかの旅路](https://www.m3tech.blog/entry/es-related-keywords)
  - [Significant terms aggregations](https://docs.opensearch.org/docs/latest/aggregations/bucket/significant-terms/)
  - [Terms aggregations](https://docs.opensearch.org/docs/latest/aggregations/bucket/terms/)
  - [Aggregations](https://docs.opensearch.org/docs/latest/aggregations/)
  - [OpenSearch・Go・MUI で実現する検索サジェスト機能](https://koko206.hatenablog.com/entry/2024/07/30/035720)
  - [Update document](https://docs.opensearch.org/docs/latest/api-reference/document-apis/update-document/)
  - [Update by query](https://docs.opensearch.org/docs/latest/api-reference/document-apis/update-by-query/#request-body-options)
```sh
{
  "query": {
    "term": {
      "oldValue": 20
    }
  },
  "script" : {
    "source": "ctx._source.oldValue += params.newValue",
    "lang": "painless",
    "params" : {
      "newValue" : 10
    }
  }
}
```
- [upsert](https://docs.opensearch.org/docs/latest/api-reference/document-apis/update-document/#using-the-upsert-operation)
