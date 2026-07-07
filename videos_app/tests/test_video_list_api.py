"""Tests for the Videoflix video list API endpoint."""

from datetime import timedelta

from unittest.mock import patch

import pytest

from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APIClient

from videos_app.tests.mixins import VideoTestMixin
from videos_app.models import Video


@pytest.mark.django_db
class TestVideoListApi(VideoTestMixin):
    """Test GET /api/video/ for authenticated video metadata listing."""

    def setup_method(self):
        """Prepare API client, active user and endpoint URL."""

        self.client = APIClient()
        self.user = self.create_active_user(email='user@example.com')
        self.url = reverse('video-list')


    def test_video_list_returns_200_for_authenticated_user(self):
        """Test that authenticated users can retrieve the video list."""

        self.authenticate_client()

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK


    def test_video_list_rejects_unauthenticated_user(self):
        """Test that unauthenticated users cannot retrieve the video list."""

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


    def test_video_list_returns_list_response(self):
        """Test that the video list endpoint returns a list response."""

        self.authenticate_client()

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)


    def test_video_list_returns_all_available_videos(self):
        """Test that the video list contains all available videos."""

        self.authenticate_client()
        self.create_video(title='Movie Title', category='Drama')
        self.create_video(title='Another Movie', category='Romance')

        response = self.client.get(self.url)

        response_titles = {video['title'] for video in response.data}

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
        assert response_titles == {'Movie Title', 'Another Movie'}


    def test_video_list_orders_videos_by_created_at_desc(self):
        """Test that newest videos are listed first."""

        self.authenticate_client()
        older_video = self.create_video(title='Older Movie')
        newer_video = self.create_video(title='Newer Movie')
        reference_time = timezone.now()

        Video.objects.filter(id=older_video.id).update(
            created_at=reference_time - timedelta(days=1),
        )
        Video.objects.filter(id=newer_video.id).update(
            created_at=reference_time,
        )

        response = self.client.get(self.url)

        response_titles = [video['title'] for video in response.data]

        assert response.status_code == status.HTTP_200_OK
        assert response_titles == ['Newer Movie', 'Older Movie']


    def test_video_list_returns_documented_video_fields(self):
        """Test that each video object contains the documented fields."""

        self.authenticate_client()
        self.create_video()

        response = self.client.get(self.url)

        expected_fields = {
            'id',
            'created_at',
            'title',
            'description',
            'thumbnail_url',
            'category',
        }

        assert response.status_code == status.HTTP_200_OK
        assert set(response.data[0].keys()) == expected_fields


    def test_video_list_returns_video_metadata(self):
        """Test that video metadata matches the stored video data."""

        self.authenticate_client()
        video = self.create_video(title='Movie Title', category='Drama')

        response = self.client.get(self.url)

        video_data = response.data[0]

        assert response.status_code == status.HTTP_200_OK
        assert video_data['id'] == video.id
        assert video_data['title'] == 'Movie Title'
        assert video_data['description'] == 'Movie Description'
        assert video_data['thumbnail_url'] == (
            'http://example.com/media/thumbnail/image.jpg'
        )
        assert video_data['category'] == 'Drama'
        assert 'created_at' in video_data
        assert video_data['created_at']


    @patch('videos_app.api.views.Video.objects.all')
    def test_video_list_returns_500_for_internal_error(self, mocked_all):
        """Test that an internal video loading error returns HTTP 500."""

        self.authenticate_client()
        mocked_all.side_effect = Exception('Forced internal video list error')

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR