from django.core.management.base import BaseCommand
from opensearchpy import OpenSearch
import environ


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

        # Create an index with non-default settings.
        index_name = 'python-test-index'
        index_body = {
            'settings': {
                'index': {
                'number_of_shards': 4
                }
            }
        }

        response = client.indices.create(index_name, body=index_body)
        print('\nCreating index:')
        print(response)

        # Add a document to the index.
        document = {
            'title': 'Moneyball',
            'director': 'Bennett Miller',
            'year': '2011'
        }
        id = '1'

        response = client.index(
            index = index_name,
            body = document,
            id = id,
            refresh = True
        )

        print('\nAdding document:')
        print(response)

        # Perform bulk operations

        movies = '{ "index" : { "_index" : "my-dsl-index", "_id" : "2" } } \n { "title" : "Interstellar", "director" : "Christopher Nolan", "year" : "2014"} \n { "create" : { "_index" : "my-dsl-index", "_id" : "3" } } \n { "title" : "Star Trek Beyond", "director" : "Justin Lin", "year" : "2015"} \n { "update" : {"_id" : "3", "_index" : "my-dsl-index" } } \n { "doc" : {"year" : "2016"} }'

        client.bulk(movies)

        # Search for the document.
        q = 'miller'
        query = {
        'size': 5,
        'query': {
            'multi_match': {
            'query': q,
            'fields': ['title^2', 'director']
            }
        }
        }

        response = client.search(
            body = query,
            index = index_name
        )
        print('\nSearch results:')
        print(response)

        # Delete the document.
        response = client.delete(
            index = index_name,
            id = id
        )

        print('\nDeleting document:')
        print(response)

        # Delete the index.
        response = client.indices.delete(
            index = index_name
        )

        print('\nDeleting index:')
        print(response)
