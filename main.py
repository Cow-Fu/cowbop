import nextcord
from nextcord.ext import commands


BOT_ID = 1061470464800731218
GUILD_IDS = [852764173292142593]

intents = nextcord.Intents.all()
bot = commands.Bot(intents=intents, default_guild_ids=GUILD_IDS)

# bot.add_cog
bot.run("MTA2MTQ3MDQ2NDgwMDczMTIxOA.Gtc6pS.HqY-gJRqjagxCxnmL_bj2fECiJ1wrzux9kaMA8")
