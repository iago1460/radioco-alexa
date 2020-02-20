import requests
from django.core.management.base import BaseCommand

from radioco.podcasts.models import RSSFeed


class Command(BaseCommand):

    def handle(self, *args, **options):
        response = requests.get('https://cuacfm.org/radioco/api/2/programmes')
        response.raise_for_status()
        for show in response.json():
            RSSFeed.objects.get_or_create(url=show['rss_url'])
