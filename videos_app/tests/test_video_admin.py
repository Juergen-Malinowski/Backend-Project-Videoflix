"""Tests for the Videoflix video admin configuration."""

from unittest.mock import patch

import pytest

from django.contrib import admin
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.files.base import ContentFile
from django.test import RequestFactory

from videos_app.admin import VideoAdmin
from videos_app.models import Video


@pytest.mark.django_db
class TestVideoAdmin:
    """Test Django admin configuration for videos."""

    def setup_method(self):
        """Prepare reusable admin test objects."""

        self.site = admin.AdminSite()
        self.video_admin = VideoAdmin(Video, self.site)
        self.request_factory = RequestFactory()


    def test_video_admin_list_display_contains_processing_status(self):
        """Test that processing status is visible in the admin list."""

        assert 'processing_status' in self.video_admin.list_display


    def test_video_admin_list_display_contains_processing_error_preview(self):
        """Test that processing errors are visible in the admin list."""

        assert 'processing_error_preview' in self.video_admin.list_display


    def test_video_admin_list_filter_contains_processing_status(self):
        """Test that videos can be filtered by processing status."""

        assert 'processing_status' in self.video_admin.list_filter


    def test_video_admin_processing_status_is_readonly(self):
        """Test that processing status cannot be edited manually."""

        assert 'processing_status' in self.video_admin.readonly_fields


    def test_video_admin_processing_error_is_readonly(self):
        """Test that processing errors cannot be edited manually."""

        assert 'processing_error' in self.video_admin.readonly_fields


    def test_video_admin_thumbnail_preview_is_readonly(self):
        """Test that the thumbnail preview is readonly in the admin."""

        assert 'thumbnail_preview' in self.video_admin.readonly_fields


    def test_video_admin_processing_status_help_is_readonly(self):
        """Test that processing status help is shown as readonly text."""

        assert 'processing_status_help' in self.video_admin.readonly_fields


    def test_video_admin_processing_error_help_is_readonly(self):
        """Test that processing error help is shown as readonly text."""

        assert 'processing_error_help' in self.video_admin.readonly_fields


    def test_video_admin_excludes_manual_thumbnail_upload(self):
        """Test that thumbnails cannot be uploaded manually in the admin."""

        assert 'thumbnail' in self.video_admin.exclude


    def test_video_admin_does_not_register_convert_to_hls_action(self):
        """Test that manual HLS conversion action is not registered."""

        assert 'convert_selected_videos_to_hls' not in self.video_admin.actions


    def test_video_admin_does_not_register_retry_failed_conversions_action(self):
        """Test that manual retry conversion action is not registered."""

        assert 'retry_failed_hls_conversions' not in self.video_admin.actions


    def test_video_admin_search_fields_contains_title_and_category(self):
        """Test that videos can be searched by title and category."""

        assert 'title' in self.video_admin.search_fields
        assert 'category' in self.video_admin.search_fields


    def test_processing_error_preview_returns_empty_marker_without_error(self):
        """Test that empty processing errors are displayed clearly."""

        video = Video(processing_error='')

        assert self.video_admin.processing_error_preview(video) == '-'


    def test_processing_error_preview_returns_short_error_text(self):
        """Test that short processing errors are returned unchanged."""

        video = Video(processing_error='FFmpeg failed')

        assert self.video_admin.processing_error_preview(video) == 'FFmpeg failed'


    def test_processing_error_preview_truncates_long_error_text(self):
        """Test that long processing errors are shortened for the admin list."""

        video = Video(processing_error='x' * 120)

        expected_preview = f'{"x" * 77}...'
        assert self.video_admin.processing_error_preview(video) == expected_preview


    def test_processing_status_help_explains_automatic_status_values(self):
        """Test that status help explains automatic processing status values."""

        help_text = self.video_admin.processing_status_help(None)

        assert 'automatischen Videoverarbeitung' in help_text
        assert 'pending = wartet auf Verarbeitung' in help_text
        assert 'processing = Verarbeitung läuft' in help_text
        assert 'ready = erfolgreich verarbeitet und im Frontend sichtbar' in help_text
        assert 'failed = fehlgeschlagen' in help_text
        assert 'processing error' in help_text


    def test_processing_error_help_explains_failed_processing_errors(self):
        """Test that processing error help explains failed conversion errors."""

        help_text = self.video_admin.processing_error_help(None)

        assert 'technische Fehlermeldung' in help_text
        assert 'automatische Videoverarbeitung fehlgeschlagen' in help_text
        assert 'Backend gesetzt' in help_text


    def test_thumbnail_preview_returns_empty_marker_without_thumbnail(self):
        """Test that missing thumbnails are displayed clearly."""

        video = Video(thumbnail='')

        assert self.video_admin.thumbnail_preview(video) == '-'


    def test_thumbnail_preview_returns_image_html_with_thumbnail(self):
        """Test that an existing thumbnail is displayed as image preview."""

        video = Video(thumbnail='videos/1/thumbnail/thumb.jpg')

        preview = self.video_admin.thumbnail_preview(video)

        assert '<img' in preview
        assert 'thumb.jpg' in preview


    @patch('videos_app.admin.VideoAdmin.message_user')
    def test_video_admin_shows_automatic_processing_message_on_create(
        self,
        mocked_message_user,
    ):
        """Test that admins see an automatic processing explanation on create."""

        request = self.create_admin_request()
        video = Video(
            title='Movie Title',
            description='Movie Description',
            category=Video.CATEGORY_DRAMA,
            source_file=ContentFile(b'video-content', name='movie.mp4'),
        )

        self.video_admin.save_model(request, video, form=None, change=False)

        expected_message = (
            'Die automatische Videoverarbeitung wurde gestartet. '
            'Aktualisieren Sie später die Seite und prüfen Sie den Status. '
            'Wenn das Video als „failed“ erscheint, ist die Verarbeitung '
            'fehlgeschlagen. Die hochgeladene Videodatei und alle dabei '
            'erzeugten Dateien wurden automatisch bereinigt. Laden Sie das '
            'Video in diesem Fall erneut hoch. Der Videodatensatz aus der '
            'fehlgeschlagenen Verarbeitung kann bei Bedarf über den '
            'Statusfilter gesucht und manuell gelöscht werden.'
        )

        mocked_message_user.assert_called_once_with(
            request,
            expected_message,
            level=30,
        )


    def create_video(
        self,
        title='Movie Title',
        processing_status=Video.STATUS_PENDING,
    ):
        """Create and return a video for admin tests."""

        return Video.objects.create(
            title=title,
            description='Movie Description',
            category=Video.CATEGORY_DRAMA,
            processing_status=processing_status,
        )


    def create_admin_request(self):
        """Create an admin request object with message storage."""

        request = self.request_factory.post('/admin/videos_app/video/')
        request.session = {}
        request._messages = FallbackStorage(request)

        return request