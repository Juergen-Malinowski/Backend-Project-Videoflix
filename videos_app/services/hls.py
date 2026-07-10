"""Services for HLS video processing."""

import shutil
import subprocess

from pathlib import Path

from django.conf import settings


HLS_RESOLUTIONS = {
    '480p': '854x480',
    '720p': '1280x720',
    '1080p': '1920x1080',
}


def get_hls_output_dir(video, resolution):
    """Return the HLS output directory for a video resolution."""

    return Path(settings.MEDIA_ROOT) / 'videos' / str(video.id) / resolution


def build_ffmpeg_hls_command(source_path, output_dir, resolution):
    """Build the FFmpeg command for HLS conversion."""

    return [
        'ffmpeg',
        '-i',
        str(source_path),
        '-vf',
        f'scale={resolution}',
        '-codec:v',
        'libx264',
        '-codec:a',
        'aac',
        '-hls_time',
        '10',
        '-hls_playlist_type',
        'vod',
        '-hls_segment_filename',
        str(output_dir / '%03d.ts'),
        str(output_dir / 'index.m3u8'),
    ]


def run_ffmpeg_command(command):
    """Run an FFmpeg command."""

    subprocess.run(command, check=True)


def process_video_to_hls(video):
    """Convert a video source file to HLS output files."""

    if not video.source_file:
        raise ValueError('Video source file is required.')

    for resolution, scale in HLS_RESOLUTIONS.items():
        output_dir = get_hls_output_dir(video, resolution)
        output_dir.mkdir(parents=True, exist_ok=True)

        command = build_ffmpeg_hls_command(
            video.source_file.path,
            output_dir,
            scale,
        )
        run_ffmpeg_command(command)


def clean_hls_output(video):
    """Remove generated HLS output folders for a video."""

    for resolution in HLS_RESOLUTIONS:
        output_dir = get_hls_output_dir(video, resolution)

        if output_dir.exists():
            shutil.rmtree(output_dir)