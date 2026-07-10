"""Tests for HLS video processing services."""

from pathlib import Path
from unittest.mock import patch

import pytest

from django.conf import settings
from django.core.files.base import ContentFile

from videos_app.models import Video
from videos_app.services.hls import (
    HLS_RESOLUTIONS,
    build_ffmpeg_hls_command,
    clean_hls_output,
    get_hls_output_dir,
    process_video_to_hls,
)


@pytest.mark.django_db
class TestHlsProcessing:
    """Test HLS processing service behavior."""

    def test_hls_resolutions_contain_required_outputs(self):
        """Test that all required HLS resolutions are configured."""

        assert '480p' in HLS_RESOLUTIONS
        assert '720p' in HLS_RESOLUTIONS
        assert '1080p' in HLS_RESOLUTIONS


    def test_get_hls_output_dir_returns_resolution_directory(self):
        """Test that HLS output path points to the resolution directory."""

        video = self.create_video()

        output_dir = get_hls_output_dir(video, '720p')

        assert output_dir == Path(settings.MEDIA_ROOT) / 'videos' / str(video.id) / '720p'


    def test_build_ffmpeg_hls_command_contains_source_file(self):
        """Test that the FFmpeg command contains the source file path."""

        video = self.create_video_with_source_file()
        output_dir = get_hls_output_dir(video, '720p')

        command = build_ffmpeg_hls_command(
            video.source_file.path,
            output_dir,
            '1280x720',
        )

        assert video.source_file.path in command


    def test_build_ffmpeg_hls_command_contains_manifest_path(self):
        """Test that the FFmpeg command writes an index manifest."""

        output_dir = Path(settings.MEDIA_ROOT) / 'videos' / '1' / '720p'

        command = build_ffmpeg_hls_command(
            '/tmp/source.mp4',
            output_dir,
            '1280x720',
        )

        assert str(output_dir / 'index.m3u8') in command


    def test_build_ffmpeg_hls_command_uses_segment_pattern(self):
        """Test that the FFmpeg command uses documented segment filenames."""

        output_dir = Path(settings.MEDIA_ROOT) / 'videos' / '1' / '720p'

        command = build_ffmpeg_hls_command(
            '/tmp/source.mp4',
            output_dir,
            '1280x720',
        )

        assert str(output_dir / '%03d.ts') in command


    def test_build_ffmpeg_hls_command_uses_ten_second_segments(self):
        """Test that the FFmpeg command uses ten second HLS segments."""

        output_dir = Path(settings.MEDIA_ROOT) / 'videos' / '1' / '720p'

        command = build_ffmpeg_hls_command(
            '/tmp/source.mp4',
            output_dir,
            '1280x720',
        )

        assert '-hls_time' in command
        assert '10' in command


    @patch('videos_app.services.hls.run_ffmpeg_command')
    def test_process_video_to_hls_creates_output_directories(
        self,
        mocked_run_ffmpeg_command,
    ):
        """Test that HLS processing creates all output directories."""

        video = self.create_video_with_source_file()

        process_video_to_hls(video)

        for resolution in HLS_RESOLUTIONS:
            output_dir = get_hls_output_dir(video, resolution)

            assert output_dir.exists()


    @patch('videos_app.services.hls.run_ffmpeg_command')
    def test_process_video_to_hls_calls_ffmpeg_for_each_resolution(
        self,
        mocked_run_ffmpeg_command,
    ):
        """Test that FFmpeg is called once per configured HLS resolution."""

        video = self.create_video_with_source_file()

        process_video_to_hls(video)

        assert mocked_run_ffmpeg_command.call_count == len(HLS_RESOLUTIONS)


    def test_process_video_to_hls_rejects_missing_source_file(self):
        """Test that videos without source files cannot be processed."""

        video = self.create_video()

        with pytest.raises(ValueError, match='source file'):
            process_video_to_hls(video)


    def test_clean_hls_output_removes_resolution_directories(self):
        """Test that HLS cleanup removes generated resolution directories."""

        video = self.create_video_with_source_file()
        self.create_hls_output_directory(video, '480p')
        self.create_hls_output_directory(video, '720p')
        self.create_hls_output_directory(video, '1080p')

        clean_hls_output(video)

        assert not get_hls_output_dir(video, '480p').exists()
        assert not get_hls_output_dir(video, '720p').exists()
        assert not get_hls_output_dir(video, '1080p').exists()


    def test_clean_hls_output_keeps_source_directory(self):
        """Test that HLS cleanup keeps the original source directory."""

        video = self.create_video_with_source_file()
        source_path = Path(video.source_file.path)
        self.create_hls_output_directory(video, '720p')

        clean_hls_output(video)

        assert source_path.parent.exists()
        assert source_path.exists()


    def create_video(self):
        """Create and return a video without a source file."""

        return Video.objects.create(
            title='Movie Title',
            description='Movie Description',
            thumbnail_url='http://example.com/media/thumbnail/image.jpg',
            category='Drama',
        )


    def create_video_with_source_file(self):
        """Create and return a video with an original source file."""

        video = self.create_video()
        video.source_file.save(
            'source.mp4',
            ContentFile(b'video content'),
            save=True,
        )

        return video


    def create_hls_output_directory(self, video, resolution):
        """Create an HLS output directory with a dummy file."""

        output_dir = get_hls_output_dir(video, resolution)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / 'index.m3u8'
        output_file.write_text('#EXTM3U', encoding='utf-8')

        return output_dir