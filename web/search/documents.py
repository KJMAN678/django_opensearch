from opensearchpy import Document, Text, Completion, Date, Keyword, Integer


class BlogDocument(Document):
    id = Text()
    title = Text()
    title_suggest = Completion()
    content = Text()
    title_aggression = Text(
        fielddata=True,
        analyzer="sudachi",
    )
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
    searched_at = Integer()  # UNIX時間（エポック秒）

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
