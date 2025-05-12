from django.core.management.base import BaseCommand
from opensearchpy import OpenSearch
import environ
from search.documents import BlogDocument
from blog.models import Blog


class Command(BaseCommand):
    help = "インデックス作成"

    def handle(self, *args, **options):
        host = "opensearch"
        port = 9200

        env = environ.Env()
        environ.Env.read_env(".env")
        OPENSEARCH_INITIAL_ADMIN_PASSWORD = env("OPENSEARCH_INITIAL_ADMIN_PASSWORD")
        auth = ("admin", OPENSEARCH_INITIAL_ADMIN_PASSWORD)

        client = OpenSearch(
            hosts=[{"host": host, "port": port}],
            http_auth=auth,
            use_ssl=True,
            verify_certs=False,
            ssl_assert_hostname=False,
            ssl_show_warn=False,
        )

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
