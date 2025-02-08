import discord
from discord.ext import commands

class Config(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Config cog ready.")

    #Config command
    @discord.app_commands.command(name="config_set", description="Setup the configuration of the bot")
    async def config_setup(self, interaction: discord.Interaction, message: str):
        print("Config_setup ")
        return


async def setup(bot: commands.Bot):
    await bot.add_cog(Config(bot))