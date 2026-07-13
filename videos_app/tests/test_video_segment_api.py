"""Tests for the Videoflix video segment API endpoint."""

from unittest.mock import patch

import pytest

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from videos_app.models import Video
from videos_app.tests.mixins import VideoTestMixin


@pytest.mark.django_db
class TestVideoSegmentApi(VideoTestMixin):
    """Test GET /api/video/<movie_id>/<resolution>/<segment>/."""

    def setup_method(self):
        """Prepare API client, active user and media root placeholder."""

        self.client = APIClient()
        self.user = self.create_active_user(email='user@example.com')
        self.media_root = None


    def get_segment_url(self, video_id, resolution='720p', segment='000.ts'):
        """Return the video segment endpoint URL."""

        return reverse(
            'video-segment',
            kwargs={
                'movie_id': video_id,
                'resolution': resolution,
                'segment': segment,
            },
        )


    def test_video_segment_returns_200_for_authenticated_user(self, settings, tmp_path):
        """Test that authenticated users can retrieve an existing segment."""

        self.media_root = tmp_path
        settings.MEDIA_ROOT = tmp_path
        self.authenticate_client()
        video = self.create_video()
        self.create_segment_file(
            video=video,
            resolution='720p',
            segment='000.ts',
        )
        url = self.get_segment_url(
            video.id,
            resolution='720p',
            segment='000.ts',
        )

        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK


    def test_video_segment_rejects_unauthenticated_user(self, settings, tmp_path):
        """Test that unauthenticated users cannot retrieve a segment."""

        self.media_root = tmp_path
        settings.MEDIA_ROOT = tmp_path
        video = self.create_video()
        self.create_segment_file(
            video=video,
            resolution='720p',
            segment='000.ts',
        )
        url = self.get_segment_url(
            video.id,
            resolution='720p',
            segment='000.ts',
        )

        response = self.client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


    def test_video_segment_returns_mp2t_content_type(self, settings, tmp_path):
        """Test that the segment response uses the documented content type."""

        self.media_root = tmp_path
        settings.MEDIA_ROOT = tmp_path
        self.authenticate_client()
        video = self.create_video()
        self.create_segment_file(
            video=video,
            resolution='720p',
            segment='000.ts',
        )
        url = self.get_segment_url(
            video.id,
            resolution='720p',
            segment='000.ts',
        )

        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response['Content-Type'] == 'video/MP2T'


    def test_video_segment_returns_binary_segment_body(self, settings, tmp_path):
        """Test that the segment response body contains binary TS data."""

        self.media_root = tmp_path
        settings.MEDIA_ROOT = tmp_path
        self.authenticate_client()
        video = self.create_video()
        self.create_segment_file(
            video=video,
            resolution='720p',
            segment='000.ts',
        )
        url = self.get_segment_url(
            video.id,
            resolution='720p',
            segment='000.ts',
        )

        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.content == b'test-ts-segment-content'


    def test_video_segment_rejects_unknown_video(self, settings, tmp_path):
        """Test that an unknown video id returns HTTP 404 NOT FOUND."""

        self.media_root = tmp_path
        settings.MEDIA_ROOT = tmp_path
        self.authenticate_client()
        url = self.get_segment_url(
            999999,
            resolution='720p',
            segment='000.ts',
        )

        response = self.client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


    def test_video_segment_rejects_missing_segment(self, settings, tmp_path):
        """Test that existing video without segment returns HTTP 404."""

        self.media_root = tmp_path
        settings.MEDIA_ROOT = tmp_path
        self.authenticate_client()
        video = self.create_video()
        url = self.get_segment_url(
            video.id,
            resolution='720p',
            segment='000.ts',
        )

        response = self.client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


    def test_video_segment_rejects_unknown_resolution(self, settings, tmp_path):
        """Test that a missing resolution segment returns HTTP 404."""

        self.media_root = tmp_path
        settings.MEDIA_ROOT = tmp_path
        self.authenticate_client()
        video = self.create_video()
        self.create_segment_file(
            video=video,
            resolution='720p',
            segment='000.ts',
        )
        url = self.get_segment_url(
            video.id,
            resolution='1080p',
            segment='000.ts',
        )

        response = self.client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


    def test_video_segment_rejects_unknown_segment_name(self, settings, tmp_path):
        """Test that an unknown segment filename returns HTTP 404."""

        self.media_root = tmp_path
        settings.MEDIA_ROOT = tmp_path
        self.authenticate_client()
        video = self.create_video()
        self.create_segment_file(
            video=video,
            resolution='720p',
            segment='000.ts',
        )
        url = self.get_segment_url(
            video.id,
            resolution='720p',
            segment='001.ts',
        )

        response = self.client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


    def test_video_segment_rejects_pending_video(self, settings, tmp_path):
        """Test that pending videos do not expose segments."""

        self.media_root = tmp_path
        settings.MEDIA_ROOT = tmp_path
        self.authenticate_client()
        video = self.create_video(processing_status=Video.STATUS_PENDING)
        self.create_segment_file(
            video=video,
            resolution='720p',
            segment='000.ts',
        )
        url = self.get_segment_url(
            video.id,
            resolution='720p',
            segment='000.ts',
        )

        response = self.client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


    def test_video_segment_rejects_processing_video(self, settings, tmp_path):
        """Test that processing videos do not expose segments."""

        self.media_root = tmp_path
        settings.MEDIA_ROOT = tmp_path
        self.authenticate_client()
        video = self.create_video(processing_status=Video.STATUS_PROCESSING)
        self.create_segment_file(
            video=video,
            resolution='720p',
            segment='000.ts',
        )
        url = self.get_segment_url(
            video.id,
            resolution='720p',
            segment='000.ts',
        )

        response = self.client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


    def test_video_segment_rejects_failed_video(self, settings, tmp_path):
        """Test that failed videos do not expose segments."""

        self.media_root = tmp_path
        settings.MEDIA_ROOT = tmp_path
        self.authenticate_client()
        video = self.create_video(processing_status=Video.STATUS_FAILED)
        self.create_segment_file(
            video=video,
            resolution='720p',
            segment='000.ts',
        )
        url = self.get_segment_url(
            video.id,
            resolution='720p',
            segment='000.ts',
        )

        response = self.client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


    @patch('videos_app.api.views.Video.objects.get')
    def test_video_segment_returns_500_for_internal_error(self, mocked_get, settings, tmp_path):
        """Test that an internal segment loading error returns HTTP 500."""

        self.media_root = tmp_path
        settings.MEDIA_ROOT = tmp_path
        self.authenticate_client()
        mocked_get.side_effect = Exception('Forced internal segment error')
        url = self.get_segment_url(1, resolution='720p', segment='000.ts')

        response = self.client.get(url)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR