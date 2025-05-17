from django.core.management.base import BaseCommand
from search.search_log import make_client


class Command(BaseCommand):
    help = "バックアップを復元"

    def handle(self, *args, **options):
        client = make_client()

        # まず、リポジトリを登録
        repository_settings = {
            "type": "fs",
            "settings": {
                "location": "/usr/share/opensearch/config/backup",
                "compress": True,
            },
        }

        # リポジトリ登録
        client.snapshot.create_repository(
            repository="my_backup_repo", body=repository_settings
        )

        # スナップショットのリストア
        client.snapshot.restore(
            repository="my_backup_repo",
            snapshot="snapshot_1",
            body={
                "indices": "*",  # リストアするインデックス（*は全て）
                "include_global_state": True,
                "include_aliases": True,
                # 必要に応じて追加オプション:
                # "rename_pattern": "index_(.+)",  # リネームパターン
                # "rename_replacement": "restored_index_$1",  # リネーム後のパターン
            },
            wait_for_completion=True,
        )

        print("リストアが完了しました")
