import yt_dlp
from typing import Optional, List
from nextcord import Interaction
from dataclasses import dataclass
import asyncio


@dataclass
class YouTubeVideo:
    interaction: Interaction
    id: str
    webpage_url: str
    title: str
    duration: int
    duration_string: str
    channel_name: str
    _data: dict
    is_downloaded: bool = False


class YoutubeVideoBuilder:
    @staticmethod
    def build(interaction: Interaction, ydl_obj: dict) -> YouTubeVideo:
        return YouTubeVideo(interaction,
                            ydl_obj['id'],
                            ydl_obj['webpage_url'],
                            ydl_obj['title'],
                            ydl_obj['duration'],
                            ydl_obj['duration_string'],
                            ydl_obj['channel'],
                            ydl_obj
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
        'outtmpl': 'file',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    def __init__(self):
        self._yt_builder = YoutubeVideoBuilder()

    async def get_video(self, interaction, url: str) -> Optional[YouTubeVideo]:
        x = await self.extract_info(url)
        if not x:
            return None
        return YoutubeVideoBuilder.build(interaction, x)

    async def download(self, video: YouTubeVideo):
        result = await self.extract_info(video.webpage_url, download=True)
        video.is_downloaded = True
        return result

    async def search(self, interaction: Interaction, query: str, count=5):
        querystr = f"ytsearch{count}:{query}"
        x = await self.extract_info(querystr)
        if not x:
            interaction.send("idk man, ask @Cow_Fu what broke this time")
            return
        results = []
        for entry in x["entries"]:
            results.append(YoutubeVideoBuilder.build(interaction, entry))
        return results

    async def extract_info(self, url=str, download=False) -> Optional[dict]:
        """
        Raises:
            yt_dlp.utils.DownloadError: Unable to download the video
        """
        loop = asyncio.get_event_loop()
        with yt_dlp.YoutubeDL(YouTubeManager._ydl_opts) as ydl:
            try:
                return await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=download))
            except yt_dlp.utils.DownloadError as e:
                return None
