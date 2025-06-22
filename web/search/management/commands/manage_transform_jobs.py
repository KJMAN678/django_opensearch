from django.core.management.base import BaseCommand
from search.search_log import make_client
import json


class Command(BaseCommand):
    help = "Manage transform jobs (list, start, stop, delete)"

    def add_arguments(self, parser):
        parser.add_argument(
            "action",
            choices=["list", "start", "stop", "delete", "status"],
            help="Action to perform on transform jobs",
        )
        parser.add_argument(
            "--job-name",
            help="Transform job name (required for start, stop, delete, status actions)",
        )

    def handle(self, *args, **options):
        client = make_client()
        action = options["action"]
        job_name = options.get("job_name")

        if action in ["start", "stop", "delete", "status"] and not job_name:
            self.stdout.write(
                self.style.ERROR(f"アクション '{action}' にはjob-nameパラメータが必要です。")
            )
            return

        try:
            if action == "list":
                self.list_transform_jobs(client)
            elif action == "start":
                self.start_transform_job(client, job_name)
            elif action == "stop":
                self.stop_transform_job(client, job_name)
            elif action == "delete":
                self.delete_transform_job(client, job_name)
            elif action == "status":
                self.get_transform_status(client, job_name)

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"操作中にエラーが発生しました: {e}"))

    def list_transform_jobs(self, client):
        try:
            response = client.transport.perform_request("GET", "/_plugins/_transform")
            
            if "transforms" in response and response["transforms"]:
                self.stdout.write("=== Transform Jobs一覧 ===")
                for transform in response["transforms"]:
                    transform_id = transform.get("_id", "N/A")
                    status = transform.get("status", "N/A")
                    source_index = transform.get("source_index", "N/A")
                    target_index = transform.get("target_index", "N/A")
                    
                    self.stdout.write(f"\nJob ID: {transform_id}")
                    self.stdout.write(f"ステータス: {status}")
                    self.stdout.write(f"ソースインデックス: {source_index}")
                    self.stdout.write(f"ターゲットインデックス: {target_index}")
                    self.stdout.write("-" * 40)
            else:
                self.stdout.write("Transform jobが見つかりませんでした。")
                
        except Exception as e:
            if "index_not_found_exception" in str(e):
                self.stdout.write("Transform jobが見つかりませんでした。")
            else:
                raise e

    def start_transform_job(self, client, job_name):
        response = client.transport.perform_request(
            "POST", f"/_plugins/_transform/{job_name}/_start"
        )
        self.stdout.write(
            self.style.SUCCESS(f"Transform job '{job_name}' を開始しました。")
        )
        self.stdout.write(f"レスポンス: {json.dumps(response, indent=2, ensure_ascii=False)}")

    def stop_transform_job(self, client, job_name):
        response = client.transport.perform_request(
            "POST", f"/_plugins/_transform/{job_name}/_stop"
        )
        self.stdout.write(
            self.style.SUCCESS(f"Transform job '{job_name}' を停止しました。")
        )
        self.stdout.write(f"レスポンス: {json.dumps(response, indent=2, ensure_ascii=False)}")

    def delete_transform_job(self, client, job_name):
        response = client.transport.perform_request(
            "DELETE", f"/_plugins/_transform/{job_name}"
        )
        self.stdout.write(
            self.style.SUCCESS(f"Transform job '{job_name}' を削除しました。")
        )
        self.stdout.write(f"レスポンス: {json.dumps(response, indent=2, ensure_ascii=False)}")

    def get_transform_status(self, client, job_name):
        response = client.transport.perform_request(
            "GET", f"/_plugins/_transform/{job_name}"
        )
        self.stdout.write(f"=== Transform Job '{job_name}' ステータス ===")
        self.stdout.write(json.dumps(response, indent=2, ensure_ascii=False))
