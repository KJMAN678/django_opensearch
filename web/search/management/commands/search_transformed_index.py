from django.core.management.base import BaseCommand
from search.search_log import make_client
import json


class Command(BaseCommand):
    help = "Search and display data from transformed index"

    def add_arguments(self, parser):
        parser.add_argument(
            "--index",
            default="blog_monthly_stats",
            help="Transformed index name to search",
        )
        parser.add_argument(
            "--size",
            type=int,
            default=10,
            help="Number of results to return",
        )

    def handle(self, *args, **options):
        client = make_client()
        index_name = options["index"]
        size = options["size"]

        if not client.indices.exists(index=index_name):
            self.stdout.write(
                self.style.ERROR(f"インデックス '{index_name}' が存在しません。")
            )
            return

        try:
            count_response = client.count(index=index_name)
            total_docs = count_response["count"]
            self.stdout.write(f"インデックス '{index_name}' に {total_docs} 件のドキュメントがあります。")

            if total_docs == 0:
                self.stdout.write("検索結果がありません。")
                return

            search_response = client.search(
                index=index_name,
                body={
                    "query": {"match_all": {}},
                    "size": size,
                    "sort": [{"date_key": {"order": "desc"}}],
                },
            )

            self.stdout.write("\n=== 変換されたインデックスの検索結果 ===")
            for hit in search_response["hits"]["hits"]:
                source = hit["_source"]
                self.stdout.write(f"\n日付: {source.get('date_key', 'N/A')}")
                self.stdout.write(f"ブログ投稿数: {source.get('blog_count', 0)}")
                self.stdout.write(f"平均コンテンツ長: {source.get('avg_content_length', 0):.1f}")
                self.stdout.write(f"総コンテンツ長: {source.get('total_content_length', 0)}")
                self.stdout.write(f"平均タイトル長: {source.get('avg_title_length', 0):.1f}")
                self.stdout.write(f"総タイトル長: {source.get('total_title_length', 0)}")
                self.stdout.write("-" * 40)

            mapping_response = client.indices.get_mapping(index=index_name)
            self.stdout.write(f"\n=== インデックスマッピング ===")
            self.stdout.write(json.dumps(mapping_response, indent=2, ensure_ascii=False))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"検索中にエラーが発生しました: {e}"))
