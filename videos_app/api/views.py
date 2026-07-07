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
            videos = Video.objects.all().order_by('-created_at')
            serializer = VideoSerializer(videos, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception:
            return Response(
                {'detail': 'Internal server error.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class VideoManifestView(APIView):
    pass


class VideoSegmentView(APIView):
    pass