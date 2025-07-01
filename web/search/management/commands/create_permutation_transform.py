from django.core.management.base import BaseCommand
from search.search_log import make_client
import json


class Command(BaseCommand):
    help = "Create and execute permutation search transform job"

    def add_arguments(self, parser):
        parser.add_argument('--delete-existing', action='store_true', help='Delete existing transform job')
        parser.add_argument('--execute', action='store_true', help='Execute transform job after creation')

    def handle(self, *args, **options):
        client = make_client()
        job_name = "permutation_search_transform"
        target_index = "permutation_search_stats"
        
        if options['delete_existing']:
            try:
                client.transport.perform_request("DELETE", f"/_plugins/_transform/{job_name}")
                self.stdout.write(f"Deleted existing transform job: {job_name}")
            except Exception as e:
                self.stdout.write(f"No existing job to delete: {e}")

        transform_config = {
            "transform": {
                "description": "Aggregate permutation search data by original query",
                "source_index": "permutation_search_word_log",
                "target_index": target_index,
                "groups": [
                    {
                        "terms": {
                            "source_field": "original_search_query",
                            "target_field": "original_query"
                        }
                    }
                ],
                "aggregations": {
                    "total_permutations": {"value_count": {"field": "search_query"}},
                    "total_searches": {"sum": {"field": "count"}},
                    "avg_permutation_usage": {"avg": {"field": "count"}}
                },
                "schedule": {
                    "interval": {
                        "period": 1,
                        "unit": "Minutes"
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
