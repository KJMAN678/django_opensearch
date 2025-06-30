from django.core.management.base import BaseCommand
from search.search_log import make_client


class Command(BaseCommand):
    help = "Clear the search_suggestion index for clean testing"

    def handle(self, *args, **options):
        client = make_client()
        
        if client.indices.exists(index='search_suggestion'):
            client.indices.delete(index='search_suggestion')
            self.stdout.write(self.style.SUCCESS('Deleted existing search_suggestion index'))
        else:
            self.stdout.write('No existing search_suggestion index found')
