import nextcord
from nextcord.ext import commands


class MusicBotCog(commands.Cog):
    def __init__(self, bot: commands.Bot, bot_id: int):
        self.bot = bot
        self.bot_id = bot_id

    @nextcord.slash_command(description="Adds music to the queue")
    def play(interaction: nextcord.Interaction):
        pass
