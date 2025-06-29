- .env ファイルを作成し、下記を入力
```sh
OPENSEARCH_INITIAL_ADMIN_PASSWORD=hoge
DJANGO_SUPERUSER_USERNAME=hoge
DJANGO_SUPERUSER_EMAIL=hoge@hoge.com
DJANGO_SUPERUSER_PASSWORD=hoge
```

source ./generate_certs.sh

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
$ select * from agg_past_search_log;

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

## OpenSearch Index-Transforms 機能

```sh
# Index-Transforms ジョブの作成と実行
$ docker compose run --rm web uv run manage.py create_index_transform --delete-existing --execute

# Transform ジョブの管理（作成、開始、停止、削除、状態確認）
$ docker compose run --rm web uv run manage.py manage_transform_jobs --action create --job-name blog_monthly_transform
$ docker compose run --rm web uv run manage.py manage_transform_jobs --action start --job-name blog_monthly_transform
$ docker compose run --rm web uv run manage.py manage_transform_jobs --action stop --job-name blog_monthly_transform
$ docker compose run --rm web uv run manage.py manage_transform_jobs --action delete --job-name blog_monthly_transform
$ docker compose run --rm web uv run manage.py manage_transform_jobs --action status --job-name blog_monthly_transform

# 変換されたインデックスの検索
$ docker compose run --rm web uv run manage.py search_transformed_index --index blog_monthly_stats
```

## 検索サジェスト機能（Scripted-Metric Aggregations）

```sh
# テストデータ作成 + 検索サジェスト生成（scripted-metric aggregations使用）
$ docker compose run --rm web uv run manage.py create_scripted_metric_suggestions --test-data

# 同時検索ログのテスト（個別検索語をセッションIDでグループ化）
$ docker compose run --rm web uv run manage.py test_co_occurrence_search --query "おにぎり 梅 美味しい" --user-id user_001

# 単語1つでもテスト可能
$ docker compose run --rm web uv run manage.py test_co_occurrence_search --query "おにぎり"
```

### 検索サジェスト機能の仕組み

1. **同時検索ログの記録**: 「おにぎり 梅 美味しい」を入力すると、各単語を個別にログ記録
   ```
   検索ワード: おにぎり, セッションID: abc123, ユーザーID: user_001
   検索ワード: 梅,     セッションID: abc123, ユーザーID: user_001  
   検索ワード: 美味しい, セッションID: abc123, ユーザーID: user_001
   ```

2. **Scripted-Metric Aggregations**: 同じセッションIDの検索語から順列を生成し、検索サジェストを作成
   ```
   検索クエリ: おにぎり → 関連サジェスト: おにぎり 梅 美味しい
   検索クエリ: 梅 → 関連サジェスト: 梅 おにぎり 美味しい
   検索クエリ: おにぎり 梅 → 関連サジェスト: おにぎり 梅 美味しい
   ```

3. **汎用的な順列生成**: 単語数に関係なく動作（1語〜5語以上まで対応）

```sh
# app 追加
$ docker compose run --rm web uv run django-admin startapp search

# マイグレーション
$ docker compose run --rm web uv run manage.py makemigrations blog search
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
