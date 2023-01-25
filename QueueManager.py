from YouTubeVideoBuilder import YoutubeVideoBuilder


class QueueManager:
    def __init__(self):
        self._queue = []

    def pop(self):
        return self.queue.pop()

    def get(self, index):
        return self.queue[index]

    def get_next(self):
        return self.get(0)

    def add(self, interaction, url):
        video = YoutubeVideoBuilder.build(interaction, url)
        self.queue.append(video)

    def is_empty(self):
        return not bool(self._queue)
