from django.core.management.base import BaseCommand
from search.search_log import make_client
import json


class Command(BaseCommand):
    help = "Create and execute co-occurrence search transform job"

    def add_arguments(self, parser):
        parser.add_argument('--delete-existing', action='store_true', help='Delete existing transform job')
        parser.add_argument('--execute', action='store_true', help='Execute transform job after creation')

    def handle(self, *args, **options):
        client = make_client()
        job_name = "co_occurrence_search_transform"
        target_index = "search_suggestion"
        
        if options['delete_existing']:
            try:
                client.transport.perform_request("DELETE", f"/_plugins/_transform/{job_name}")
                self.stdout.write(f"Deleted existing transform job: {job_name}")
            except Exception as e:
                self.stdout.write(f"No existing job to delete: {e}")

        transform_config = {
            "transform": {
                "description": "Extract co-occurrence search patterns for suggestions",
                "source_index": "co_occurrence_search_log",
                "target_index": target_index,
                "data_selection_query": {
                    "match_all": {}
                },
                "page_size": 1000,
                "schedule": {
                    "interval": {
                        "period": 1,
                        "unit": "Minutes"
                    }
                },
                "groups": [
                    {
                        "terms": {
                            "source_field": "session_id",
                            "target_field": "session_group"
                        }
                    },
                    {
                        "terms": {
                            "source_field": "user_id", 
                            "target_field": "user_group"
                        }
                    }
                ],
                "aggregations": {
                    "search_words": {
                        "terms": {
                            "field": "search_word",
                            "size": 100
                        }
                    },
                    "word_count": {
                        "value_count": {
                            "field": "search_word"
                        }
                    }
                }
            }
        }

        try:
            response = client.transport.perform_request(
                "PUT", f"/_plugins/_transform/{job_name}", body=transform_config
            )
            self.stdout.write(f"Transform job created: {response}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to create transform job: {e}"))
            return

        if options['execute']:
            try:
                response = client.transport.perform_request(
                    "POST", f"/_plugins/_transform/{job_name}/_start"
                )
                self.stdout.write(f"Transform job started: {response}")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to start transform job: {e}"))
