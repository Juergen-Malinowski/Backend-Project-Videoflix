"""Admin configuration for the Videoflix videos app."""

from django.contrib import admin

from videos_app.models import Video


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    """Admin interface for video metadata."""

    list_display = (
        'id',
        'title',
        'category',
        'created_at',
    )
    list_filter = (
        'category',
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
