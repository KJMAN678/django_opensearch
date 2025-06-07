import uuid
from django.core.management.base import BaseCommand
from search.models import SearchLog
from search.search_log import make_client
from search.documents import SearchLogDocument


class Command(BaseCommand):
    help = "SearchLogモデルの内容をOpenSearchの検索インデックスに登録します"

    def handle(self, *args, **options):
        client = make_client()

        # インデックスがなければ作成
        if not client.indices.exists(index="search_log"):
            SearchLogDocument.init(using=client, index="search_log")

        logs = SearchLog.objects.all()
        count = 0
        for log in logs:
            doc = SearchLogDocument(
                id=str(uuid.uuid4()),
                user_id=log.user_id,
                search_query=log.search_query,
                searched_at=log.searched_at,
            )
            doc.save(using=client, index="search_log")
            count += 1

        self.stdout.write(
            self.style.SUCCESS(f"{count}件の検索ログをOpenSearchに登録しました")
        )
