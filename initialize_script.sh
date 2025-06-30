docker compose run --rm web uv run manage.py migrate
docker compose run --rm web uv run manage.py createsuperuser --noinput
docker compose run --rm web uv run manage.py register_fake_blog_model --num 100
# インデックス作成に時間がかかるため、4秒待つ
sleep 4s
docker compose run --rm web uv run manage.py init_index
sleep 4s
# 検索ログのインポート
docker compose run --rm web uv run manage.py import_search_log search_log.csv
sleep 4s
docker compose run --rm web uv run manage.py register_searchlog_to_index
sleep 4s
# 同時検索ログのテスト（個別検索語をセッションIDでグループ化）
$ docker compose run --rm web uv run manage.py test_co_occurrence_search --query "おにぎり 梅 美味しい 新鮮" --user user_001
sleep 4s
# テストデータ作成 + 検索サジェスト生成（scripted-metric aggregations使用）
# search_suggestion インデックスが更新される
$ docker compose run --rm web uv run manage.py create_scripted_metric_suggestions --test-data
