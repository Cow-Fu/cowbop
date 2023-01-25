import nextcord
from nextcord.ext import commands, tasks
from QueueManager import QueueManager


class MusicBotCog(commands.Cog):
    def __init__(self, bot: commands.Bot, bot_id: int):
        self._bot = bot
        self._bot_id = bot_id
        self._volume = 5
        self.q = QueueManager()

    @nextcord.slash_command(description="Adds music to the queue")
    def play(self, interaction: nextcord.Interaction, url: str):
        self.q.add(url)
        if not self.q.is_empty() and not self.song_loop.is_running():
            self.song_loop.start()

    @nextcord.slash_command(description="Pauses current song")
    def pause(self, interaction: nextcord.Interaction):
        pass

    @nextcord.slash_command(description="Resumes current song")
    def resume(self, interaction: nextcord.Interaction):
        pass

    @nextcord.slash_command(description="Stops playing music")
    def stop(self, interaction: nextcord.Interaction):
        pass

    @nextcord.slash_command(description="Skips current song")
    def skip(self, interaction: nextcord.Interaction):
        pass

    @nextcord.slash_command(description="Volume")
    def volume(self, interaction: nextcord.Interaction):
        pass

    @nextcord.slash_command(description="Displays the current song queue")
    def queue(self, interaction: nextcord.Interaction):
        pass

    @tasks.loop(seconds=1)
    def song_loop():
        pass
