from QueueManager import QueueManager
from YouTubeVideo import YouTubeVideo
from math import floor
import nextcord
import pytube


class SongSelectionButton(nextcord.ui.Button):
    def __init__(self, controller, value: pytube.YouTube, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.controller = controller
        self.value = value

    async def callback(self, interaction: nextcord.Interaction):
        self.controller: MediaController
        self.controller._queue.add(interaction, self.value.watch_url)
        is_queue_ongoing = True
        if not self.controller.is_loop_running:
            is_queue_ongoing = False
            await self.controller.song_loop()
        self.view.stop()
        start = f"Added {self.label}:" if is_queue_ongoing else f"Playing {self.label}:"
        title = self.value.title
        song_length = self.controller.get_time_from_seconds(self.value.length)
        await interaction.message.edit(content=f"{text} {title} ({song_length})", embed=None, view=None)
        # TODO do callback here


class SongSelectionView(nextcord.ui.View):
    def __init__(self, interaction: nextcord.Interaction, media_controller, data):
        super().__init__()
        self.interaction = interaction
        self.value = None

        for i, x in enumerate(data):
            btn = SongSelectionButton(media_controller, x, label=f"Song {i + 1}")
            btn.style = nextcord.ButtonStyle.blurple
            self.add_item(btn)


class MediaController:
    def __init__(self):
        self._queue = QueueManager()
        self._volume = 5
        self._current_song: YouTubeVideo = None
        self.is_loop_running = False

    async def play(self, interaction: nextcord.Interaction, url: str):
        if not interaction.guild.voice_client:
            if not interaction.user.voice:
                await interaction.send("You must first join a voice channel!", ephemeral=True)
                return
            await interaction.user.voice.channel.connect()
        self._queue.add(interaction, url)
        if not self.is_loop_running:
            await self.song_loop()

    async def search(self, interaction: nextcord.Interaction, query: str):
        if not interaction.guild.voice_client:
            if not interaction.user.voice:
                await interaction.send("You must first join a voice channel!", ephemeral=True)
                return
        await interaction.response.defer()
        result = pytube.Search(query)
        view = SongSelectionView(interaction, self, result.results[:5])

        embed = nextcord.Embed(title=f'Results for: "{query}"')
        for i, x in enumerate(result.results[:5]):
            embed.add_field(name=f"Song {i + 1}", value=f"{x.title} ({self.get_time_from_seconds(x.length)})", inline=False)
        await interaction.send(embed=embed, view=view)

    async def pause(self, interaction: nextcord.Interaction):
        vc: nextcord.VoiceClient = interaction.guild.voice_client
        vc.pause()
        await interaction.send("Playback has been paused.", delete_after=60)

    async def resume(self, interaction: nextcord.Interaction):
        vc: nextcord.VoiceClient = interaction.guild.voice_client
        if not vc:
            interaction.send("Not connected to voice chat.", delete_after=60)
        vc.resume()
        await interaction.send("Playback has been resumed.", delete_after=60)

    async def skip(self, interaction: nextcord.Interaction):
        vc: nextcord.VoiceClient = interaction.guild.voice_client
        vc.stop()
        await interaction.send("Song skipped.", delete_after=60)

    async def stop(self, interaction: nextcord.Interaction):
        vc: nextcord.VoiceClient = interaction.guild.voice_client
        if not vc:
            interaction.send("Not connected to voice chat.", delete_after=60)
        vc.stop()
        self._queue.clear()
        await interaction.send("Stopped. Any remaining songs have been removed.", delete_after=60)

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
        if self._queue.length() == 0 and self._current_song is None:
            await interaction.send("No songs in queue", delete_after=60)
        if self._queue.length() < lines:
            lines = self._queue.length()
        if self._current_song:
            text.append(f"Current song: {self._current_song.video.title}")
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
            print(user_voice_client)
            await user_voice_client.channel.connect()
        if not inter.guild.voice_client.is_connected():
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
        inter.guild.voice_client.play(source=audio, after=self.song_loop)

    async def song_loop(self, *args, **kwargs):
        if self._queue.is_empty():
            self.is_loop_running = False
            self._current_song = None
            return
        self.is_loop_running = True
        self._current_song = self._queue.get(0)
        await self._play_music(self._current_song)
        self._queue.pop(0)

    def get_time_from_seconds(self, seconds):
        minutes = floor(seconds / 60)
        seconds = seconds % 60
        if seconds < 10:
            seconds = f"0{seconds}"
        return f"{minutes}:{seconds}"
