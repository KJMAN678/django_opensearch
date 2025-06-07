import csv
from django.core.management.base import BaseCommand
from search.models import SearchLog
import datetime


class Command(BaseCommand):
    help = "CSVファイルから検索ログをインポートします"

    def add_arguments(self, parser):
        parser.add_argument(
            "csv_file", type=str, help="インポートするCSVファイルのパス"
        )

    def handle(self, *args, **options):
        csv_file = options["csv_file"]

        with open(csv_file, "r", encoding="utf-8-sig") as f:  # UTF-8-BOM対応
            reader = csv.DictReader(f)
            for row in reader:
                # タイムスタンプのパース
                timestamp = datetime.datetime.strptime(
                    row["TIMESTAMP"], "%Y-%m-%d %H:%M:%S"
                )

                SearchLog.objects.create(
                    user_id=row["USER_ID"],
                    search_query=row["ITEM_ID"],
                    timestamp=timestamp,
                )

        self.stdout.write(self.style.SUCCESS("検索ログのインポートが完了しました"))
