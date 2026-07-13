"""Tests for the Videoflix video manifest API endpoint."""

from unittest.mock import patch

import pytest

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from videos_app.models import Video
from videos_app.tests.mixins import VideoTestMixin


@pytest.mark.django_db
class TestVideoManifestApi(VideoTestMixin):
    """Test GET /api/video/<movie_id>/<resolution>/index.m3u8."""

    def setup_method(self):
        """Prepare API client, active user and media root placeholder."""

        self.client = APIClient()
        self.user = self.create_active_user(email='user@example.com')
        self.media_root = None


    def get_manifest_url(self, video_id, resolution='720p'):
        """Return the video manifest endpoint URL."""

        return reverse(
            'video-manifest',
            kwargs={
                'movie_id': video_id,
                'resolution': resolution,
            },
        )


    def test_video_manifest_returns_200_for_authenticated_user(self, settings, tmp_path):
        """Test that authenticated users can retrieve an existing manifest."""

        self.media_root = tmp_path
        settings.MEDIA_ROOT = tmp_path
        self.authenticate_client()
        video = self.create_video()
        self.create_manifest_file(video=video, resolution='720p')
        url = self.get_manifest_url(video.id, resolution='720p')

        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK


    def test_video_manifest_rejects_unauthenticated_user(self, settings, tmp_path):
        """Test that unauthenticated users cannot retrieve a manifest."""

        self.media_root = tmp_path
        settings.MEDIA_ROOT = tmp_path
        video = self.create_video()
        self.create_manifest_file(video=video, resolution='720p')
        url = self.get_manifest_url(video.id, resolution='720p')

        response = self.client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


    def test_video_manifest_returns_mpegurl_content_type(self, settings, tmp_path):
        """Test that the manifest response uses the documented content type."""

        self.media_root = tmp_path
        settings.MEDIA_ROOT = tmp_path
        self.authenticate_client()
        video = self.create_video()
        self.create_manifest_file(video=video, resolution='720p')
        url = self.get_manifest_url(video.id, resolution='720p')

        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response['Content-Type'] == 'application/vnd.apple.mpegurl'


    def test_video_manifest_returns_m3u8_body(self, settings, tmp_path):
        """Test that the manifest response body contains M3U8 content."""

        self.media_root = tmp_path
        settings.MEDIA_ROOT = tmp_path
        self.authenticate_client()
        video = self.create_video()
        self.create_manifest_file(video=video, resolution='720p')
        url = self.get_manifest_url(video.id, resolution='720p')

        response = self.client.get(url)

        body = response.content.decode('utf-8')

        assert response.status_code == status.HTTP_200_OK
        assert '#EXTM3U' in body
        assert 'segment_000.ts' in body


    def test_video_manifest_rejects_unknown_video(self, settings, tmp_path):
        """Test that an unknown video id returns HTTP 404 NOT FOUND."""

        self.media_root = tmp_path
        settings.MEDIA_ROOT = tmp_path
        self.authenticate_client()
        url = self.get_manifest_url(999999, resolution='720p')

        response = self.client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


    def test_video_manifest_rejects_missing_manifest(self, settings, tmp_path):
        """Test that an existing video without manifest returns HTTP 404."""

        self.media_root = tmp_path
        settings.MEDIA_ROOT = tmp_path
        self.authenticate_client()
        video = self.create_video()
        url = self.get_manifest_url(video.id, resolution='720p')

        response = self.client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


    def test_video_manifest_rejects_unknown_resolution(self, settings, tmp_path):
        """Test that a missing resolution manifest returns HTTP 404."""

        self.media_root = tmp_path
        settings.MEDIA_ROOT = tmp_path
        self.authenticate_client()
        video = self.create_video()
        self.create_manifest_file(video=video, resolution='720p')
        url = self.get_manifest_url(video.id, resolution='1080p')

        response = self.client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


    def test_video_manifest_rejects_pending_video(self, settings, tmp_path):
        """Test that pending videos do not expose manifests."""

        self.media_root = tmp_path
        settings.MEDIA_ROOT = tmp_path
        self.authenticate_client()
        video = self.create_video(processing_status=Video.STATUS_PENDING)
        self.create_manifest_file(video=video, resolution='720p')
        url = self.get_manifest_url(video.id, resolution='720p')

        response = self.client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


    def test_video_manifest_rejects_processing_video(self, settings, tmp_path):
        """Test that processing videos do not expose manifests."""

        self.media_root = tmp_path
        settings.MEDIA_ROOT = tmp_path
        self.authenticate_client()
        video = self.create_video(processing_status=Video.STATUS_PROCESSING)
        self.create_manifest_file(video=video, resolution='720p')
        url = self.get_manifest_url(video.id, resolution='720p')

        response = self.client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


    def test_video_manifest_rejects_failed_video(self, settings, tmp_path):
        """Test that failed videos do not expose manifests."""

        self.media_root = tmp_path
        settings.MEDIA_ROOT = tmp_path
        self.authenticate_client()
        video = self.create_video(processing_status=Video.STATUS_FAILED)
        self.create_manifest_file(video=video, resolution='720p')
        url = self.get_manifest_url(video.id, resolution='720p')

        response = self.client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


    @patch('videos_app.api.views.Video.objects.get')
    def test_video_manifest_returns_500_for_internal_error(self, mocked_get, settings, tmp_path):
        """Test that an internal manifest loading error returns HTTP 500."""

        self.media_root = tmp_path
        settings.MEDIA_ROOT = tmp_path
        self.authenticate_client()
        mocked_get.side_effect = Exception('Forced internal manifest error')
        url = self.get_manifest_url(1, resolution='720p')

        response = self.client.get(url)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR