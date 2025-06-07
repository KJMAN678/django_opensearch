docker compose run --rm web uv run manage.py migrate
docker compose run --rm web uv run manage.py createsuperuser --noinput
docker compose run --rm web uv run manage.py register_fake_blog_model --num 100
# インデックス作成に時間がかかるため、4秒待つ
sleep 4s
docker compose run --rm web uv run manage.py init_index
sleep 4s
# 検索ログのインポート
docker compose run --rm web uv run manage.py import_search_log search_log.csv
