import django_filters
from radioco.podcasts.models import PodcastEpisode, PodcastShow


class PodcastShowFilter(django_filters.FilterSet):
    station_id = django_filters.UUIDFilter(label='station_id', method='rss_feed_proxy_filter')

    def rss_feed_proxy_filter(self, queryset, name, value):
        return queryset.filter(**{
            f'rss_feed__{name}': value,
        })

    class Meta:
        model = PodcastShow
        fields = ('station_id',)


class PodcastEpisodeFilter(django_filters.FilterSet):
    pub_date__gt = django_filters.IsoDateTimeFilter(field_name='pub_date', lookup_expr='gt')
    pub_date__lt = django_filters.IsoDateTimeFilter(field_name='pub_date', lookup_expr='lt')
    pub_date__gte = django_filters.IsoDateTimeFilter(field_name='pub_date', lookup_expr='gte')
    pub_date__lte = django_filters.IsoDateTimeFilter(field_name='pub_date', lookup_expr='lte')
    created__gt = django_filters.IsoDateTimeFilter(field_name='created', lookup_expr='gt')
    created__lt = django_filters.IsoDateTimeFilter(field_name='created', lookup_expr='lt')
    created__gte = django_filters.IsoDateTimeFilter(field_name='created', lookup_expr='gte')
    created__lte = django_filters.IsoDateTimeFilter(field_name='created', lookup_expr='lte')

    class Meta:
        model = PodcastEpisode
        fields = {
            'pub_date': ['lt', 'gt', 'lte', 'gte'],
            'created': ['lt', 'gt', 'lte', 'gte'],
            'show': ['exact'],
        }
