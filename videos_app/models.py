"""Database models for the Videoflix videos app."""

from pathlib import Path
from shutil import move

from django.conf import settings
from django.db import models


def video_source_upload_path(instance, filename):
    """Return the temporary upload path for original video files."""

    return f'videos/temp/{filename}'


class Video(models.Model):
    """Represent a video with metadata and processing state."""

    STATUS_PENDING = 'pending'
    STATUS_PROCESSING = 'processing'
    STATUS_READY = 'ready'
    STATUS_FAILED = 'failed'

    PROCESSING_STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_PROCESSING, 'Processing'),
        (STATUS_READY, 'Ready'),
        (STATUS_FAILED, 'Failed'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    thumbnail_url = models.URLField(max_length=500)
    category = models.CharField(max_length=100)

    source_file = models.FileField(
        upload_to=video_source_upload_path,
        blank=True,
    )

    processing_status = models.CharField(
        max_length=20,
        choices=PROCESSING_STATUS_CHOICES,
        default=STATUS_PENDING,
    )

    processing_error = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Define default ordering and admin labels for video records."""

        ordering = ['id']
        verbose_name = 'Video'
        verbose_name_plural = 'Videos'


    def __str__(self):
        """Return the video title as string representation."""

        return self.title

    
    def save(self, *args, **kwargs):
        """Save the video and move source files into the final media path."""

        super().save(*args, **kwargs)

        if self.source_file and self.is_source_file_temporary():
            self.move_source_file_to_final_path()


    def is_source_file_temporary(self):
        """Return whether the source file is still in the temp folder."""

        return self.source_file.name.startswith('videos/temp/')


    def move_source_file_to_final_path(self):
        """Move the uploaded source file into the video source directory."""

        current_path = Path(settings.MEDIA_ROOT) / self.source_file.name
        final_name = self.get_final_source_file_name()
        final_path = Path(settings.MEDIA_ROOT) / final_name

        final_path.parent.mkdir(parents=True, exist_ok=True)
        move(current_path, final_path)

        self.source_file.name = final_name
        super().save(update_fields=['source_file'])


    def get_final_source_file_name(self):
        """Return the final source file name for this video."""

        filename = Path(self.source_file.name).name

        return f'videos/{self.id}/source/{filename}'