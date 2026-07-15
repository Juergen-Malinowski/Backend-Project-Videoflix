"""Tests for video background processing tasks."""

from pathlib import Path
from unittest.mock import patch

import pytest

from django.conf import settings
from django.core.files.base import ContentFile

from videos_app.models import Video
from videos_app.tasks import convert_video_to_hls
from videos_app.tests.mixins import VideoTestMixin


@pytest.mark.django_db
class TestVideoTasks(VideoTestMixin):
    """Test video processing background tasks."""

    def create_video_with_processing_files(self):
        """Create a video with source, thumbnail and HLS output files."""

        video = self.create_video_for_tasks()
        video.source_file.save(
            'source.mp4',
            ContentFile(b'video content'),
            save=True,
        )
        video.thumbnail.name = f'videos/{video.id}/thumbnail/thumbnail.jpg'
        video.save(update_fields=['thumbnail'])

        thumbnail_path = Path(settings.MEDIA_ROOT) / video.thumbnail.name
        hls_path = Path(settings.MEDIA_ROOT) / 'videos' / str(video.id) / '720p'

        thumbnail_path.parent.mkdir(parents=True, exist_ok=True)
        hls_path.mkdir(parents=True, exist_ok=True)

        thumbnail_path.write_bytes(b'thumbnail content')
        (hls_path / 'index.m3u8').write_text('#EXTM3U', encoding='utf-8')

        return video


    @patch('videos_app.tasks.process_video_to_hls')
    def test_convert_video_to_hls_ignores_unknown_video_id(self, mocked_process_video_to_hls):
        """Test that unknown video ids do not raise processing errors."""

        convert_video_to_hls(999999)

        mocked_process_video_to_hls.assert_not_called()


    @patch('videos_app.tasks.process_video_to_hls')
    def test_convert_video_to_hls_sets_status_to_processing_before_processing(
        self,
        mocked_process_video_to_hls,
    ):
        """Test that conversion marks the video as processing before HLS work."""

        video = self.create_video_for_tasks()

        def assert_processing_status(processed_video):
            processed_video.refresh_from_db()

            assert processed_video.processing_status == Video.STATUS_PROCESSING

        mocked_process_video_to_hls.side_effect = assert_processing_status

        convert_video_to_hls(video.id)

        video.refresh_from_db()

        assert video.processing_status == Video.STATUS_READY


    @patch('videos_app.tasks.process_video_to_hls')
    def test_convert_video_to_hls_clears_old_processing_error(self, _mocked_process_video_to_hls):
        """Test that old processing errors are cleared before conversion."""

        video = self.create_video_for_tasks(
            processing_status=Video.STATUS_FAILED,
            processing_error='Old FFmpeg error',
        )

        convert_video_to_hls(video.id)

        video.refresh_from_db()
        assert video.processing_error == ''


    @patch('videos_app.tasks.process_video_to_hls')
    def test_convert_video_to_hls_calls_hls_processing_service(self, mocked_process_video_to_hls):
        """Test that conversion calls the HLS processing service."""

        video = self.create_video_for_tasks()

        convert_video_to_hls(video.id)

        mocked_process_video_to_hls.assert_called_once()
        processed_video = mocked_process_video_to_hls.call_args.args[0]

        assert processed_video.id == video.id


    @patch('videos_app.tasks.process_video_to_hls')
    def test_convert_video_to_hls_sets_status_to_ready_on_success(self, _mocked_process_video_to_hls):
        """Test that successful conversion marks the video as ready."""

        video = self.create_video_for_tasks()

        convert_video_to_hls(video.id)

        video.refresh_from_db()

        assert video.processing_status == Video.STATUS_READY


    @patch('videos_app.tasks.process_video_to_hls')
    def test_convert_video_to_hls_sets_status_to_failed_on_error(
        self,
        mocked_process_video_to_hls,
    ):
        """Test that failed conversion marks the video as failed."""

        mocked_process_video_to_hls.side_effect = RuntimeError('FFmpeg failed')
        video = self.create_video_for_tasks()

        convert_video_to_hls(video.id)

        video.refresh_from_db()

        assert video.processing_status == Video.STATUS_FAILED


    @patch('videos_app.tasks.process_video_to_hls')
    def test_convert_video_to_hls_stores_error_message_on_error(
        self,
        mocked_process_video_to_hls,
    ):
        """Test that failed conversion stores the processing error."""

        mocked_process_video_to_hls.side_effect = RuntimeError('FFmpeg failed')
        video = self.create_video_for_tasks()

        convert_video_to_hls(video.id)

        video.refresh_from_db()

        assert video.processing_error == 'FFmpeg failed'


    @patch('videos_app.tasks.process_video_to_hls')
    def test_convert_video_to_hls_keeps_video_record_on_error(
        self,
        mocked_process_video_to_hls,
    ):
        """Test that failed conversion keeps the video database record."""

        mocked_process_video_to_hls.side_effect = RuntimeError('FFmpeg failed')
        video = self.create_video_with_processing_files()

        convert_video_to_hls(video.id)

        assert Video.objects.filter(id=video.id).exists()


    @patch('videos_app.tasks.process_video_to_hls')
    def test_convert_video_to_hls_removes_hls_output_on_error(
        self,
        mocked_process_video_to_hls,
    ):
        """Test that failed conversion removes generated HLS output."""

        mocked_process_video_to_hls.side_effect = RuntimeError('FFmpeg failed')
        video = self.create_video_with_processing_files()
        hls_path = Path(settings.MEDIA_ROOT) / 'videos' / str(video.id) / '720p'

        convert_video_to_hls(video.id)

        assert not hls_path.exists()


    @patch('videos_app.tasks.process_video_to_hls')
    def test_convert_video_to_hls_removes_source_file_on_error(
        self,
        mocked_process_video_to_hls,
    ):
        """Test that failed conversion removes the uploaded source file."""

        mocked_process_video_to_hls.side_effect = RuntimeError('FFmpeg failed')
        video = self.create_video_with_processing_files()
        source_path = Path(video.source_file.path)

        convert_video_to_hls(video.id)

        assert not source_path.exists()


    @patch('videos_app.tasks.process_video_to_hls')
    def test_convert_video_to_hls_removes_thumbnail_file_on_error(
        self,
        mocked_process_video_to_hls,
    ):
        """Test that failed conversion removes the generated thumbnail file."""

        mocked_process_video_to_hls.side_effect = RuntimeError('FFmpeg failed')
        video = self.create_video_with_processing_files()
        thumbnail_path = Path(settings.MEDIA_ROOT) / video.thumbnail.name

        convert_video_to_hls(video.id)

        assert not thumbnail_path.exists()


    @patch('videos_app.tasks.clear_video_list_cache')
    @patch('videos_app.tasks.process_video_to_hls')
    def test_convert_video_to_hls_clears_video_list_cache_on_success(
        self,
        _mocked_process_video_to_hls,
        mocked_clear_video_list_cache,
    ):
        """Test that successful conversion clears the video list cache."""

        video = self.create_video_for_tasks()

        convert_video_to_hls(video.id)

        assert mocked_clear_video_list_cache.call_count == 2


    @patch('videos_app.tasks.clear_video_list_cache')
    @patch('videos_app.tasks.process_video_to_hls')
    def test_convert_video_to_hls_clears_video_list_cache_on_error(
        self,
        mocked_process_video_to_hls,
        mocked_clear_video_list_cache,
    ):
        """Test that failed conversion clears the video list cache."""

        mocked_process_video_to_hls.side_effect = RuntimeError('FFmpeg failed')
        video = self.create_video_for_tasks()

        convert_video_to_hls(video.id)

        assert mocked_clear_video_list_cache.call_count == 2


    @patch('videos_app.tasks.clear_video_list_cache')
    @patch('videos_app.tasks.process_video_to_hls')
    def test_convert_video_to_hls_does_not_clear_cache_for_unknown_video_id(
        self,
        mocked_process_video_to_hls,
        mocked_clear_video_list_cache,
    ):
        """Test that unknown video ids do not clear the video list cache."""

        convert_video_to_hls(999999)

        mocked_process_video_to_hls.assert_not_called()
        mocked_clear_video_list_cache.assert_not_called()