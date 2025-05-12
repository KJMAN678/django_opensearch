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
                # "title": {
                #     "type": "text",
                #     "analyzer": "sudachi_analyzer",
                #     "fielddata": True,
                # },
                "title_suggest": {"type": "completion", "analyzer": "sudachi_analyzer"},
                # "title_aggression": {
                #     "type": "text",
                #     "fielddata": True,
                #     "analyzer": "sudachi_analyzer",
                # },
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


class RelatedSearchWordLogDocument(Document):
    """関連の検索ワードを保存・表示するためのドキュメント"""

    id = Text()
    search_query = Keyword()
    related_search_word = Keyword()
    count = Integer()

    class Meta:
        name = "related_search_word_log"
