from django.core.management.base import BaseCommand
from search.search_log import make_client
from search.documents import SearchSuggestionDocument
import json


class Command(BaseCommand):
    help = "Generate search suggestions using scripted-metric aggregations"

    def add_arguments(self, parser):
        parser.add_argument('--test-data', action='store_true', help='Create test co-occurrence data')

    def handle(self, *args, **options):
        client = make_client()
        
        if options['test_data']:
            self.create_test_data()
        
        self.generate_suggestions_with_scripted_metric()

    def create_test_data(self):
        """テスト用の同時検索データを作成"""
        from search.search_log import co_occurrence_search_log
        
        test_searches = [
            "おにぎり 梅 美味しい",
            "おにぎり 鮭 美味しい", 
            "おにぎり 昆布 美味しい",
            "梅 美味しい 酸っぱい",
            "美味しい 料理 簡単"
        ]
        
        for search in test_searches:
            session_id = co_occurrence_search_log(search)
            self.stdout.write(f"Created test data for: {search} (session: {session_id})")

    def generate_suggestions_with_scripted_metric(self):
        """scripted-metric aggregationを使って検索サジェストを生成"""
        client = make_client()
        
        scripted_metric_query = {
            "size": 0,
            "aggs": {
                "session_combinations": {
                    "terms": {
                        "field": "session_id",
                        "size": 1000
                    },
                    "aggs": {
                        "word_combinations": {
                            "scripted_metric": {
                                "init_script": """
                                    state.words = [];
                                    state.user_id = null;
                                """,
                                "map_script": """
                                    state.words.add(doc['search_word'].value);
                                    if (state.user_id == null) {
                                        state.user_id = doc['user_id'].value;
                                    }
                                """,
                                "combine_script": """
                                    return ['words': state.words, 'user_id': state.user_id];
                                """,
                                "reduce_script": """
                                    def combinations = [];
                                    def words = [];
                                    def user_id = null;
                                    
                                    for (state in states) {
                                        if (state.words != null) {
                                            words.addAll(state.words);
                                            if (user_id == null) {
                                                user_id = state.user_id;
                                            }
                                        }
                                    }
                                    
                                    if (words.size() == 0) {
                                        return combinations;
                                    }
                                    
                                    // Handle single word case
                                    if (words.size() == 1) {
                                        def single_word = words.get(0);
                                        combinations.add(['search_query': single_word, 'suggestion': single_word]);
                                        return combinations;
                                    }
                                    
                                    // Simple approach: generate combinations directly without complex permutations
                                    // This avoids Painless scripting limitations with complex algorithms
                                    
                                    // For each word position, create search_query + remaining words combinations
                                    for (int i = 1; i < words.size(); i++) {
                                        // Take first i words as search query
                                        def query_words = [];
                                        for (int j = 0; j < i; j++) {
                                            query_words.add(words.get(j));
                                        }
                                        
                                        // Take remaining words as suggestion
                                        def remaining_words = [];
                                        for (int j = i; j < words.size(); j++) {
                                            remaining_words.add(words.get(j));
                                        }
                                        
                                        if (query_words.size() > 0 && remaining_words.size() > 0) {
                                            def search_query = String.join(' ', query_words);
                                            def suggestion = String.join(' ', remaining_words);
                                            combinations.add(['search_query': search_query, 'suggestion': suggestion]);
                                        }
                                    }
                                    
                                    // Create single word queries with search_query + each co-occurring word
                                    for (int i = 0; i < words.size(); i++) {
                                        def single_word = words.get(i);
                                        
                                        for (int j = 0; j < words.size(); j++) {
                                            if (j != i) {
                                                def co_occurring_word = words.get(j);
                                                def suggestion = single_word + ' ' + co_occurring_word;
                                                combinations.add(['search_query': single_word, 'suggestion': suggestion]);
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
            
            self.process_scripted_metric_results(response)
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error executing scripted-metric aggregation: {e}"))

    def process_scripted_metric_results(self, response):
        """scripted-metricの結果を処理してsearch_suggestionインデックスに保存"""
        client = make_client()
        
        if not client.indices.exists(index="search_suggestion"):
            SearchSuggestionDocument.init(using=client, index="search_suggestion")
        
        suggestion_count = 0
        
        self.stdout.write(f"Processing {len(response['aggregations']['session_combinations']['buckets'])} sessions...")
        
        for session_bucket in response["aggregations"]["session_combinations"]["buckets"]:
            session_id = session_bucket["key"]
            combinations = session_bucket["word_combinations"]["value"]
            
            self.stdout.write(f"Session {session_id[:8]}... has {len(combinations)} combinations")
            
            for combo in combinations:
                search_query = combo["search_query"]
                suggestion = combo["suggestion"]
                
                doc_id = f"{search_query}_{suggestion}".replace(" ", "_").replace("　", "_")
                
                try:
                    client.update(
                        id=doc_id,
                        index="search_suggestion",
                        body={
                            "script": {
                                "source": "ctx._source.co_occurrence_count += 1",
                                "lang": "painless",
                            },
                            "upsert": {
                                "search_query": search_query,
                                "related_keyword_suggestion": suggestion,
                                "co_occurrence_count": 1,
                            },
                        },
                    )
                    suggestion_count += 1
                    self.stdout.write(f"Saved: '{search_query}' -> '{suggestion}'")
                except Exception as e:
                    self.stdout.write(f"Error saving suggestion '{search_query}' -> '{suggestion}': {e}")
        
        self.stdout.write(f"Generated {suggestion_count} search suggestions using scripted-metric")
        self.display_suggestions()

    def display_suggestions(self):
        """生成されたサジェストを表示"""
        client = make_client()
        
        try:
            response = client.search(
                index="search_suggestion",
                body={
                    "query": {"match_all": {}},
                    "size": 50,
                    "sort": [{"co_occurrence_count": {"order": "desc"}}]
                }
            )
            
            self.stdout.write(f"\n=== Generated Search Suggestions (Scripted-Metric) ===")
            for hit in response["hits"]["hits"]:
                source = hit["_source"]
                self.stdout.write(
                    f"検索クエリ: '{source['search_query']}', "
                    f"関連キーワードサジェスト: '{source['related_keyword_suggestion']}', "
                    f"共起回数: {source['co_occurrence_count']}"
                )
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error displaying suggestions: {e}"))
