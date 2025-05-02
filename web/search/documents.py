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
                    "my_analyzer": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": ["lowercase", "asciifolding"],
                    }
                }
            }
        }
        mappings = {
            "properties": {
                "title_suggest": {"type": "completion", "analyzer": "my_analyzer"}
            }
        }
