"""Serializers for the Videoflix video API."""

from rest_framework import serializers

from videos_app.models import Video


class VideoSerializer(serializers.ModelSerializer):
    """Serialize video metadata for the video list endpoint."""

    thumbnail_url = serializers.SerializerMethodField()

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


    def get_thumbnail_url(self, video):
        """Return the local thumbnail URL for the frontend."""

        if not video.thumbnail:
            return ''

        return video.thumbnail.url