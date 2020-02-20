import logging

from django.db import models
from django.utils.text import slugify
from model_utils.models import TimeStampedModel


class RSSFeed(TimeStampedModel):
    url = models.URLField(help_text='URL of a Podcast RSS feed to ingest', unique=True, max_length=255)
    is_valid = models.BooleanField(help_text='Indicates if the feed has been successfully parsed.', default=False)
    # station = models.ForeignKey(Station, on_delete=models.CASCADE)

    @property
    def name(self):
        try:
            return self.show.title or self.url
        except PodcastShow.DoesNotExist:
            return self.url

    def __str__(self):
        return self.name


class PodcastShow(TimeStampedModel):
    # RSS 2.0
    title = models.CharField(max_length=255, blank=True)

    description = models.TextField(help_text='Describe subject matter, media format, episode schedule and other relevant information while incorporating keywords.', blank=True)

    rss_feed = models.OneToOneField(RSSFeed, related_name='show', on_delete=models.CASCADE)

    # Optional
    language = models.CharField(max_length=7, help_text='See <a href="http://en.wikipedia.org/wiki/List_of_ISO_639-1_codes">ISO 639-1</a> and <a href="http://en.wikipedia.org/wiki/ISO_3166-1_alpha-2#Officially_assigned_code_elements">ISO 3166-1</a> for more language codes.', blank=True)

    image_url = models.URLField(help_text='Artwork must be a minimum size of 1400 x 1400 pixels and a maximum size of 3000 x 3000 pixels, in JPEG or PNG format, 72 dpi, with appropriate file extensions (.jpg, .png), and in the RGB colorspace.', blank=True, max_length=500)
    # TODO: itunes:owner

    def __str__(self):
        return self.title


class PodcastEpisode(TimeStampedModel):
    guid = models.CharField(max_length=255, blank=True, db_index=True)
    show = models.ForeignKey(PodcastShow, on_delete=models.CASCADE, related_name='episodes')

    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(default='', blank=True)
    author = models.CharField(max_length=255, blank=True)
    duration = models.DurationField(null=True, blank=True, help_text='The episode duration in hours, minutes, and seconds.')

    image_url = models.URLField(help_text='Artwork must be a minimum size of 1400 x 1400 pixels and a maximum size of 3000 x 3000 pixels, in JPEG or PNG format, 72 dpi, with appropriate file extensions (.jpg, .png), and in the RGB colorspace.', blank=True, max_length=500)

    season = models.PositiveIntegerField(null=True, blank=True, help_text='The episode season number.')
    episode = models.PositiveIntegerField(null=True, blank=True, help_text='The episode season number.')

    pub_date = models.DateTimeField(db_index=True)
    stream_url = models.URLField(max_length=500)

    def __str__(self):
        if self.episode and self.season:
            return f'{self.episode}x{self.season} - {self.title}'
        return f'{self.title}'


ATOM_TO_RSS = {
    'feed': 'channel',
    'rights': 'copyright',
    'subtitle': '',
    'content': 'description',
    'summary': 'description',
    'id': 'guid',
    'logo': 'image',
    'entry': 'item',
    'updated': 'lastBuildDate',
    'author': 'managingEditor',
    'contributor': 'managingEditor',
    'published': 'pubDate',
    'ttl': '',
}

