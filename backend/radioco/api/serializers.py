from radioco.podcasts.models import PodcastEpisode, PodcastShow
from rest_framework import serializers


class PodcastShowSerializer(serializers.ModelSerializer):

    class Meta:
        model = PodcastShow
        exclude = ('rss_feed',)


class PodcastEpisodeSerializer(serializers.ModelSerializer):

    class Meta:
        model = PodcastEpisode
        fields = '__all__'
