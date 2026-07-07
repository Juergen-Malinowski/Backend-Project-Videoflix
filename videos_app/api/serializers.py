"""Serializers for the Videoflix video API."""

from rest_framework import serializers

from videos_app.models import Video


class VideoSerializer(serializers.ModelSerializer):
    """Serialize video metadata for the video list endpoint."""

    class Meta:
        """Define serialized video fields."""

        model = Video
        fields = [
            'id',
            'created_at',
            'title',
            'description',
            'thumbnail_url',
            'category',
        ]