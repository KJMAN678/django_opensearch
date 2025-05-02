from opensearchpy import Document, Text, Completion


class BlogDocument(Document):
    id = Text()
    title = Text()
    title_suggest = Completion()
    content = Text()

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
                "title_suggest": {"type": "completion", "analyzer": "sudachi_analyzer"}
            }
        }
