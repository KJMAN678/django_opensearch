from django.core.management.base import BaseCommand
from search.search_log import permutation_search_word_log, make_client


class Command(BaseCommand):
    help = "Test permutation search functionality"

    def add_arguments(self, parser):
        parser.add_argument('--query', type=str, default='おにぎり 梅 美味しい', help='Search query to test')

    def handle(self, *args, **options):
        test_query = options['query']
        
        self.stdout.write(f"Testing permutation search with: '{test_query}'")
        
        permutation_search_word_log(test_query)
        
        client = make_client()
        
        try:
            response = client.search(
                index="permutation_search_word_log",
                body={
                    "query": {"match": {"original_search_query": test_query}},
                    "size": 20,
                    "sort": [{"permutation_order": {"order": "asc"}}]
                }
            )
            
            self.stdout.write(f"\n=== Generated Permutations ===")
            for hit in response["hits"]["hits"]:
                source = hit["_source"]
                self.stdout.write(
                    f"Search Query: '{source['search_query']}', "
                    f"Related Word: '{source['related_search_word']}', "
                    f"Count: {source['count']}"
                )
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error searching permutations: {e}"))
