"""Tests for the Videoflix video admin configuration."""

from unittest.mock import patch

import pytest

from django.contrib import admin
from django.contrib.messages.storage.fallback import FallbackStorage
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

    def test_video_admin_search_fields_contains_title_and_category(self):
        """Test that videos can be searched by title and category."""

        assert 'title' in self.video_admin.search_fields
        assert 'category' in self.video_admin.search_fields

    def test_video_admin_actions_contain_convert_to_hls_action(self):
        """Test that the convert to HLS admin action is registered."""

        assert 'convert_selected_videos_to_hls' in self.video_admin.actions

    def test_video_admin_actions_contain_retry_failed_conversions_action(self):
        """Test that the retry failed conversions admin action is registered."""

        assert 'retry_failed_hls_conversions' in self.video_admin.actions

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

    @patch('videos_app.admin.convert_video_to_hls')
    def test_convert_selected_videos_to_hls_calls_task_for_each_video(
        self,
        mocked_task,
    ):
        """Test that convert action starts one task per selected video."""

        request = self.create_admin_request()
        first_video = self.create_video(title='First Movie')
        second_video = self.create_video(title='Second Movie')
        queryset = Video.objects.filter(id__in=[first_video.id, second_video.id])

        self.video_admin.convert_selected_videos_to_hls(request, queryset)

        assert mocked_task.delay.call_count == 2
        mocked_task.delay.assert_any_call(first_video.id)
        mocked_task.delay.assert_any_call(second_video.id)

    @patch('videos_app.admin.convert_video_to_hls')
    def test_retry_failed_hls_conversions_calls_task_only_for_failed_videos(
        self,
        mocked_task,
    ):
        """Test that retry action starts tasks only for failed videos."""

        request = self.create_admin_request()
        failed_video = self.create_video(
            title='Failed Movie',
            processing_status=Video.STATUS_FAILED,
        )
        ready_video = self.create_video(
            title='Ready Movie',
            processing_status=Video.STATUS_READY,
        )
        queryset = Video.objects.filter(id__in=[failed_video.id, ready_video.id])

        self.video_admin.retry_failed_hls_conversions(request, queryset)

        mocked_task.delay.assert_called_once_with(failed_video.id)

    def create_video(
        self,
        title='Movie Title',
        processing_status=Video.STATUS_PENDING,
    ):
        """Create and return a video for admin tests."""

        return Video.objects.create(
            title=title,
            description='Movie Description',
            thumbnail_url='http://example.com/media/thumbnail/image.jpg',
            category='Drama',
            processing_status=processing_status,
        )

    def create_admin_request(self):
        """Create an admin request object with message storage."""

        request = self.request_factory.post('/admin/videos_app/video/')
        request.session = {}
        request._messages = FallbackStorage(request)

        return request