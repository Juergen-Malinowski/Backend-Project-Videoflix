"""Background tasks for video processing."""

import django_rq

from videos_app.cache import clear_video_list_cache
from videos_app.models import Video
from videos_app.services.hls import clean_video_processing_files, process_video_to_hls


@django_rq.job
def convert_video_to_hls(video_id):
    """Convert a video source file to HLS output files and thumbnail."""

    try:
        video = Video.objects.get(id=video_id)

    except Video.DoesNotExist:
        return None

    mark_video_as_processing(video)

    try:
        process_video_to_hls(video)

    except Exception as error:
        mark_video_as_failed(video, error)
        clean_video_processing_files(video)

        return None

    mark_video_as_ready(video)

    return None


def mark_video_as_processing(video):
    """Mark a video as currently being processed."""

    video.processing_status = Video.STATUS_PROCESSING
    video.processing_error = ''
    video.save(update_fields=['processing_status', 'processing_error'])
    clear_video_list_cache()


def mark_video_as_ready(video):
    """Mark a video as ready after successful processing."""

    video.processing_status = Video.STATUS_READY
    video.processing_error = ''
    video.save(update_fields=['processing_status', 'processing_error'])
    clear_video_list_cache()


def mark_video_as_failed(video, error):
    """Mark a video as failed after a processing error."""

    video.processing_status = Video.STATUS_FAILED
    video.processing_error = str(error)
    video.save(update_fields=['processing_status', 'processing_error'])
    clear_video_list_cache()
