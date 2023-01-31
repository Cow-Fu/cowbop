from YouTubeVideoBuilder import YoutubeVideoBuilder
import YouTubeVideo


class QueueManager:
    def __init__(self):
        self._queue = []

    def pop(self, index=0) -> YouTubeVideo:
        return self._queue.pop(index)

    def get(self, index) -> YouTubeVideo:
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
