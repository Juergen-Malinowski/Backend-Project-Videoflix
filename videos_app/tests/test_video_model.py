"""Tests for the Videoflix video model."""

from pathlib import Path

import pytest

from django.core.files.base import ContentFile

from videos_app.models import Video


@pytest.mark.django_db
class TestVideoModel:
    """Test video model fields and source file handling."""

    def create_video(self, **kwargs):
        """Create and return a video instance for model tests."""

        defaults = {
            'title': 'Movie Title',
            'description': 'Movie Description',
            'thumbnail_url': 'http://example.com/media/thumbnail/image.jpg',
            'category': 'Drama',
        }
        defaults.update(kwargs)

        return Video.objects.create(**defaults)


    def test_video_default_processing_status_is_pending(self):
        """Test that new videos start with pending processing status."""

        video = self.create_video()

        assert video.processing_status == Video.STATUS_PENDING


    def test_video_processing_status_choices_are_defined(self):
        """Test that all required processing status choices are available."""

        expected_choices = {
            (Video.STATUS_PENDING, 'Pending'),
            (Video.STATUS_PROCESSING, 'Processing'),
            (Video.STATUS_READY, 'Ready'),
            (Video.STATUS_FAILED, 'Failed'),
        }

        assert set(Video.PROCESSING_STATUS_CHOICES) == expected_choices


    def test_video_processing_error_is_empty_by_default(self):
        """Test that new videos do not contain a processing error."""

        video = self.create_video()

        assert video.processing_error == ''


    def test_video_source_file_can_be_empty(self):
        """Test that a video can be created without source file."""

        video = self.create_video()

        assert video.source_file.name == ''


    def test_video_source_file_is_moved_to_final_path(self, settings, tmp_path):
        """Test that uploaded source files are moved to the video folder."""

        settings.MEDIA_ROOT = tmp_path

        video = self.create_video(
            source_file=ContentFile(b'video-content', name='movie.mp4'),
        )

        expected_name = f'videos/{video.id}/source/movie.mp4'
        expected_path = tmp_path / expected_name

        assert video.source_file.name == expected_name
        assert expected_path.exists()


    def test_video_source_file_keeps_uploaded_content(self, settings, tmp_path):
        """Test that moved source files keep their uploaded content."""

        settings.MEDIA_ROOT = tmp_path

        video = self.create_video(
            source_file=ContentFile(b'video-content', name='movie.mp4'),
        )

        source_path = Path(settings.MEDIA_ROOT) / video.source_file.name

        assert source_path.read_bytes() == b'video-content'


    def test_video_source_temp_file_is_removed_after_move(self, settings, tmp_path):
        """Test that the temporary source file is removed after moving."""

        settings.MEDIA_ROOT = tmp_path

        video = self.create_video(
            source_file=ContentFile(b'video-content', name='movie.mp4'),
        )

        temp_path = tmp_path / 'videos' / 'temp' / 'movie.mp4'

        assert video.source_file.name == f'videos/{video.id}/source/movie.mp4'
        assert not temp_path.exists()