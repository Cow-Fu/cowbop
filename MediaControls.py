from QueueManager import QueueManager
from YouTubeVideo import YouTubeVideo
from nextcord.ext import tasks
import nextcord


class MediaController:
    def __init__(self):
        self._queue = QueueManager()
        self._volume = 5

    async def play(self, interaction: nextcord.Interaction, url: str):
        if not interaction.guild.voice_client:
            if not interaction.user.voice:
                interaction.send("You must first join a voice channel!", ephemeral=True)
                return
            await interaction.user.voice.channel.connect()
        self._queue.add(self, interaction, url)
        if not self.song_loop.is_running():
            self.song_loop.start()

    async def pause(self, interaction: nextcord.Interaction):
        vc: nextcord.VoiceClient = interaction.guild.voice_client
        vc.pause()
        await interaction.send("Playback has been paused.", delete_after=60)

    async def skip(self, interaction: nextcord.Interaction):
        vc: nextcord.VoiceClient = interaction.guild.voice_client
        vc.stop()
        await interaction.send("Song skipped.", delete_after=60)

    async def stop(self, interaction: nextcord.Interaction):
        vc: nextcord.VoiceClient = interaction.guild.voice_client
        vc.stop()
        self._queue.clear()
        await interaction.send("Stopped. Any remaining songs have been removed", delete_after=60)

    async def volume(self, interaction: nextcord.Interaction, volume: int):
        if not 0 < volume <= 100:
            await interaction.send("Value must be between 1 and 100.", delete_after=60)
            return
        self._volume = volume
        if interaction.guild.voice_client:
            interaction.guild.voice_client.source.volume = self._volume / 100
        await interaction.send(f"Volume has beeen set to {volume}%", delete_after=60)

    async def queue(self, interaction: nextcord.Interaction):
        text = []
        lines = 5
        if self._queue.length() < lines:
            lines = self._queue.length()
        for i in range(lines):
            video: YouTubeVideo = self._queue.get(i)
            text.append(f"{video.video.title}")
        await interaction.send("\n".join(text))

    def _download_video(self, yt_video: YouTubeVideo):
        video = yt_video.video
        try:
            stream = video.streams.filter(mime_type="audio/mp4").last()
        except Exception:
            video.bypass_age_gate()
            stream = video.streams.filter(mime_type="audio/mp4").last()
        try:
            stream.download(filename="file.mp4")
        except Exception as e:
            print(f"{e}\n{type(e)}")
            return False
        return True

    async def _play_music(self, video: YouTubeVideo):
        inter = video.interaction
        vc: nextcord.VoiceClient = inter.guild.voice_client
        user_voice_client = inter.user.voice
        if not vc: 
            await user_voice_client.channel.connect()
        if not vc.is_connected():
            if not user_voice_client.channel.connect():
                await inter.send("You need to be connected to a voice channel!", 
                                 ephemeral=True, delete_after=60)
                return
            await user_voice_client.channel.connect()
        if not self._download_video(video):
            await inter.send("Unable to download video.")
            return
        audio = nextcord.PCMVolumeTransformer(nextcord.FFmpegPCMAudio("file.mp4", options="-vn"))
        audio.volume = self._volume / 100
        vc.play(audio)

    @tasks.loop(1)
    async def song_loop(self):
        if self._queue.is_empty():
            self.song_loop.stop()
            return
        video: YouTubeVideo = self._queue.pop(0)
        await self._play_music(video)
