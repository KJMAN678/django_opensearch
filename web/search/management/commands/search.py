from django.core.management.base import BaseCommand
from opensearchpy import OpenSearch
import environ
from search.documents import BlogDocument


class Command(BaseCommand):
    help = "インデックス作成"

    def handle(self, *args, **options):

        host = 'opensearch'
        port = 9200

        env = environ.Env()
        environ.Env.read_env(".env")
        OPENSEARCH_INITIAL_ADMIN_PASSWORD = env('OPENSEARCH_INITIAL_ADMIN_PASSWORD')
        auth = ('admin', OPENSEARCH_INITIAL_ADMIN_PASSWORD)

        client = OpenSearch(
            hosts=[{'host': host, 'port': port}],
            http_auth=auth,
            use_ssl=True,
            verify_certs=False,
            ssl_assert_hostname=False,
            ssl_show_warn=False,
        )

        # データの検索
        response = client.search(
            index=BlogDocument._index._name,
            body={
                "query": {
                    "match": {
                        "title": "動物"
                    }
                }
            }
        )
        print(response)
