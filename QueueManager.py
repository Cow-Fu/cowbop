from YouTubeVideoBuilder import YoutubeVideoBuilder
from typing import Optional
import YouTubeVideo


class QueueManager:
    def __init__(self):
        self._queue = []

    def pop(self, index=0) -> YouTubeVideo:
        return self._queue.pop(index)

    def get(self, index) -> Optional[YouTubeVideo]:
        if not index < len(self._queue):
            return None
        return self._queue[index]

    def get_next(self) -> YouTubeVideo:
        return self._queue[0]

    def add(self, interaction, url) -> bool:
        video: YouTubeVideo
        video = YoutubeVideoBuilder.build(interaction, url)
        self._queue.append(video)
        return True

    def is_empty(self) -> bool:
        return not bool(self._queue)

    def length(self) -> int:
        return len(self._queue)

    def clear(self):
        self._queue.clear()
