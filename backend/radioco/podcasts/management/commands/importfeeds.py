import logging
import time

import feedparser
from django.conf import settings
from django.core.management.base import BaseCommand
from radioco.podcasts.models import PodcastShow, PodcastEpisode, RSSFeed

from radioco.podcasts.utils import parse_date, parse_duration, parse_title


SLEEP_DURATION_SECONDS = 60 * 10

logger = logging.getLogger(__name__)


def import_feed(rss_feed):
    rss_url = rss_feed.url
    feed_data = feedparser.parse(rss_url)

    show, created = PodcastShow.objects.update_or_create(
        rss_feed=rss_feed,
        defaults={
            'title': feed_data['feed']['title'],
            'language': feed_data['feed'].get('language'),
            'description': feed_data['feed'].get('description') or
                           feed_data['feed'].get('summary'),
            'image_url': feed_data['feed'].get('image', {'href': None})['href'],
        },
    )
    if created:
        logger.info(f'Created "{show}"')

    show_episodes = feed_data.entries

    processed_episode_ids = []
    for episode in show_episodes:
        podcast_episode, created = PodcastEpisode.objects.update_or_create(
            guid=episode.get('guid') or episode['link'],
            defaults={
                **parse_title(episode.title),
                'pub_date': parse_date(episode.published),
                'description': episode.description,  # FIXME: itunes_summary
                'image_url': feed_data['feed'].get('image', {'href': None})['href'],
                'duration': parse_duration(episode['itunes_duration']),
                'stream_url': [link['href'] for link in episode.links if link['rel'] == 'enclosure'][0],
                'show': show,
            }
        )
        processed_episode_ids.append(podcast_episode.id)

    num_deleted_episodes, _ = PodcastEpisode.objects.filter(show=show).exclude(id__in=processed_episode_ids).delete()
    if num_deleted_episodes:
        logger.info(
            f'Deleted {num_deleted_episodes} episodes from show "{show}", ID: {show.id}'
        )
    if not show.episodes.exists():
        logger.info(
            f'Deleted "{show}", ID: {show.id}'
        )
        show.delete()


def import_feeds():
    for rss_feed in RSSFeed.objects.all().select_related('show'):
        import_feed(rss_feed)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--daemon',
            action='store_true',
            dest='daemon',
            help='Run the import command as a daemon',
        )

    def handle(self, *args, **options):
        import_feeds()

        if options['daemon']:
            while True:
                time.sleep(SLEEP_DURATION_SECONDS)
                import_feeds()
