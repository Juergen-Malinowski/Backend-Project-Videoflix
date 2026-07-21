"""Admin configuration for the Videoflix videos app."""

from django.contrib import admin, messages
from django.utils.html import format_html

from videos_app.models import Video


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
    actions = ()
    exclude = (
        'thumbnail',
    )
    readonly_fields = (
        'thumbnail_preview',
        'processing_status_help',
        'processing_status',
        'processing_error_help',
        'processing_error',
    )


    def get_readonly_fields(self, request, obj=None):
        """Return readonly fields for the video admin form."""

        readonly_fields = list(super().get_readonly_fields(request, obj))

        if obj:
            readonly_fields.append('source_file')

        return readonly_fields


    def processing_error_preview(self, video):
        """Return a shortened processing error for the admin list."""

        if not video.processing_error:
            return '-'

        if len(video.processing_error) <= 80:
            return video.processing_error

        return f'{video.processing_error[:77]}...'


    @admin.display(description='Thumbnail preview')
    def thumbnail_preview(self, video):
        """Return an HTML image preview for the generated thumbnail."""

        if not video.thumbnail:
            return '-'

        return format_html(
            '<img src="{}" style="max-width: 240px; height: auto;" />',
            video.thumbnail.url,
        )


    @admin.display(description='Processing status help')
    def processing_status_help(self, _video):
        """Return admin help text for automatic processing status."""

        return (
            'Zeigt den aktuellen Stand der automatischen Videoverarbeitung. '
            'Dieses Feld wird vom Backend gesetzt und kann nicht manuell '
            'geändert werden. Status: pending = wartet auf Verarbeitung, '
            'processing = Verarbeitung läuft, ready = erfolgreich verarbeitet '
            'und im Frontend sichtbar, failed = fehlgeschlagen. Bei failed '
            'steht die Ursache im Feld „processing error“.'
        )


    @admin.display(description='Processing error help')
    def processing_error_help(self, _video):
        """Return admin help text for automatic processing errors."""

        return (
            'Enthält die technische Fehlermeldung, falls die automatische '
            'Videoverarbeitung fehlgeschlagen ist. Dieses Feld wird vom '
            'Backend gesetzt und kann nicht manuell geändert werden.'
        )


    def save_model(self, request, obj, form, change):
        """Save the video and show automatic processing information."""

        super().save_model(request, obj, form, change)

        if not change and obj.source_file:
            self.message_user(
                request,
                self.get_automatic_processing_message(),
                level=messages.WARNING,
            )


    def get_automatic_processing_message(self):
        """Return the admin message for automatic video processing."""

        return (
            'Die automatische Videoverarbeitung wurde gestartet. '
            'Aktualisieren Sie später die Seite und prüfen Sie den Status. '
            'Wenn das Video als „failed“ erscheint, ist die Verarbeitung '
            'fehlgeschlagen. Die hochgeladene Videodatei und alle dabei '
            'erzeugten Dateien wurden automatisch bereinigt. Laden Sie das '
            'Video in diesem Fall erneut hoch. Der Videodatensatz aus der '
            'fehlgeschlagenen Verarbeitung kann bei Bedarf über den '
            'Statusfilter gesucht und manuell gelöscht werden.'
        )
