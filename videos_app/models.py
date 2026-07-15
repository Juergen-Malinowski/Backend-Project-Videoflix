"""Database models for the Videoflix videos app."""

from pathlib import Path
from shutil import move, rmtree

from django.conf import settings
from django.db import models


def video_source_upload_path(instance, filename):
    """Return the temporary upload path for original video files."""

    return f'videos/temp/{filename}'


def video_thumbnail_upload_path(instance, filename):
    """Return the upload path for generated video thumbnails."""

    return f'videos/{instance.id}/thumbnail/{filename}'


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

    CATEGORY_ACTION = 'Action'
    CATEGORY_ADVENTURE = 'Adventure'
    CATEGORY_ANIMATION = 'Animation'
    CATEGORY_COMEDY = 'Comedy'
    CATEGORY_CRIME = 'Crime'
    CATEGORY_DOCUMENTARY = 'Documentary'
    CATEGORY_DRAMA = 'Drama'
    CATEGORY_FAMILY = 'Family'
    CATEGORY_FANTASY = 'Fantasy'
    CATEGORY_HISTORY = 'History'
    CATEGORY_HORROR = 'Horror'
    CATEGORY_MYSTERY = 'Mystery'
    CATEGORY_NATURE = 'Nature'
    CATEGORY_ROMANCE = 'Romance'
    CATEGORY_SCIENCE_FICTION = 'Science Fiction'
    CATEGORY_SPORTS = 'Sports'
    CATEGORY_THRILLER = 'Thriller'
    CATEGORY_TRAVEL = 'Travel'

    CATEGORY_CHOICES = [
        (CATEGORY_ACTION, 'Action'),
        (CATEGORY_ADVENTURE, 'Adventure'),
        (CATEGORY_ANIMATION, 'Animation'),
        (CATEGORY_COMEDY, 'Comedy'),
        (CATEGORY_CRIME, 'Crime'),
        (CATEGORY_DOCUMENTARY, 'Documentary'),
        (CATEGORY_DRAMA, 'Drama'),
        (CATEGORY_FAMILY, 'Family'),
        (CATEGORY_FANTASY, 'Fantasy'),
        (CATEGORY_HISTORY, 'History'),
        (CATEGORY_HORROR, 'Horror'),
        (CATEGORY_MYSTERY, 'Mystery'),
        (CATEGORY_NATURE, 'Nature'),
        (CATEGORY_ROMANCE, 'Romance'),
        (CATEGORY_SCIENCE_FICTION, 'Science Fiction'),
        (CATEGORY_SPORTS, 'Sports'),
        (CATEGORY_THRILLER, 'Thriller'),
        (CATEGORY_TRAVEL, 'Travel'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()

    thumbnail = models.ImageField(
        upload_to=video_thumbnail_upload_path,
        blank=True,
    )

    category = models.CharField(
        max_length=100,
        choices=CATEGORY_CHOICES,
    )

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


    def delete(self, *args, **kwargs):
        """Delete the video and remove its media directory."""

        video_media_dir = self.get_video_media_dir()

        super().delete(*args, **kwargs)

        if video_media_dir.exists():
            rmtree(video_media_dir)


    def get_video_media_dir(self):
        """Return the media directory for this video."""

        return Path(settings.MEDIA_ROOT) / 'videos' / str(self.id)