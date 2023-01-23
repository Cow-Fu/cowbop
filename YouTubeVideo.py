from pytube import YouTube
from dataclasses import dataclass


@dataclass
class YoutubeVideo:
    url: str
    video: YouTube
