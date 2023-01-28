from YouTubeVideoBuilder import YoutubeVideoBuilder
from YouTubeVideo import YouTubeVideo


class QueueManager:
    def __init__(self):
        self._queue: YouTubeVideo
        self._queue = []

    def pop(self) -> YouTubeVideo:
        return self.queue.pop()

    def get(self, index) -> YouTubeVideo:
        return self.queue[index]

    def get_next(self) -> YouTubeVideo:
        return self.get(0)

    def add(self, interaction, url) -> bool:
        video: YouTubeVideo
        try:
            video = YoutubeVideoBuilder.build(interaction, url)
        except Exception as e:
            print(e)
            return False
        self.queue.append(video)
        return True

    def is_empty(self) -> bool:
        return not bool(self._queue)

    def length(self) -> int:
        return len(self._queue)
