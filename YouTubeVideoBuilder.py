import pytube
import nextcord


class YouTubeVideoError(Exception):
    pass


class YoutubeVideoBuilder:
    def __init__(self):
        pass

    def build(self, interaction: nextcord.Interaction, url: str):
        try:
            return pytube.YouTube(url, use_oauth=True)
        except Exception:
            raise YouTubeVideoError
