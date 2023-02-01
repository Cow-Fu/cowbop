import nextcord
from nextcord.ext import commands, tasks
from QueueManager import QueueManager
from YouTubeVideo import YouTubeVideo
import pytube


class MusicBotCog(commands.Cog):
    def __init__(self, bot: commands.Bot, bot_id: int):
        self._bot = bot
        self._bot_id = bot_id
        self._volume = 5
        self._queue = QueueManager()

    @nextcord.slash_command(description="Adds music to the queue")
    async def play(self, interaction: nextcord.Interaction, url: str):
        if not interaction.guild.voice_client:
            if not interaction.user.voice:
                interaction.send("You must first join a voice channel", ephemeral=True)
                return
            await interaction.user.voice.channel.connect()
        self._queue.add(interaction, url)
        if not self.song_loop.is_running():
            self.song_loop.start()

    @nextcord.slash_command(description="Pauses current song")
    async def pause(self, interaction: nextcord.Interaction):
        vc: nextcord.VoiceClient = interaction.guild.voice_client
        vc.pause()
        await interaction.send("Playback has been paused", ephemeral=True, delete_after=10)

    @nextcord.slash_command(description="Resumes current song")
    async def resume(self, interaction: nextcord.Interaction):
        vc: nextcord.VoiceClient = interaction.guild.voice_client
        vc.resume()
        await interaction.send("Playback has been resumed", ephemeral=True, delete_after=10)

    @nextcord.slash_command(description="Stops playing music")
    async def stop(self, interaction: nextcord.Interaction):
        vc: nextcord.VoiceClient = interaction.guild.voice_client
        vc.stop()
        await interaction.send("Playback has been stopped", ephemeral=True, delete_after=10)

    @nextcord.slash_command(description="Skips current song")
    async def skip(self, interaction: nextcord.Interaction):
        pass

    @nextcord.slash_command(description="Volume")
    async def volume(self, interaction: nextcord.Interaction, volume: int):
        if not 0 < volume <= 100:
            await interaction.send("Value must be between 1 and 100", delete_after=10)
            return
        interaction.guild.voice_client.source.volume = volume / 100
        await interaction.send(f"Volume has been set to {volume}%", delete_after=10)

    @nextcord.slash_command(description="Displays the current song queue")
    async def queue(self, interaction: nextcord.Interaction):
        text = ""
        lines = 5
        if self._queue.length() < lines:
            lines = self._queue.length()
        video: YouTubeVideo
        for i in range(lines):
            video = self._queue.get(i)
            text += f"{video.video.title}\n"
        await interaction.send(text)

    def _download_video(self, yt_video: YouTubeVideo):
        video = yt_video.video
        stream: pytube.Stream
        try:
            stream = video.streams.filter(mime_type="audio/mp4").last()
        except Exception:
            video.bypass_age_gate()
            stream = video.streams.filter(mime_type="audio/mp4").last()
        try:
            stream.download(filename="file.mp4")
        except Exception as e:
            return False
        return True

    async def _play_music(self, video: YouTubeVideo):
        inter = video.interaction
        vc: nextcord.VoiceClient = inter.guild.voice_client
        if not vc:
            await inter.user.voice.channel.connect()
        if not vc.is_connected():
            if not video.interaction.user.voice:
                await inter.send("You need to be connected to a voice channel!", ephemeral=True)
                return
            await inter.user.voice.channel.connect()
        if not self._download_video(video):
            await inter.send("Unable to download video")
            return
        audio = nextcord.PCMVolumeTransformer(nextcord.FFmpegPCMAudio("file.mp4", options="-vn"))
        audio.volume = self._volume / 100
        video.interaction.guild.voice_client.play(audio)

    @tasks.loop(seconds=1)
    async def song_loop(self):
        if self._queue.is_empty():
            self.song_loop.stop()
            return
        item: YouTubeVideo
        item = self._queue.pop(0)
        await self._play_music(item)


