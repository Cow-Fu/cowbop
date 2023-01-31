from pytube import YouTube
from dataclasses import dataclass
from nextcord import Interaction


@dataclass
class YouTubeVideo:
    interaction: Interaction
    video: YouTube
