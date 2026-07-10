"""Background tasks for video processing."""

import django_rq


@django_rq.job
def convert_video_to_hls(video_id):
    """Convert a video source file to HLS output files."""

    return None