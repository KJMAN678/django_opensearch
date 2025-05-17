from django.core.management.base import BaseCommand
from search.documents import BlogDocument
from blog.models import Blog
from search.search_log import make_client


class Command(BaseCommand):
    help = "インデックス作成"

    def handle(self, *args, **options):
        client = make_client()

        if client.indices.exists(index="past_search_log"):
            client.indices.delete(index="past_search_log")

        if client.indices.exists(index="blog"):
            client.indices.delete(index="blog")

        # インデックスを作成
        BlogDocument.init(using=client, index="blog")

        blogs = Blog.objects.all()
        for blog in blogs:
            doc = BlogDocument(
                id=blog.id,
                title=blog.title,
                title_suggest={"input": blog.title},
                title_aggression=blog.title,
                content=blog.content,
            )
            doc.save(using=client, index="blog")
