"""Tests for video caching helpers."""

import pytest

from videos_app.cache import clear_video_list_cache


@pytest.mark.django_db
class TestVideoCache:
    """Test video cache helper behavior."""

    def test_clear_video_list_cache_does_not_raise_error(self):
        """Test that clearing the video list cache is safe to call."""

        clear_video_list_cache()