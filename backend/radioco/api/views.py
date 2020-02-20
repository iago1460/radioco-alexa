from django_filters.rest_framework import DjangoFilterBackend
from radioco.podcasts.models import PodcastShow, PodcastEpisode
from rest_framework import filters, viewsets
from rest_framework.decorators import api_view
from rest_framework.exceptions import ParseError, NotFound
from rest_framework.response import Response


from .filters import (
    PodcastEpisodeFilter,
    PodcastShowFilter,
)
from .serializers import (
    PodcastShowSerializer,
    PodcastEpisodeSerializer,
)


class PodcastShowViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PodcastShow.objects.select_related('rss_feed')
    serializer_class = PodcastShowSerializer
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    filter_class = PodcastShowFilter
    search_fields = ('title', 'description')


class PodcastEpisodeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PodcastEpisode.objects.all().order_by('-pub_date')
    serializer_class = PodcastEpisodeSerializer
    filter_class = PodcastEpisodeFilter
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('title', 'description')
    ordering_fields = ('pub_date', 'created')


@api_view()
def alexa_view(request):
    params = {
        'show_id': None,
        'season': None,
        'episode': None,
        # 'station': None,
    }
    for key in params:
        params[key] = request.query_params.get(key)

    try:
        params['show_id'] = int(params['show_id'])
        params['season'] = int(params['season']) if params['season'] else 0
        params['episode'] = int(params['episode']) if params['episode'] else 0
    # except (TypeError, ValueError) as e:
    except IndexError as e:
        raise ParseError(f'Error: {e}')

    filter_fields = {'show_id': params['show_id']}
    order_by_fields = ['season', 'episode']

    if params['episode'] > 1:
        filter_fields['episode'] = params['episode']
    if params['season'] > 0:
        filter_fields['season'] = params['season']

    if not params['episode'] and not params['season']:
        order_by_fields = ['-season', '-episode']
    elif params['season'] == -1 and params['episode'] == -1:
        # Last episode of last season
        order_by_fields = ['-season', '-episode']
    elif params['season'] == -1:
        # Last season
        order_by_fields = ['-season', 'episode']
    elif params['season'] == 1 and params['episode'] == -1:
        # Last episode of first season
        order_by_fields = ['season', '-episode']
    elif params['episode'] == -1:
        # Last episode
        order_by_fields = ['-season', '-episode']

    episode = PodcastEpisode.objects.filter(**filter_fields).order_by(*order_by_fields).first()
    if not episode and params['episode'] > 1 and not params['season']:
        # Assume user wants the x episode in order
        try:
            episode = PodcastEpisode.objects.filter(
                show_id=params['show_id']
            ).order_by('season', 'episode')[params['episode'] - 1]
        except IndexError:
            pass
    if episode:
        serializer = PodcastEpisodeSerializer(episode)
        return Response(serializer.data)

    raise NotFound
