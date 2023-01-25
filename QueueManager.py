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

    def add(self, interaction, url):
        video = YoutubeVideoBuilder.build(interaction, url)
        self.queue.append(video)

    def is_empty(self):
        return not bool(self._queue)
