import yt_dlp
from typing import Optional, List
from nextcord import Interaction
from dataclasses import dataclass


@dataclass
class YouTubeVideo:
    interaction: Interaction
    id: str
    webpage_url: str
    title: str
    duration: int
    duration_string: str


class YoutubeVideoBuilder:
    @staticmethod
    def build(interaction: Interaction, ydl_obj: dict) -> YouTubeVideo:
        return YouTubeVideo(interaction,
                            ydl_obj['id'],
                            ydl_obj['webpage_url'],
                            ydl_obj['title'],
                            ydl_obj['duration'],
                            ydl_obj['duration_string']
                            )


class YouTubeManager:
    class MyLogger:
        def debug(self, msg):
            # For compatibility with youtube-dl, both debug and info are passed
            # into debug. You can distinguish them by the prefix '[debug] '
            if msg.startswith('[debug] '):
                pass
            else:
                pass

        def info(self, msg):
            pass

        def warning(self, msg):
            pass

        def error(self, msg):
            print(msg)

    _ydl_opts = {
        'logger': MyLogger(),
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    def __init__(self):
        self._yt_builder = YoutubeVideoBuilder()

    def get_video(self, interaction, url: str) -> Optional[YouTubeVideo]:
        x = self.get_video_info(url)
        if not x:
            return None
        return YoutubeVideoBuilder.build(interaction, x)

    def download(video: YouTubeVideo):
        with yt_dlp.YoutubeDL(YouTubeManager._ydl_opts) as ydl:
            ydl.download(video.webpage_url)
    def search(self, interaction: Interaction, query: str, count=5):
        querystr = f"ytsearch{count}:{query}"
        x = self.get_video_info(querystr)
        if not x:
            interaction.send("idk man, ask @Cow_Fu what broke this time")
            return
        results = []
        for entry in x["entries"]:
            results.append(YoutubeVideoBuilder.build(interaction, entry))
        return results

    def get_video_info(self, url=str) -> Optional[dict]:
        """
        Raises:
            yt_dlp.utils.DownloadError: Unable to download the video
        """
        with yt_dlp.YoutubeDL(YouTubeManager._ydl_opts) as ydl:
            try:
                return ydl.extract_info(url, download=False)
            except yt_dlp.utils.DownloadError as e:
                return None
