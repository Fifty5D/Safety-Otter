import json
import re
import discord
from discord.ext import commands

import secret

class Maintenance(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print("Maintenance cog ready.")

    @discord.app_commands.command(name="maintenance_request", description="Send a maintenance request to the maintenance team.")
    @discord.app_commands.guilds(secret.GUILD_ID)
    async def maintenance(self, interaction: discord.Interaction, message: str, priority: int, photos: discord.Attachment = None):
        try:
            with open("config.json", "r") as f:
                config = json.load(f)
            open_tickets = 1331744963691548845
            location = re.findall(r"\[.*\]", interaction.user.display_name)[0]
            ticket_name = (f"{location}-{priority}")
            maintenance_team = discord.utils.get(interaction.guild.roles, id=config[str(interaction.guild.id)]["roles"]["maintenance_team"])
            config[str(interaction.guild.id)]["ticket_count"] += 1
            with open("config.json", "w") as f:
                json.dump(config, f, indent=4)
            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.user: discord.PermissionOverwrite(read_messages=True),
                maintenance_team: discord.PermissionOverwrite(read_messages=True)
            }
            new_ticket = await interaction.guild.create_text_channel(ticket_name, category=discord.utils.get(interaction.guild.categories, id=open_tickets), overwrites = overwrites)
            view = discord.ui.View()
            view.add_item(MaintenanceButton(style=discord.ButtonStyle.danger, label="Close", custom_id="close"))
            await interaction.response.send_message(f"Your maintenance request has been sent to the maintenance team. You can view it in {new_ticket.mention}.", ephemeral=True)
            await new_ticket.send(view=view)
            await new_ticket.send(f"{maintenance_team.mention}\nNew maintenance request from{interaction.user.mention}:\n{message}", file= await photos.to_file() if photos else None)
        except discord.HTTPException:
            await interaction.response.send_message("An error occurred while trying to send the maintenance request. Please try again later.")

    @discord.app_commands.command(name="clear_tickets", description="Clear all maintenance tickets.")
    @discord.app_commands.guilds(secret.GUILD_ID)
    async def clear_tickets(self, interaction: discord.Interaction):
        try:
            audit = discord.utils.get(interaction.guild.text_channels, name="audit-logs")
            await interaction.response.send_message("Clearing all tickets.", ephemeral=True)
            with open("config.json", "r") as f:
                config = json.load(f)
            open_tickets = discord.utils.get(interaction.guild.categories, id=1331744963691548845)
            cleared = False
            for channel in open_tickets.channels:
                await channel.delete()
                cleared = True
            if not cleared:
                await interaction.followup.send("There are no maintenance tickets to clear.", ephemeral=True)
            config[str(interaction.guild.id)]["ticket_count"] = 0
            with open("config.json", "w") as f:
                json.dump(config, f, indent=4)
            await audit.send(embed=discord.Embed(title="Audit Log", description=f"{interaction.user.mention} has cleared all maintenance tickets.", color=discord.Color.green()))
        except discord.HTTPException:
            await interaction.response.send_message("An error occurred while trying to clear the maintenance tickets. Please try again later.")

class MaintenanceButton(discord.ui.Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def callback(self, interaction: discord.Interaction):
        match interaction.data["custom_id"]:
            case "close":
                view = discord.ui.View()
                view.add_item(MaintenanceButton(style=discord.ButtonStyle.success, label="yes", custom_id="yes"))
                view.add_item(MaintenanceButton(style=discord.ButtonStyle.danger, label="no", custom_id="no"))
                await interaction.response.send_message("Are you sure you want to close this ticket?", ephemeral=True, view=view)
            case "yes":
                await interaction.response.send_message("Ticket closed.", ephemeral=True)
                await interaction.channel.delete()
                
            case "no":
                await interaction.response.send_message("pfft fine >:(", ephemeral=True, delete_after=5)

async def setup(bot: commands.Bot):
    await bot.add_cog(Maintenance(bot))
