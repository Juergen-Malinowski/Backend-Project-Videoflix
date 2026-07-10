"""API views for the Videoflix videos app."""

from pathlib import Path

from django.conf import settings
from django.http import HttpResponse

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_app.api.authentication import CookieJWTAuthentication
from videos_app.api.serializers import VideoSerializer
from videos_app.models import Video


class VideoListView(APIView):
    """Return metadata for all available videos."""

    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return all video metadata ordered by creation date descending."""

        try:
            videos = Video.objects.filter(processing_status=Video.STATUS_READY).order_by('-created_at')
            serializer = VideoSerializer(videos, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception:
            return Response(
                {'detail': 'Internal server error.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class VideoManifestView(APIView):
    """Return an HLS manifest file for a video and resolution."""

    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id, resolution):
        """Return the requested HLS manifest file."""

        try:
            Video.objects.get(id=movie_id)
            manifest_path = self.get_manifest_path(movie_id, resolution)

            if not manifest_path.is_file():
                return Response(status=status.HTTP_404_NOT_FOUND)

            content = manifest_path.read_text(encoding='utf-8')

            return HttpResponse(
                content,
                content_type='application/vnd.apple.mpegurl',
            )

        except Video.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        except Exception:
            return Response(
                {'detail': 'Internal server error.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def get_manifest_path(self, movie_id, resolution):
        """Return the expected HLS manifest path."""

        return (
            Path(settings.MEDIA_ROOT)
            / 'videos'
            / str(movie_id)
            / resolution
            / 'index.m3u8'
        )


class VideoSegmentView(APIView):
    """Return an HLS video segment file for a video and resolution."""

    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id, resolution, segment):
        """Return the requested HLS video segment file."""

        try:
            Video.objects.get(id=movie_id)
            segment_path = self.get_segment_path(
                movie_id,
                resolution,
                segment,
            )

            if not segment_path.is_file():
                return Response(status=status.HTTP_404_NOT_FOUND)

            content = segment_path.read_bytes()

            return HttpResponse(
                content,
                content_type='video/MP2T',
            )

        except Video.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        except Exception:
            return Response(
                {'detail': 'Internal server error.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def get_segment_path(self, movie_id, resolution, segment):
        """Return the expected HLS video segment path."""

        return (
            Path(settings.MEDIA_ROOT)
            / 'videos'
            / str(movie_id)
            / resolution
            / segment
        )