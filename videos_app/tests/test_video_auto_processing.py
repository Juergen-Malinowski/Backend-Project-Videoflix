"""Tests for automatic video processing after video upload."""

from unittest.mock import patch

import pytest

from django.core.files.base import ContentFile
from django.db import transaction

from videos_app.models import Video


@pytest.mark.django_db(transaction=True)
class TestVideoAutoProcessing:
    """Test automatic RQ job registration for uploaded videos."""

    def create_video(self, **kwargs):
        """Create and return a video instance for auto-processing tests."""

        defaults = {
            'title': 'Movie Title',
            'description': 'Movie Description',
            'category': Video.CATEGORY_DRAMA,
        }
        defaults.update(kwargs)

        return Video.objects.create(**defaults)


    @patch('videos_app.tasks.convert_video_to_hls')
    def test_new_video_with_source_file_starts_conversion_after_commit(
        self,
        mocked_convert_video_to_hls,
    ):
        """Test that a new uploaded video starts conversion after commit."""

        video = self.create_video(
            source_file=ContentFile(b'video-content', name='movie.mp4'),
        )

        mocked_convert_video_to_hls.delay.assert_called_once_with(video.id)


    @patch('videos_app.tasks.convert_video_to_hls')
    def test_conversion_job_does_not_start_before_commit(
        self,
        mocked_convert_video_to_hls,
    ):
        """Test that conversion is delayed until the database commit."""

        with transaction.atomic():
            video = self.create_video(
                source_file=ContentFile(b'video-content', name='movie.mp4'),
            )

            mocked_convert_video_to_hls.delay.assert_not_called()

        mocked_convert_video_to_hls.delay.assert_called_once_with(video.id)


    @patch('videos_app.tasks.convert_video_to_hls')
    def test_metadata_update_does_not_start_conversion_again(
        self,
        mocked_convert_video_to_hls,
    ):
        """Test that later metadata updates do not start another conversion."""

        video = self.create_video(
            source_file=ContentFile(b'video-content', name='movie.mp4'),
        )
        mocked_convert_video_to_hls.delay.reset_mock()

        video.title = 'Updated Movie Title'
        video.save(update_fields=['title'])

        mocked_convert_video_to_hls.delay.assert_not_called()


    @patch('videos_app.tasks.convert_video_to_hls')
    def test_video_without_source_file_does_not_start_conversion(
        self,
        mocked_convert_video_to_hls,
    ):
        """Test that videos without uploaded source files are not processed."""

        self.create_video()

        mocked_convert_video_to_hls.delay.assert_not_called()