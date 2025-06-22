from django.core.management.base import BaseCommand
from search.search_log import make_client
from search.documents import BlogTransformDocument
import json
import time


class Command(BaseCommand):
    help = "Create and execute index transform job for blog data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--job-name",
            default="blog_monthly_transform",
            help="Transform job name",
        )
        parser.add_argument(
            "--target-index",
            default="blog_monthly_stats",
            help="Target index name",
        )
        parser.add_argument(
            "--execute",
            action="store_true",
            help="Execute the transform job immediately",
        )
        parser.add_argument(
            "--delete-existing",
            action="store_true",
            help="Delete existing transform job and target index",
        )

    def handle(self, *args, **options):
        client = make_client()
        job_name = options["job_name"]
        target_index = options["target_index"]

        if options["delete_existing"]:
            self.delete_existing_resources(client, job_name, target_index)

        if not client.indices.exists(index="blog"):
            self.stdout.write(
                self.style.ERROR("ソースインデックス 'blog' が存在しません。先にinit_indexコマンドを実行してください。")
            )
            return

        blog_count = client.count(index="blog")["count"]
        if blog_count == 0:
            self.stdout.write(
                self.style.ERROR("ソースインデックス 'blog' にデータがありません。")
            )
            return

        self.stdout.write(f"ソースインデックス 'blog' に {blog_count} 件のドキュメントが見つかりました。")

        import time
        current_time = int(time.time())
        
        transform_config = {
            "transform": {
                "enabled": True,
                "continuous": False,
                "schedule": {
                    "interval": {
                        "period": 1,
                        "unit": "Minutes",
                        "start_time": current_time
                    }
                },
                "description": "ブログデータを月別に集約するTransform job",
                "source_index": "blog",
                "target_index": target_index,
                "data_selection_query": {"match_all": {}},
                "page_size": 1000,
                "groups": [
                    {
                        "date_histogram": {
                            "source_field": "created_at",
                            "calendar_interval": "1M",
                            "format": "yyyy-MM",
                            "target_field": "date_key"
                        }
                    }
                ],
                "aggregations": {
                    "blog_count": {"value_count": {"field": "id"}}
                }
            }
        }

        try:
            response = client.transport.perform_request(
                "PUT", f"/_plugins/_transform/{job_name}", body=transform_config
            )
            self.stdout.write(
                self.style.SUCCESS(f"Transform job '{job_name}' を作成しました。")
            )
            self.stdout.write(f"レスポンス: {json.dumps(response, indent=2, ensure_ascii=False)}")

            if options["execute"]:
                self.execute_transform_job(client, job_name, target_index)

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Transform job作成中にエラーが発生しました: {e}"))

    def delete_existing_resources(self, client, job_name, target_index):
        try:
            client.transport.perform_request("DELETE", f"/_plugins/_transform/{job_name}")
            self.stdout.write(f"既存のTransform job '{job_name}' を削除しました。")
        except Exception:
            pass

        try:
            if client.indices.exists(index=target_index):
                client.indices.delete(index=target_index)
                self.stdout.write(f"既存のターゲットインデックス '{target_index}' を削除しました。")
        except Exception:
            pass

    def execute_transform_job(self, client, job_name, target_index):
        try:
            response = client.transport.perform_request(
                "POST", f"/_plugins/_transform/{job_name}/_start"
            )
            self.stdout.write(
                self.style.SUCCESS(f"Transform job '{job_name}' を開始しました。")
            )

            self.stdout.write("Transform jobの実行状況を監視中...")
            max_wait_time = 60
            wait_time = 0
            
            while wait_time < max_wait_time:
                try:
                    status_response = client.transport.perform_request(
                        "GET", f"/_plugins/_transform/{job_name}"
                    )
                    
                    if "transform" in status_response:
                        transform_status = status_response["transform"]
                        status = transform_status.get("status", "unknown")
                        self.stdout.write(f"現在のステータス: {status}")
                        
                        if status == "finished":
                            self.stdout.write(
                                self.style.SUCCESS("Transform jobが正常に完了しました！")
                            )
                            break
                        elif status == "failed":
                            self.stdout.write(
                                self.style.ERROR("Transform jobが失敗しました。")
                            )
                            break
                    
                    time.sleep(5)
                    wait_time += 5
                    
                except Exception as e:
                    self.stdout.write(f"ステータス確認中にエラー: {e}")
                    break

            if client.indices.exists(index=target_index):
                count = client.count(index=target_index)["count"]
                self.stdout.write(
                    self.style.SUCCESS(f"ターゲットインデックス '{target_index}' に {count} 件のドキュメントが作成されました。")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"ターゲットインデックス '{target_index}' がまだ作成されていません。")
                )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Transform job実行中にエラーが発生しました: {e}"))
