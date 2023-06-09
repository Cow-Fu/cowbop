from typing import Optional
from YouTube import YouTubeVideo, YouTubeManager


class QueueManager:
    def __init__(self):
        self._queue = []
        self._yt_manager = YouTubeManager()

    def pop(self, index=0) -> YouTubeVideo:
        return self._queue.pop(index)

    def get(self, index) -> Optional[YouTubeVideo]:
        if not index < len(self._queue):
            return None
        return self._queue[index]

    def get_next(self) -> YouTubeVideo:
        return self._queue[0]

    async def add(self, interaction, url) -> bool:
        video: YouTubeVideo
        video = await self._yt_manager.get_video(interaction, url)
        self._queue.append(video)
        return True

    def is_empty(self) -> bool:
        return not bool(self._queue)

    def length(self) -> int:
        return len(self._queue)

    def clear(self):
        self._queue.clear()
