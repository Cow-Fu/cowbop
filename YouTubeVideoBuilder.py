import pytube
import nextcord
import YouTubeVideo


class YouTubeVideoError(Exception):
    pass


class YoutubeVideoBuilder:
    @staticmethod
    def build(interaction: nextcord.Interaction, url: str) -> YouTubeVideo:
        try:
            return YouTubeVideo(url, pytube.YouTube(url, use_oauth=True))
        except Exception:
            raise YouTubeVideoError
