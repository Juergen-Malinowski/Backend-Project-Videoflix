"""Tests for video background processing tasks."""

from unittest.mock import patch

import pytest

from videos_app.models import Video
from videos_app.tasks import convert_video_to_hls


@pytest.mark.django_db
class TestVideoTasks:
    """Test video processing background tasks."""

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

        video = self.create_video()

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

        video = self.create_video(
            processing_status=Video.STATUS_FAILED,
            processing_error='Old FFmpeg error',
        )

        convert_video_to_hls(video.id)

        video.refresh_from_db()
        assert video.processing_error == ''


    @patch('videos_app.tasks.process_video_to_hls')
    def test_convert_video_to_hls_calls_hls_processing_service(self, mocked_process_video_to_hls):
        """Test that conversion calls the HLS processing service."""

        video = self.create_video()

        convert_video_to_hls(video.id)

        mocked_process_video_to_hls.assert_called_once()
        processed_video = mocked_process_video_to_hls.call_args.args[0]

        assert processed_video.id == video.id


    @patch('videos_app.tasks.process_video_to_hls')
    def test_convert_video_to_hls_sets_status_to_ready_on_success(self, _mocked_process_video_to_hls):
        """Test that successful conversion marks the video as ready."""

        video = self.create_video()

        convert_video_to_hls(video.id)

        video.refresh_from_db()

        assert video.processing_status == Video.STATUS_READY


    @patch('videos_app.tasks.process_video_to_hls')
    @patch('videos_app.tasks.clean_hls_output')
    def test_convert_video_to_hls_sets_status_to_failed_on_error(
        self,
        _mocked_clean_hls_output,
        mocked_process_video_to_hls,
    ):
        """Test that failed conversion marks the video as failed."""

        mocked_process_video_to_hls.side_effect = RuntimeError('FFmpeg failed')
        video = self.create_video()

        convert_video_to_hls(video.id)

        video.refresh_from_db()

        assert video.processing_status == Video.STATUS_FAILED


    @patch('videos_app.tasks.process_video_to_hls')
    @patch('videos_app.tasks.clean_hls_output')
    def test_convert_video_to_hls_stores_error_message_on_error(
        self,
        _mocked_clean_hls_output,
        mocked_process_video_to_hls,
    ):
        """Test that failed conversion stores the processing error."""

        mocked_process_video_to_hls.side_effect = RuntimeError('FFmpeg failed')
        video = self.create_video()

        convert_video_to_hls(video.id)

        video.refresh_from_db()

        assert video.processing_error == 'FFmpeg failed'


    @patch('videos_app.tasks.process_video_to_hls')
    @patch('videos_app.tasks.clean_hls_output')
    def test_convert_video_to_hls_cleans_hls_output_on_error(
        self,
        mocked_clean_hls_output,
        mocked_process_video_to_hls,
    ):
        """Test that failed conversion removes partial HLS output."""

        mocked_process_video_to_hls.side_effect = RuntimeError('FFmpeg failed')
        video = self.create_video()

        convert_video_to_hls(video.id)

        mocked_clean_hls_output.assert_called_once()
        cleaned_video = mocked_clean_hls_output.call_args.args[0]

        assert cleaned_video.id == video.id


    def create_video(
        self,
        processing_status=Video.STATUS_PENDING,
        processing_error='',
    ):
        """Create and return a video for task tests."""

        return Video.objects.create(
            title='Movie Title',
            description='Movie Description',
            thumbnail_url='http://example.com/media/thumbnail/image.jpg',
            category='Drama',
            processing_status=processing_status,
            processing_error=processing_error,
        )