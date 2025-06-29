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
                                    
                                    // Generate all permutations for multiple words
                                    def permutations = [];
                                    
                                    // Generate permutations based on word count
                                    if (words.size() == 2) {
                                        def w0 = words.get(0);
                                        def w1 = words.get(1);
                                        permutations.add([w0, w1]);
                                        permutations.add([w1, w0]);
                                    } else if (words.size() == 3) {
                                        def w0 = words.get(0);
                                        def w1 = words.get(1);
                                        def w2 = words.get(2);
                                        
                                        permutations.add([w0, w1, w2]);
                                        permutations.add([w0, w2, w1]);
                                        permutations.add([w1, w0, w2]);
                                        permutations.add([w1, w2, w0]);
                                        permutations.add([w2, w0, w1]);
                                        permutations.add([w2, w1, w0]);
                                    } else if (words.size() == 4) {
                                        // Generate all 24 permutations for 4 words
                                        def w0 = words.get(0);
                                        def w1 = words.get(1);
                                        def w2 = words.get(2);
                                        def w3 = words.get(3);
                                        
                                        permutations.add([w0, w1, w2, w3]);
                                        permutations.add([w0, w1, w3, w2]);
                                        permutations.add([w0, w2, w1, w3]);
                                        permutations.add([w0, w2, w3, w1]);
                                        permutations.add([w0, w3, w1, w2]);
                                        permutations.add([w0, w3, w2, w1]);
                                        permutations.add([w1, w0, w2, w3]);
                                        permutations.add([w1, w0, w3, w2]);
                                        permutations.add([w1, w2, w0, w3]);
                                        permutations.add([w1, w2, w3, w0]);
                                        permutations.add([w1, w3, w0, w2]);
                                        permutations.add([w1, w3, w2, w0]);
                                        permutations.add([w2, w0, w1, w3]);
                                        permutations.add([w2, w0, w3, w1]);
                                        permutations.add([w2, w1, w0, w3]);
                                        permutations.add([w2, w1, w3, w0]);
                                        permutations.add([w2, w3, w0, w1]);
                                        permutations.add([w2, w3, w1, w0]);
                                        permutations.add([w3, w0, w1, w2]);
                                        permutations.add([w3, w0, w2, w1]);
                                        permutations.add([w3, w1, w0, w2]);
                                        permutations.add([w3, w1, w2, w0]);
                                        permutations.add([w3, w2, w0, w1]);
                                        permutations.add([w3, w2, w1, w0]);
                                    } else {
                                        // For 5+ words, use original order only to avoid too many combinations
                                        permutations.add(words);
                                    }
                                    
                                    // For each permutation, create combinations
                                    for (perm in permutations) {
                                        for (int i = 1; i < perm.size(); i++) {
                                            def query_words = [];
                                            def remaining_words = [];
                                            
                                            for (int k = 0; k < i; k++) {
                                                query_words.add(perm.get(k));
                                            }
                                            
                                            for (int k = i; k < perm.size(); k++) {
                                                remaining_words.add(perm.get(k));
                                            }
                                            
                                            if (query_words.size() > 0 && remaining_words.size() > 0) {
                                                def search_query = String.join(' ', query_words);
                                                def suggestion = search_query + ' ' + String.join(' ', remaining_words);
                                                combinations.add(['search_query': search_query, 'suggestion': suggestion]);
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
