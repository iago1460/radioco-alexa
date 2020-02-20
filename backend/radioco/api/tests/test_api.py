import datetime

import pytest

from radioco.podcasts.models import PodcastShow, PodcastEpisode, RSSFeed
from django.utils import timezone

FIRST = 1
LAST = -1


@pytest.fixture()
@pytest.mark.django_db()
def shows():
    episode_kwargs = {'pub_date': timezone.now()}
    rss_feed = RSSFeed.objects.create(url='http://fake.com/1')
    show = PodcastShow.objects.create(title='normal show', rss_feed=rss_feed)

    PodcastEpisode.objects.create(show=show, season=1, episode=1, **episode_kwargs)
    PodcastEpisode.objects.create(show=show, season=1, episode=2, **episode_kwargs)
    PodcastEpisode.objects.create(show=show, season=1, episode=3, **episode_kwargs)

    PodcastEpisode.objects.create(show=show, season=2, episode=1, **episode_kwargs)
    PodcastEpisode.objects.create(show=show, season=2, episode=2, **episode_kwargs)
    PodcastEpisode.objects.create(show=show, season=2, episode=3, **episode_kwargs)

    rss_feed = RSSFeed.objects.create(url='http://fake.com/2')
    show = PodcastShow.objects.create(title='season 6 only', rss_feed=rss_feed)
    PodcastEpisode.objects.create(show=show, season=6, episode=1, **episode_kwargs)
    PodcastEpisode.objects.create(show=show, season=6, episode=2, **episode_kwargs)
    PodcastEpisode.objects.create(show=show, season=6, episode=3, **episode_kwargs)

    rss_feed = RSSFeed.objects.create(url='http://fake.com/3')
    show = PodcastShow.objects.create(title='episode per season', rss_feed=rss_feed)
    PodcastEpisode.objects.create(show=show, season=1, episode=1, **episode_kwargs)
    PodcastEpisode.objects.create(show=show, season=2, episode=1, **episode_kwargs)
    PodcastEpisode.objects.create(show=show, season=3, episode=1, **episode_kwargs)


@pytest.mark.django_db()
@pytest.mark.parametrize('query, expected', [
    (
        dict(),
        {
            'normal show': dict(season=2, episode=3),
            'season 6 only': dict(season=6, episode=3),
            'episode per season': dict(season=3, episode=1),
        }
    ),
    (
        dict(season=FIRST),
        {
            'normal show': dict(season=1, episode=1),
            'season 6 only': None,
            'episode per season': dict(season=1, episode=1),
        }
    ),
    (
        dict(season=2),
        {
            'normal show': dict(season=2, episode=1),
            'season 6 only': None,
            'episode per season': dict(season=2, episode=1),
        }
    ),
    (
        dict(season=LAST),
        {
            'normal show': dict(season=2, episode=1),
            'season 6 only': dict(season=6, episode=1),
            'episode per season': dict(season=3, episode=1),
        }
    ),
    (
        dict(episode=FIRST),
        {
            'normal show': dict(season=1, episode=1),
            'season 6 only': dict(season=6, episode=1),
            'episode per season': dict(season=1, episode=1),
        }
    ),
    (
        dict(episode=2),
        {
            'normal show': dict(season=1, episode=2),
            'season 6 only': dict(season=6, episode=2),
            'episode per season': dict(season=2, episode=1),
        }
    ),
    (
        dict(episode=LAST),
        {
            'normal show': dict(season=2, episode=3),
            'season 6 only': dict(season=6, episode=3),
            'episode per season': dict(season=3, episode=1),
        }
    ),
    (
        dict(season=FIRST, episode=FIRST),
        {
            'normal show': dict(season=1, episode=1),
            'season 6 only': None,
            'episode per season': dict(season=1, episode=1),
        }
    ),
    (
        dict(season=2, episode=FIRST),
        {
            'normal show': dict(season=2, episode=1),
            'season 6 only': None,
            'episode per season': dict(season=2, episode=1),
        }
    ),
    (
        dict(season=FIRST, episode=2),
        {
            'normal show': dict(season=1, episode=2),
            'season 6 only': None,
            'episode per season': None,
        }
    ),
    (
        dict(season=FIRST, episode=LAST),
        {
            'normal show': dict(season=1, episode=3),
            'season 6 only': None,
            'episode per season': dict(season=1, episode=1),
        }
    ),
    (
        dict(season=2, episode=LAST),
        {
            'normal show': dict(season=2, episode=3),
            'season 6 only': None,
            'episode per season': dict(season=2, episode=1),
        }
    ),
    (
        dict(season=LAST, episode=FIRST),
        {
            'normal show': dict(season=2, episode=1),
            'season 6 only': dict(season=6, episode=1),
            'episode per season': dict(season=3, episode=1),
        }
    ),
    (
        dict(season=LAST, episode=2),
        {
            'normal show': dict(season=2, episode=2),
            'season 6 only': dict(season=6, episode=2),
            'episode per season': None,
        }
    ),
    (
        dict(season=LAST, episode=LAST),
        {
            'normal show': dict(season=2, episode=3),
            'season 6 only': dict(season=6, episode=3),
            'episode per season': dict(season=3, episode=1),
        }
    ),
    (
        dict(season=2, episode=2),
        {
            'normal show': dict(season=2, episode=2),
            'season 6 only': None,
            'episode per season': None,
        }
    ),
])
def test_order(query, expected, client, shows):
    for show_title, expected_data in expected.items():
        show = PodcastShow.objects.get(title=show_title)
        query['show_id'] = show.id
        response = client.get(f'http://testserver/api/alexa/', query)
        if response.status_code == 404:
            assert expected_data is None
        else:
            assert expected_data
            data = response.json()
            assert data['show'] == show.id
            assert data['season'] == expected_data['season']
            assert data['episode'] == expected_data['episode']
