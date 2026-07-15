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


def get_thumbnail_output_path(video):
    """Return the generated thumbnail output path for a video."""

    return (
        Path(settings.MEDIA_ROOT)
        / 'videos'
        / str(video.id)
        / 'thumbnail'
        / 'thumbnail.jpg'
    )


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


def build_ffmpeg_thumbnail_command(source_path, thumbnail_path):
    """Build the FFmpeg command for thumbnail generation."""

    return [
        'ffmpeg',
        '-ss',
        '00:00:01',
        '-i',
        str(source_path),
        '-frames:v',
        '1',
        str(thumbnail_path),
    ]


def run_ffmpeg_command(command):
    """Run an FFmpeg command."""

    subprocess.run(command, check=True)


def generate_video_thumbnail(video):
    """Generate and assign a thumbnail for a video."""

    thumbnail_path = get_thumbnail_output_path(video)
    thumbnail_path.parent.mkdir(parents=True, exist_ok=True)

    command = build_ffmpeg_thumbnail_command(
        video.source_file.path,
        thumbnail_path,
    )
    run_ffmpeg_command(command)

    video.thumbnail.name = (
        f'videos/{video.id}/thumbnail/thumbnail.jpg'
    )
    video.save(update_fields=['thumbnail'])


def process_video_to_hls(video):
    """Convert a video source file to HLS output files and thumbnail."""

    if not video.source_file:
        raise ValueError('Video source file is required.')

    generate_video_thumbnail(video)

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