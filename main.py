import nextcord
from nextcord.ext import commands
from pytube import YouTube
import pytube

intents = nextcord.Intents.all()
bot = commands.Bot(intents=intents)


async def join_vc_from_interaction(interaction: nextcord.Interaction):
    if not interaction.user.voice:
        return False
    await interaction.user.voice.channel.connect()
    return True


def download_video(url:str):
    videos = YouTube(url)
    video: pytube.Stream = videos.streams.filter(mime_type="audio/mp4").last()
    try:
        video.download(filename="file.mp4")
    except Exception as e:
        print(e)
        return False
    return True


GUILD_IDS = [852764173292142593]
@bot.slash_command(guild_ids=GUILD_IDS, description="join a voice chat")
async def join(interaction: nextcord.Interaction, channel: nextcord.VoiceChannel):
    # Todo do this
    vc: nextcord.VoiceClient = interaction.guild.voice_client
    if not vc:
        await channel.connect()
        return
    for member in channel.members:
        if member.id == BOT_ID:
            await interaction.send("Already connected!", delete_after=10, ephemeral=True)
            return
    await vc.move_to(channel)


@bot.slash_command(guild_ids=GUILD_IDS, description="change volume")
async def volume(interaction: nextcord.Interaction, volume: int):
    if not 0 < volume <= 100:
        await interaction.send("Value must be between 1 and 100", delete_after=10)
        return
    interaction.guild.voice_client.source.volume = volume / 100
    await interaction.send(f"Volume has been set to {volume}%", delete_after=10)


@bot.slash_command(guild_ids=GUILD_IDS, description="pauses")
async def pause(interaction: nextcord.Interaction):
    interaction.guild.voice_client.pause()


@bot.slash_command(guild_ids=GUILD_IDS, description="resume")
async def resume(interaction: nextcord.Interaction):
    interaction.guild.voice_client.resume()


@bot.slash_command(guild_ids=GUILD_IDS, description="stop music")
async def stop(interaction: nextcord.Interaction):
    voice_client: nextcord.VoiceClient = interaction.guild.voice_client
    if not voice_client.is_playing():
        await interaction.send("Not playing anything currently", delete_after=10)
        return
    interaction.guild.voice_client.stop()
    await interaction.send("Stopping", delete_after=10)


@bot.slash_command(guild_ids=GUILD_IDS, description="play music")
async def play(interaction: nextcord.Interaction, url: str):
    if not await join_vc_from_interaction(interaction):
        await interaction.send("You need to join a voice channel.", delete_after=10)
        return
    if not download_video(url):
        await interaction.send("Error downloading video", delete_after=10)
        return

    thing = nextcord.PCMVolumeTransformer(nextcord.FFmpegPCMAudio("file.mp4", options="-vn"))
    thing.volume = .05

    interaction.guild.voice_client.play(thing)
    # await interaction.response.send_message(f"ur url nerd: {url}")

# rawr.streams.filter(mime_type="audio/mp4").last().download()

bot.run("MTA2MTQ3MDQ2NDgwMDczMTIxOA.Gtc6pS.HqY-gJRqjagxCxnmL_bj2fECiJ1wrzux9kaMA8")


