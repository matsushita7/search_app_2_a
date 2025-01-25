from django.core.management.base import BaseCommand
from django.core.cache import cache

class Command(BaseCommand):
    help = 'Check cache data for bestseller ranking'

    def handle(self, *args, **kwargs):
        cached_data = cache.get('bestseller_ranking')
        if cached_data:
            self.stdout.write("キャッシュデータ:")
            self.stdout.write(str(cached_data))
        else:
            self.stdout.write("キャッシュは空です")