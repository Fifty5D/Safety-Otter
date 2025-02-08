import json
import os

import discord
from discord.ext import commands

import secret

INENTS = discord.Intents.all()
COGS = [cog[:-3] for cog in os.listdir("cogs/") if cog.endswith(".py")]
GUILD = discord.Object(secret.GUILD_ID)

#Setting up the bot
class SafetyOtter(commands.Bot):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(
            command_prefix="-", 
            intents=intents, 
            activity=discord.Activity(type=discord.ActivityType.playing, name="Renting Storage Units like a BOSS"),
            status=discord.Status.online
        )

    async def setup_hook(self) -> None:
        for cog in COGS:
            await self.load_extension(f"cogs.{cog}")
        self.tree.copy_global_to(guild=GUILD)
        await self.tree.sync(guild=GUILD)
    
bot = SafetyOtter(intents=discord.Intents.all())

#Configure the bot
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} ({bot.user.id}")

with open("config.json", "r") as f:
    config = json.load(f)
    bot.config = config

#Configure / command add modal for inputs
#Todo: add modal for inputs
@bot.tree.command(name="configure", description="Configure the bot for your server.", guild=discord.Object(secret.GUILD_ID))
async def configure(interaction: discord.Interaction, key: str, value: str):
    try:
        if interaction.user.guild_permissions.administrator or interaction.user.id in config[str(interaction.guild.id)]["admins"]:
            if key in config[str(interaction.guild.id)]["roles"] and value.isdigit():
                config[str(interaction.guild.id)]["roles"][key] = int(value)
            elif key in config[str(interaction.guild.id)]["channels"] and value.isdigit():
                config[str(interaction.guild.id)]["channels"][key] = int(value)
            else:
                config[str(interaction.guild.id)][key] = int(value) if value.isdigit() else value
            with open("config.json", "w") as f:
                json.dump(config, f, indent=4)
            await interaction.response.send_message(f"Set {key} to {value}", ephemeral=True, delete_after=10)
        else:
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True, delete_after=10)
    except discord.HTTPException:
        await interaction.response.send_message("An error occurred while trying to configure the bot. Please try again later.", ephemeral=True, delete_after=10)

#Configure List Command to show all the current configurations of that guild
@bot.tree.command(name="configure_list", description="Show the current configuration of the bot for your server.", guild=discord.Object(secret.GUILD_ID))
async def configure_list(interaction: discord.Interaction):
    try:
        if interaction.user.guild_permissions.administrator or interaction.user.id in config[str(interaction.guild.id)]["admins"]:
            guild_config = config[str(interaction.guild.id)]
            admins = guild_config.get("admins", {})
            roles = guild_config.get("roles", {})
            channels = guild_config.get("channels", {})
            other_settings = {k: v for k, v in guild_config.items() if k not in ["roles", "channels", "admins"]}
            
            message = "Current Admins:\n"
            for admin, admin_id in admins.items():
                admin_obj = interaction.guild.get_member(admin_id)
                message += f"{admin}: {admin_obj.mention if admin_obj else 'User not found'}\n"

            message = "Current configuration:\n\n**Roles:**\n"
            for role, role_id in roles.items():
                role_obj = interaction.guild.get_role(role_id)
                message += f"{role}: {role_obj.mention if role_obj else 'Role not found'}\n"

            message += "\n**Channels:**\n"
            for channel, channel_id in channels.items():
                channel_obj = interaction.guild.get_channel(channel_id)
                message += f"{channel}: {channel_obj.mention if channel_obj else 'Channel not found'}\n"

            message += "\n**Other Settings:**\n"
            for key, value in other_settings.items():
                message += f"{key}: {value}\n"

            await interaction.response.send_message(message, ephemeral=True, delete_after=60)
            await interaction.response.send_message(f"Current configuration:\n{json.dumps(config[str(interaction.guild.id)], indent=4)}", ephemeral=True, delete_after=60)
        else:
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True, delete_after=10)
    except discord.HTTPException:
        await interaction.response.send_message("An error occurred while trying to get the configuration. Please try again later.", ephemeral=True, delete_after=20)

#Add admin / command
@bot.tree.command(name="add_admin", description="Add a user as an admin.")
async def add_admin(interaction: discord.Interaction, add_admin: discord.User):
    try:
        if interaction.user.guild_permissions.administrator:
            if str(add_admin.id) in config[str(interaction.guild.id)]["admins"]:
                await interaction.response.send_message(f"<@{add_admin.id}> is already an admin.", ephemeral=True, delete_after=10)
                return
            config[str(interaction.guild.id)]["admins"][str(add_admin.id)] = add_admin.id
            with open("config.json", "w") as f:
                json.dump(config, f, indent=4)
            await interaction.response.send_message(f"Added <@{add_admin.id}> as an admin.", ephemeral=True, delete_after=10)
        else:
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True, delete_after=10)
    except discord.HTTPException:
        await interaction.response.send_message("An error occurred while trying to add the admin. Please try again later.", ephemeral=True, delete_after=10)

#Remove admin / command
@bot.tree.command(name="remove_admin", description="Remove a user as an admin.", guild=discord.Object(secret.GUILD_ID))
async def remove_admin(interaction: discord.Interaction, remove_admin: discord.User):
    try:
        if interaction.user.guild_permissions.administrator or interaction.user.id in config[str(interaction.guild.id)]["admins"]:
            if str(remove_admin.id) not in config[str(interaction.guild.id)]["admins"]:
                await interaction.response.send_message(f"<@{remove_admin.id}> is not an admin.", ephemeral=True, delete_after=10)
                return
            del config[str(interaction.guild.id)]["admins"][str(remove_admin.id)]
            with open("config.json", "w") as f:
                json.dump(config, f, indent=4)
            await interaction.response.send_message(f"Removed <@{remove_admin.id}> as an admin.", ephemeral=True, delete_after=10)
        else:
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True, delete_after=10)
    except discord.HTTPException:
        await interaction.response.send_message("An error occurred while trying to remove the admin. Please try again later.", ephemeral=True, delete_after=10)

#Start the bot
if __name__ == "__main__":
    bot.run(secret.TOKEN)
