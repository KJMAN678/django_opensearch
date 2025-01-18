from django.core.management.base import BaseCommand
from faker import Faker
from blog.models import Blog

class Command(BaseCommand):
    help = "ダミーデータの登録"

    def add_arguments(self, parser):
        parser.add_argument('--num', nargs='?', default=1, type=int)

    def handle(self, *args, **options):
        fake = Faker("ja_JP")

        for i in range(options['num']):

            Blog.objects.create(
                title=fake.sentence(),
                content=fake.text(),
            )
