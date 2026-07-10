"""Admin configuration for the Videoflix videos app."""

from django.contrib import admin

from videos_app.models import Video
from videos_app.tasks import convert_video_to_hls


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    """Admin interface for video metadata and processing."""

    list_display = (
        'id',
        'title',
        'category',
        'created_at',
        'processing_status',
        'processing_error_preview',
    )
    list_filter = (
        'category',
        'processing_status',
        'created_at',
    )
    search_fields = (
        'title',
        'description',
        'category',
    )
    ordering = (
        '-created_at',
    )
    actions = (
        'convert_selected_videos_to_hls',
        'retry_failed_hls_conversions',
    )


    def processing_error_preview(self, video):
        """Return a shortened processing error for the admin list."""

        if not video.processing_error:
            return '-'

        if len(video.processing_error) <= 80:
            return video.processing_error

        return f'{video.processing_error[:77]}...'


    def convert_selected_videos_to_hls(self, request, queryset):
        """Start HLS conversion tasks for selected videos."""

        for video in queryset:
            convert_video_to_hls.delay(video.id)


    def retry_failed_hls_conversions(self, request, queryset):
        """Restart HLS conversion tasks for selected failed videos."""

        failed_videos = queryset.filter(
            processing_status=Video.STATUS_FAILED,
        )

        for video in failed_videos:
            convert_video_to_hls.delay(video.id)
