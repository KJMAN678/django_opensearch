from django.core.management.base import BaseCommand
from search.search_log import co_occurrence_search_log, make_client


class Command(BaseCommand):
    help = "Test co-occurrence search functionality"

    def add_arguments(self, parser):
        parser.add_argument('--query', type=str, default='おにぎり 梅 美味しい', help='Search query to test')
        parser.add_argument('--user', type=str, default='user_001', help='User ID')
        parser.add_argument('--test-scripted-metric', action='store_true', help='Test scripted-metric aggregation')

    def handle(self, *args, **options):
        test_query = options['query']
        user_id = options['user']
        
        self.stdout.write(f"Testing co-occurrence search with: '{test_query}' for user: {user_id}")
        
        session_id = co_occurrence_search_log(test_query, user_id)
        
        self.stdout.write(f"Created session: {session_id}")
        
        client = make_client()
        
        try:
            response = client.search(
                index="co_occurrence_search_log",
                body={
                    "query": {"term": {"session_id": session_id}},
                    "size": 20,
                    "sort": [{"created_at": {"order": "asc"}}]
                }
            )
            
            self.stdout.write(f"\n=== Recorded Co-occurrence Log ===")
            for i, hit in enumerate(response["hits"]["hits"], 1):
                source = hit["_source"]
                self.stdout.write(
                    f"{i}. 検索ワード: '{source['search_word']}', "
                    f"セッションID: {source['session_id'][:8]}..., "
                    f"ユーザー: {source['user_id']}"
                )
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error searching co-occurrence log: {e}"))
        
        if options['test_scripted_metric']:
            self.test_scripted_metric_aggregation()

    def test_scripted_metric_aggregation(self):
        """Test scripted-metric aggregation directly"""
        client = make_client()
        
        self.stdout.write(f"\n=== Testing Scripted-Metric Aggregation ===")
        
        scripted_metric_query = {
            "size": 0,
            "aggs": {
                "session_combinations": {
                    "terms": {
                        "field": "session_id",
                        "size": 10
                    },
                    "aggs": {
                        "word_combinations": {
                            "scripted_metric": {
                                "init_script": "state.words = []",
                                "map_script": "state.words.add(doc['search_word'].value)",
                                "combine_script": "return state.words",
                                "reduce_script": """
                                    def all_words = [];
                                    for (words in states) {
                                        all_words.addAll(words);
                                    }
                                    def combinations = [];
                                    if (all_words.size() >= 2) {
                                        for (int i = 1; i < all_words.size(); i++) {
                                            for (int start = 0; start <= all_words.size() - i; start++) {
                                                def query_words = [];
                                                def remaining_words = [];
                                                
                                                for (int k = start; k < start + i; k++) {
                                                    query_words.add(all_words.get(k));
                                                }
                                                
                                                for (int k = 0; k < all_words.size(); k++) {
                                                    if (k < start || k >= start + i) {
                                                        remaining_words.add(all_words.get(k));
                                                    }
                                                }
                                                
                                                if (query_words.size() > 0 && remaining_words.size() > 0) {
                                                    def search_query = String.join(' ', query_words);
                                                    def suggestion = search_query + ' ' + String.join(' ', remaining_words);
                                                    combinations.add(['search_query': search_query, 'suggestion': suggestion]);
                                                }
                                            }
                                        }
                                    }
                                    return combinations;
                                """
                            }
                        }
                    }
                }
            }
        }
        
        try:
            response = client.search(
                index="co_occurrence_search_log",
                body=scripted_metric_query
            )
            
            for session_bucket in response["aggregations"]["session_combinations"]["buckets"]:
                session_id = session_bucket["key"]
                combinations = session_bucket["word_combinations"]["value"]
                
                self.stdout.write(f"\nSession: {session_id[:8]}...")
                for i, combo in enumerate(combinations, 1):
                    self.stdout.write(
                        f"{i}. 検索クエリ: '{combo['search_query']}', "
                        f"関連キーワードサジェスト: '{combo['suggestion']}'"
                    )
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error testing scripted-metric: {e}"))
