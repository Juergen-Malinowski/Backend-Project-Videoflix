"""Reusable test helpers for Videoflix video API tests."""

from rest_framework_simplejwt.tokens import AccessToken

from auth_app.tests.mixins import AuthTestMixin
from videos_app.models import Video


class VideoTestMixin(AuthTestMixin):
    """Provide reusable helpers for video API tests."""

    def authenticate_client(self):
        """Authenticate the API client with an access token cookie."""

        access_token = AccessToken.for_user(self.user)
        self.client.cookies['access_token'] = str(access_token)


    def create_video(self, title='Movie Title', category='Drama'):
        """Create and return a video object for video API tests."""

        return Video.objects.create(
            title=title,
            description='Movie Description',
            thumbnail_url='http://example.com/media/thumbnail/image.jpg',
            category=category,
        )