from django.core.management.base import BaseCommand
from samapp.utils import update_bestseller_ranking

class Command(BaseCommand):
    help = 'Update bestseller ranking'

    def handle(self, *args, **kwargs):
        update_bestseller_ranking()
        self.stdout.write(self.style.SUCCESS('Successfully updated bestseller ranking'))