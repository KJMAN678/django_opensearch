from django.core.management.base import BaseCommand
from search.search_log import make_client


class Command(BaseCommand):
    help = "バックアップ作成"

    def handle(self, *args, **options):
        client = make_client()
        repository_settings = {
            "type": "fs",
            "settings": {
                "location": "/usr/share/opensearch/config/backup",  # バックアップ先のディレクトリパス
                "compress": True,
            },
        }

        # リポジトリ登録
        client.snapshot.create_repository(
            repository="my_backup_repo", body=repository_settings
        )

        # スナップショット作成（全インデックスのバックアップ）
        client.snapshot.create(
            repository="my_backup_repo",
            snapshot="snapshot_1",
            body={
                "indices": "*",  # バックアップするインデックス（*は全て）
                "include_global_state": True,  # クラスター設定も含める
            },
            wait_for_completion=True,  # スナップショット完了まで待機
        )
        print("バックアップが完了しました")
