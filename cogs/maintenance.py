import discord
from discord.ext import commands

class Maintenance(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print("Maintenance cog ready.")

    @discord.app_commands.command(name="maintenance", description="Send a maintenance request to the maintenance team.")
    async def maintenance(self, interaction: discord.Interaction, message: str):
        try:
            role = interaction.guild.get_role(self.bot.config[str(interaction.guild.id)]["roles"]["maintenance_team"])
            await interaction.channel.send(f"{role.mention} Maintenance request from <@{int(interaction.user.id)}>: {message}")
            await interaction.response.send_message("Your request has been sent to the maintenance team.")
        except discord.HTTPException:
            await interaction.response.send_message("An error occurred while trying to send the maintenance request. Please try again later.")

async def setup(bot: commands.Bot):
    await bot.add_cog(Maintenance(bot))
