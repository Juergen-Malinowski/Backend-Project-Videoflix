"""Reusable test helpers for Videoflix video API tests."""

from pathlib import Path

from rest_framework_simplejwt.tokens import AccessToken

from auth_app.tests.mixins import AuthTestMixin
from videos_app.models import Video


class VideoTestMixin(AuthTestMixin):
    """Provide reusable helpers for video API tests."""

    def authenticate_client(self):
        """Authenticate the API client with an access token cookie."""

        access_token = AccessToken.for_user(self.user)
        self.client.cookies['access_token'] = str(access_token)


    def create_video(self, title='Movie Title', category='Drama', processing_status=Video.STATUS_READY):
        """Create and return a video object for video API tests."""

        return Video.objects.create(
            title=title,
            description='Movie Description',
            thumbnail_url='http://example.com/media/thumbnail/image.jpg',
            category=category,
            processing_status=processing_status,
        )


    def create_manifest_file(self, video, resolution='720p'):
        """Create and return a test HLS manifest file path."""

        manifest_dir = Path('videos') / str(video.id) / resolution
        full_manifest_dir = Path(self.media_root) / manifest_dir
        full_manifest_dir.mkdir(parents=True, exist_ok=True)

        manifest_path = full_manifest_dir / 'index.m3u8'
        manifest_path.write_text(
            '#EXTM3U\n'
            '#EXT-X-VERSION:3\n'
            '#EXTINF:10.0,\n'
            'segment_000.ts\n',
            encoding='utf-8',
        )

        return manifest_path


    def create_segment_file(self, video, resolution='720p', segment='000.ts'):
        """Create and return a test HLS TS segment file path."""

        segment_dir = Path('videos') / str(video.id) / resolution
        full_segment_dir = Path(self.media_root) / segment_dir
        full_segment_dir.mkdir(parents=True, exist_ok=True)

        segment_path = full_segment_dir / segment
        segment_path.write_bytes(b'test-ts-segment-content')

        return segment_path