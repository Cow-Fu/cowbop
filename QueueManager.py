import YouTubeVideoBuilder


class QueueManager:
    def __init__(self):
        self._queue = []

    def pop(self):
        return self.queue.pop()

    def get(self, index=0):
        return self.queue[index]

    def add(self, song):
        self.queue.append(song)
