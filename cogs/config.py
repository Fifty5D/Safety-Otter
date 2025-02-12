import json
import discord
from discord.ext import commands

import secret


class Config(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    

    @commands.Cog.listener()
    async def on_ready(self):
        print("Config cog ready.")

    #Config command
    @discord.app_commands.command(name="config_set", description="Setup the configuration of the bot")
    @discord.app_commands.guilds(secret.GUILD_ID)
    async def config_setup(self, interaction: discord.Interaction, message: str):
        print("Config_setup ")
        return
    

    #Configure List Command to show all the current configurations of that guild
    @discord.app_commands.command(name="configure_list", description="Show the current configuration of the bot for your server.")
    @discord.app_commands.guilds(secret.GUILD_ID)
    async def configure_list(self, interaction: discord.Interaction):
        with open("config.json", "r") as f:
            config = json.load(f)
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

                message += "Current configuration:\n\n**Roles:**\n"
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
                await interaction.followup.send(f"Current configuration:\n{json.dumps(config[str(interaction.guild.id)], indent=4)}", ephemeral=True)
            else:
                await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True, delete_after=10)
        except discord.HTTPException:
            await interaction.response.send_message("An error occurred while trying to get the configuration. Please try again later.", ephemeral=True, delete_after=20)



async def setup(bot: commands.Bot):
    await bot.add_cog(Config(bot))