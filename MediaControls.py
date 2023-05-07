from QueueManager import QueueManager
from YouTube import YouTubeVideo, YouTubeManager
from math import floor
import nextcord


# TODO av_interleaved_write_frame error seemingly from the search command
# prolly need to add the play func to the pytube download callback

# TODO figure out why this link breaks it https://www.youtube.com/watch?v=nt9c0UeYhFc
# so it looks like Google is throttling connections, prolly need to swap to yt-dlp since pytube isn't updated much

class SongSelectionView(nextcord.ui.View):
    def __init__(self, interaction: nextcord.Interaction, media_controller, message_author, data):
        super().__init__()
        self.interaction = interaction
        self.value = None

        for index, song_title in enumerate(data):
            btn = SongSelectionButton(media_controller, message_author, song_title, label=f"Song {index + 1}")
            btn.style = nextcord.ButtonStyle.blurple
            self.add_item(btn)


class SongSelectionButton(nextcord.ui.Button):
    def __init__(self, controller, message_author, value: YouTubeVideo, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.controller = controller
        self.message_author = message_author
        self.value = value

    async def callback(self, interaction: nextcord.Interaction):
        self.controller: MediaController
        self.controller._queue.add(interaction, self.value.webpage_url)
        is_queue_ongoing = True
        if not self.controller.is_loop_running:
            is_queue_ongoing = False
            await self.controller.song_loop()
        self.view.stop()
        author = self.message_author.display_name
        status = f"Added {self.label}:" if is_queue_ongoing else f"Playing {self.label}:"
        title = self.value.title
        song_length = self.value.duration_string
        await interaction.message.delete()
        await interaction.message.channel.send(content=f"{author} {status} {title} ({song_length})", embed=None, view=None)

class MediaController:
    def __init__(self):
        self._queue = QueueManager()
        self._volume = 5
        self._current_song: YouTubeVideo = None
        self.is_loop_running = False
        self._yt_manager = YouTubeManager()

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
        print(f"searching for {query}")
        result = self._yt_manager.search(interaction, query)

        view = SongSelectionView(interaction, self, interaction.user, result)
        embed = nextcord.Embed(title=f'Results for: "{query}"')
        for i, x in enumerate(result):
            value = x.title
            if x.duration:
                value = f"{value} ({x.duration_string})"
                print(value)
            embed.add_field(name=f"Song {i + 1}", value=value, inline=False)
        await interaction.followup.send(embed=embed, view=view)

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
            return
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
            await user_voice_client.channel.connect()
        if not inter.guild.voice_client.is_connected():
            if not user_voice_client.channel.connect():
                await inter.send("You need to be connected to a voice channel!", 
                                 ephemeral=True, delete_after=60)
                return
            await user_voice_client.channel.connect()

        self._yt_manager.download(video)
        if not video.is_downloaded:
            await inter.send("Unable to download video.")
            return
        audio = nextcord.PCMVolumeTransformer(nextcord.FFmpegPCMAudio("file.mp3", options="-vn"))
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
