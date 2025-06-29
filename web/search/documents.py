from opensearchpy import Document, Text, Completion, Date, Keyword, Integer


class BlogDocument(Document):
    id = Keyword()  # Changed to Keyword for aggregations
    title = Text()
    title_suggest = Completion()
    content = Text()
    title_aggression = Text(
        fielddata=True,
        analyzer="sudachi",
    )
    created_at = Date()
    updated_at = Date()
    # title_aggression = Keyword()

    class Meta:
        name = "blog"
        settings = {
            "analysis": {
                "analyzer": {
                    "sudachi_analyzer": {
                        "type": "custom",
                        "tokenizer": "sudachi_tokenizer",
                        "mode": "search",
                        "char_filter": ["icu_normalizer"],
                        "filter": [
                            "sudachi_baseform",
                            "sudachi_part_of_speech",
                            "cjk_width",
                            "lowercase",
                            "sudachi_readingform",
                            "sudachi_normalizedform",
                        ],
                    }
                }
            }
        }
        mappings = {
            "properties": {
                "title_suggest": {"type": "completion", "analyzer": "sudachi_analyzer"},
            }
        }


class PastSearchLogDocument(Document):
    """そのユーザーの過去の検索ログを保存・表示するためのドキュメント"""

    id = Text()
    user_id = Text()
    search_word = Keyword()
    created_at = Date()

    class Meta:
        name = "past_search_log"


class AggPastSearchLogDocument(Document):
    """集計対象にするための検索ログを保存するためのドキュメント"""

    id = Text()
    user_id = Text()
    search_original_word = Keyword()
    related_search_word = Keyword()
    search_word = Keyword()
    created_at = Date()

    class Meta:
        name = "agg_past_search_log"


class RelatedSearchWordLogDocument(Document):
    """関連の検索ワードを保存・表示するためのドキュメント"""

    id = Text()
    search_query = Keyword()
    related_search_word = Keyword()
    count = Integer()

    class Meta:
        name = "related_search_word_log"


class NoOrderRelatedSearchWordLogDocument(Document):
    """ワードの順番を考慮しない、関連の検索ワードを保存・表示するためのドキュメント"""

    id = Text()
    search_query = Keyword()
    related_search_word = Keyword()
    count = Integer()

    class Meta:
        name = "no_order_related_search_word_log"


class SearchLogDocument(Document):
    """検索ログを保存するためのドキュメント"""

    id = Text()
    user_id = Keyword()
    search_query = Keyword()
    searched_at = Date()

    class Meta:
        name = "search_log"
        settings = {
            "analysis": {
                "analyzer": {
                    "sudachi_analyzer": {
                        "type": "custom",
                        "tokenizer": "sudachi_tokenizer",
                        "mode": "search",
                        "char_filter": ["icu_normalizer"],
                        "filter": [
                            "sudachi_baseform",
                            "sudachi_part_of_speech",
                            "lowercase",
                            "sudachi_readingform",
                        ],
                    }
                }
            }
        }


class BlogTransformDocument(Document):
    """ブログデータの変換結果を保存するためのドキュメント"""

    date_key = Keyword()
    blog_count = Integer()
    avg_content_length = Integer()
    total_content_length = Integer()
    avg_title_length = Integer()
    total_title_length = Integer()

    class Meta:
        name = "blog_transform"


class PermutationSearchWordLogDocument(Document):
    """順列を考慮した関連検索ワードを保存・表示するためのドキュメント"""
    
    id = Text()
    original_search_query = Keyword()
    search_query = Keyword()
    related_search_word = Keyword()
    permutation_order = Integer()
    count = Integer()
    
    class Meta:
        name = "permutation_search_word_log"
