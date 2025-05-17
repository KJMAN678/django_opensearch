docker compose run --rm web uv run manage.py migrate
docker compose run --rm web uv run manage.py createsuperuser --noinput
docker compose run --rm web uv run manage.py register_fake_blog_model --num 100
# インデックス作成に時間がかかるため、4秒待つ
sleep 4s
docker compose run --rm web uv run manage.py init_index
