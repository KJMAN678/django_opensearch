import csv
import os
from django.core.management.base import BaseCommand
from search.models import SearchLog
import datetime
from django.utils import timezone


class Command(BaseCommand):
    help = "CSVファイルから検索ログをインポートします"

    def add_arguments(self, parser):
        parser.add_argument(
            "csv_file", type=str, help="インポートするCSVファイルのパス"
        )

    def handle(self, *args, **options):
        csv_file = options["csv_file"]

        # ファイルパスの検証
        if not os.path.isfile(csv_file):
            self.stdout.write(self.style.ERROR("指定されたファイルが存在しません。"))
            return

        try:
            with open(csv_file, "r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                logs = []

                for row in reader:
                    try:
                        # タイムスタンプのパースとUNIX時間への変換
                        searched_at = timezone.make_aware(
                            datetime.datetime.strptime(
                                row["TIMESTAMP"], "%Y-%m-%d %H:%M:%S"
                            )
                        )
                        unix_timestamp = int(searched_at.timestamp())

                        logs.append(
                            SearchLog(
                                user_id=row["USER_ID"],
                                search_query=row["SEARCH_QUERY"],
                                searched_at=unix_timestamp,
                            )
                        )
                    except (ValueError, KeyError) as e:
                        self.stdout.write(
                            self.style.WARNING(
                                f"行の処理中にエラーが発生しました: {str(e)}"
                            )
                        )
                        continue

                # バルクインサートの実行
                if logs:
                    SearchLog.objects.bulk_create(logs)
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"{len(logs)}件の検索ログのインポートが完了しました"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING("インポートするデータがありませんでした。")
                    )

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR("指定されたファイルが見つかりません。"))
            return
        except PermissionError:
            self.stdout.write(
                self.style.ERROR("ファイルへのアクセス権限がありません。")
            )
            return
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"予期せぬエラーが発生しました: {str(e)}")
            )
            return
