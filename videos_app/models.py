"""Database models for the Videoflix videos app."""

from django.db import models


class Video(models.Model):
    """Represent a video with metadata used by the video API."""

    title = models.CharField(max_length=255)
    description = models.TextField()
    thumbnail_url = models.URLField(max_length=500)
    category = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Define default ordering for video records."""

        ordering = ['id']


    def __str__(self):
        """Return the video title as string representation."""

        return self.title