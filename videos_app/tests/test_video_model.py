"""Tests for the Videoflix video model."""

from pathlib import Path

import pytest

from django.conf import settings
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
            'category': Video.CATEGORY_DRAMA,
        }
        defaults.update(kwargs)

        return Video.objects.create(**defaults)


    def create_hls_output_directory(self, video, resolution):
        """Create an HLS output directory with a dummy file."""

        output_dir = (
            Path(settings.MEDIA_ROOT)
            / 'videos'
            / str(video.id)
            / resolution
        )
        output_dir.mkdir(parents=True, exist_ok=True)

        manifest_path = output_dir / 'index.m3u8'
        segment_path = output_dir / '000.ts'

        manifest_path.write_text('#EXTM3U', encoding='utf-8')
        segment_path.write_bytes(b'test-segment')

        return output_dir


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


    def test_video_category_choices_are_defined(self):
        """Test that all required video category choices are available."""

        expected_choices = {
            (Video.CATEGORY_ACTION, 'Action'),
            (Video.CATEGORY_ADVENTURE, 'Adventure'),
            (Video.CATEGORY_ANIMATION, 'Animation'),
            (Video.CATEGORY_COMEDY, 'Comedy'),
            (Video.CATEGORY_CRIME, 'Crime'),
            (Video.CATEGORY_DOCUMENTARY, 'Documentary'),
            (Video.CATEGORY_DRAMA, 'Drama'),
            (Video.CATEGORY_FAMILY, 'Family'),
            (Video.CATEGORY_FANTASY, 'Fantasy'),
            (Video.CATEGORY_HISTORY, 'History'),
            (Video.CATEGORY_HORROR, 'Horror'),
            (Video.CATEGORY_MYSTERY, 'Mystery'),
            (Video.CATEGORY_NATURE, 'Nature'),
            (Video.CATEGORY_ROMANCE, 'Romance'),
            (Video.CATEGORY_SCIENCE_FICTION, 'Science Fiction'),
            (Video.CATEGORY_SPORTS, 'Sports'),
            (Video.CATEGORY_THRILLER, 'Thriller'),
            (Video.CATEGORY_TRAVEL, 'Travel'),
        }

        assert set(Video.CATEGORY_CHOICES) == expected_choices


    def test_video_category_defaults_to_drama_in_test_factory(self):
        """Test that the model test factory creates drama videos by default."""

        video = self.create_video()

        assert video.category == Video.CATEGORY_DRAMA


    def test_video_processing_error_is_empty_by_default(self):
        """Test that new videos do not contain a processing error."""

        video = self.create_video()

        assert video.processing_error == ''


    def test_video_source_file_can_be_empty(self):
        """Test that a video can be created without source file."""

        video = self.create_video()

        assert video.source_file.name == ''


    def test_video_thumbnail_can_be_empty_initially(self):
        """Test that a video can be created without a thumbnail."""

        video = self.create_video()

        assert video.thumbnail.name == ''


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


    def test_video_delete_removes_video_media_directory(self, settings, tmp_path):
        """Test that deleting a video removes its full media directory."""

        settings.MEDIA_ROOT = tmp_path

        video = self.create_video(
            source_file=ContentFile(b'video-content', name='movie.mp4'),
        )
        self.create_hls_output_directory(video, '720p')
        video_media_dir = tmp_path / 'videos' / str(video.id)

        video.delete()

        assert not video_media_dir.exists()


    def test_video_delete_removes_source_file(self, settings, tmp_path):
        """Test that deleting a video removes its source file."""

        settings.MEDIA_ROOT = tmp_path

        video = self.create_video(
            source_file=ContentFile(b'video-content', name='movie.mp4'),
        )
        source_path = Path(video.source_file.path)

        video.delete()

        assert not source_path.exists()


    def test_video_delete_removes_hls_output_directories(self, settings, tmp_path):
        """Test that deleting a video removes generated HLS output."""

        settings.MEDIA_ROOT = tmp_path

        video = self.create_video(
            source_file=ContentFile(b'video-content', name='movie.mp4'),
        )
        self.create_hls_output_directory(video, '480p')
        self.create_hls_output_directory(video, '720p')
        self.create_hls_output_directory(video, '1080p')

        video.delete()

        assert not (tmp_path / 'videos' / str(video.id) / '480p').exists()
        assert not (tmp_path / 'videos' / str(video.id) / '720p').exists()
        assert not (tmp_path / 'videos' / str(video.id) / '1080p').exists()


    def test_video_delete_does_not_fail_when_media_directory_is_missing(
        self,
        settings,
        tmp_path,
    ):
        """Test that deleting a video works when its media directory is missing."""

        settings.MEDIA_ROOT = tmp_path

        video = self.create_video()

        video.delete()

        assert not Video.objects.filter(id=video.id).exists()