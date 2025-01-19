from opensearchpy import Document, Text


class BlogDocument(Document):
    id = Text()
    title = Text()
    content = Text()

    class Meta:
        name = "blog"
