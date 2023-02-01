import pytube
from nextcord import Interaction
from YouTubeVideo import YouTubeVideo


class YouTubeVideoError(Exception):
    pass


class YoutubeVideoBuilder:
    @staticmethod
    def build(interaction: Interaction, url: str) -> YouTubeVideo:
        try:
            return YouTubeVideo(interaction, pytube.YouTube(url, use_oauth=True))
        except pytube.exceptions.RegexMatchError:
            interaction.send("Not a valid Youtube url")
