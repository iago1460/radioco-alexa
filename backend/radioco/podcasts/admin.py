from django.contrib import admin, messages
from django.conf import settings
from django.utils.html import format_html
from django.urls import resolve, reverse
from django.utils.safestring import mark_safe

from .models import (
    PodcastEpisode,
    PodcastShow,
    RSSFeed,
)
from .management.commands.importfeeds import import_feed


class RSSFeedAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_valid', 'url')
    actions = ['import_feeds', ]
    readonly_fields = ['is_valid',]
    list_filter = ['is_valid']
    search_fields = ('url', 'show__title')

    def import_feeds(self, request, queryset):
        for feed in queryset:
            self._import_feed(feed, request)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        self._import_feed(obj, request)

    def _import_feed(self, feed, request):
        feed = import_feed(feed)
        if feed.is_valid:
            self.message_user(request, f'Successfully imported {feed}.')
        else:
            self.message_user(request, f'Successfully imported {feed}.', level=messages.ERROR)


admin.site.register(RSSFeed, RSSFeedAdmin)


def get_itunes_image_preview(obj):
    if obj.pk:
        html = """<a href="{src}" target="_blank"><img src="{src}" alt="{title}" style="max-width: 200px; max-height: 200px;" /></a>"""
        return format_html(html.format(
            src=obj.itunes_image,
            title=obj.title,
        ))
    return "(No iTunes image)"


get_itunes_image_preview.short_description = "iTunes Image Preview"


def get_rss_feed(obj):
    rss_feed = obj.rss_feed
    if rss_feed:
        url = rss_feed.url
        html = f'<a href="{url}">{url}</a>'
        icon_name = 'yes' if rss_feed.is_valid else 'no'
        html += f' <img src="/static/admin/img/icon-{icon_name}.svg" alt="{rss_feed.is_valid}"/>'
        return format_html(html)


get_rss_feed.short_description = "RSS feed"


class PodcastShowAdmin(admin.ModelAdmin):
    list_display = ('title', 'created', 'modified', )
    list_filter = ('created', 'modified', )
    search_fields = ('title', )
    exclude = ('rss_feed', )
    readonly_fields = [get_rss_feed, get_itunes_image_preview]


admin.site.register(PodcastShow, PodcastShowAdmin)


class PodcastEpisodeAdmin(admin.ModelAdmin):
    list_display = ('title', 'pub_date', 'created', 'show')
    list_filter = ('pub_date', 'created')
    search_fields = ('title', 'show__title', 'show__rss_feed__url')


admin.site.register(PodcastEpisode, PodcastEpisodeAdmin)
