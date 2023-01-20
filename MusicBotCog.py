import nextcord
from nextcord.ext import commands


class MusicBotCog(commands.Cog):
    def __init__(self, bot: commands.Bot, bot_id: int):
        self.bot = bot
        self.bot_id = bot_id
        self._volume = 5

    @nextcord.slash_command(description="Adds music to the queue")
    def play(interaction: nextcord.Interaction):
        pass

    @nextcord.slash_command(description="Pauses current song")
    def pause(interaction: nextcord.Interaction):
        pass

    @nextcord.slash_command(description="Resumes current song")
    def resume(interaction: nextcord.Interaction):
        pass

    @nextcord.slash_command(description="Stops playing music")
    def stop(interaction: nextcord.Interaction):
        pass

    @nextcord.slash_command(description="Skips current song")
    def skip(interaction: nextcord.Interaction):
        pass

    @nextcord.slash_command(description="Volume")
    def volume(interaction: nextcord.Interaction):
        pass

    @nextcord.slash_command(description="Displays the current song queue")
    def queue(interaction: nextcord.Interaction):
        pass
