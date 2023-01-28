from pytube import YouTube
from dataclasses import dataclass
from nextcord import Interaction


@dataclass
class YoutubeVideo:
    interaction: Interaction
    video: YouTube
