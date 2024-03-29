import nextcord
from nextcord.ext.commands import Bot, Cog
from MediaControls import MediaController


class MusicBotCog(Cog):
    def __init__(self, bot: Bot, bot_id: int):
        self._bot = bot
        self._bot_id = bot_id
        self.media_controller = MediaController()

    @nextcord.slash_command(description="Adds music to the queue")
    async def play(self, interaction: nextcord.Interaction, url: str):
        await self.media_controller.play(interaction, url)

    @nextcord.slash_command(description="Searches for given query")
    async def search(self, interaction: nextcord.Interaction, query: str):
        await self.media_controller.search(interaction, query)

    @nextcord.slash_command(description="Pauses current song")
    async def pause(self, interaction: nextcord.Interaction):
        await self.media_controller.pause(interaction)

    @nextcord.slash_command(description="Resumes current song")
    async def resume(self, interaction: nextcord.Interaction):
        await self.media_controller.resume(interaction)

    @nextcord.slash_command(description="Stops playing music")
    async def stop(self, interaction: nextcord.Interaction):
        await self.media_controller.stop(interaction)

    @nextcord.slash_command(description="Skips current song")
    async def skip(self, interaction: nextcord.Interaction):
        await self.media_controller.skip(interaction)

    @nextcord.slash_command(description="Volume")
    async def volume(self, interaction: nextcord.Interaction, volume: int):
        await self.media_controller.volume(interaction, volume)

    @nextcord.slash_command(description="Displays the current song queue")
    async def queue(self, interaction: nextcord.Interaction):
        await self.media_controller.queue(interaction)

    @nextcord.ext.commands.Cog.listener()
    async def on_voice_state_update(self, member: nextcord.Member, before, after):
        vc: nextcord.VoiceClient = member.guild.voice_client
        if vc is None:
            return
        for member in vc.channel.members:
            if not member.bot:
                return
        await vc.disconnect()
