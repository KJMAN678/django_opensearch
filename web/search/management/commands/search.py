from django.core.management.base import BaseCommand
from search.search_log import make_client


class Command(BaseCommand):
    help = "インデックス作成"

    def handle(self, *args, **options):
        client = make_client()

        # データの検索
        response = client.search(
            index="blog",
            body={
                "suggest": {
                    "title_suggest": {
                        "prefix": "主婦",
                        "completion": {"field": "title_suggest", "size": 5},
                    }
                }
            },
        )
        for option in response["suggest"]["title_suggest"][0]["options"]:
            print(option["text"])
