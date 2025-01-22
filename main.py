import json

import discord
from discord.ext import commands

import secret


#Setting up the bot
class SafetyOtter(commands.Bot):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(
            command_prefix="-", 
            intents=intents, 
            activity=discord.Activity(type=discord.ActivityType.playing, name="Renting Storage Units like a BOSS"),
            status=discord.Status.online
        )
    
client = SafetyOtter(intents=discord.Intents.all())

#Configure the bot
@client.event
async def on_ready():
    try:
        GUILD = discord.Object(secret.GUILD_ID)
        print("Syncing commands")
        await client.tree.sync(guild=GUILD)
        print("Synced commands")
    except discord.HTTPException:
        print("Failed to sync commands. This is likely due to a missing permission.")
    except discord.CommandSyncFailure:
        print("Failed to sync commands. This is likely due to a user related error.")
    except discord.Forbidden:
        print("The client does not have the applications.commands scope in the guild.")
    except discord.MissingApplicationID:
        print("The client does not have an application ID.")
    print(f"Logged in as {client.user.name} ({client.user.id})\nBot is ready to use!")

with open("config.json", "r") as f:
    config = json.load(f)

#Config command
#Todo: Make it into a / command and predefine the options
@client.command()
async def configure(ctx: commands.Context, key: str, value: str):
    if ctx.author.guild_permissions.administrator or ctx.author.id in config[str(ctx.guild.id)]["admins"]:
        if key in config[str(ctx.guild.id)]["roles"] and value.isdigit():
            config[str(ctx.guild.id)]["roles"][key] = int(value)
        elif key in config[str(ctx.guild.id)]["channels"] and value.isdigit():
            config[str(ctx.guild.id)]["channels"][key] = int(value)
        else:
            config[str(ctx.guild.id)][key] = int(value) if value.isdigit() else value
        with open("config.json", "w") as f:
            json.dump(config, f, indent=4)
        await ctx.send(f"Set {key} to {value}")
    else:
        await ctx.send("You do not have permission to use this command.")

#Configure List Command to show all the current configurations of that guild
#Todo: Make it into a / command and clean up the output
@client.command()
async def configure_list(ctx: commands.Context):
    if ctx.author.guild_permissions.administrator or ctx.author.id in config[str(ctx.guild.id)]["admins"]:
        await ctx.send(f"Current configuration:\n{json.dumps(config[str(ctx.guild.id)], indent=4)}")
    else:
        await ctx.send("You do not have permission to use this command.")

#Maintenance / Command
@client.tree.command(name="maintenance", description="Send a maintenance request to the maintenance team.")
async def maintenance(interaction: discord.Interaction, message: str):
    try:
        channel = interaction.channel
        role = interaction.guild.get_role(config[str(interaction.guild.id)]["roles"]["maintenance_team"])
        await channel.send(f"{role.mention} Maintenance request from <@{int(interaction.user.id)}>: {message}")
        await interaction.response.send_message("Your request has been sent to the maintenance team.")
    except discord.HTTPException:
        await interaction.response.send_message("An error occurred while trying to send the maintenance request. Please try again later.")

#Add admin / command
@client.tree.command(name="add_admin", description="Add a user as an admin.")
async def add_admin(interaction: discord.Interaction, add_admin: discord.User):
    try:
        if interaction.user.guild_permissions.administrator:
            if str(add_admin.id) in config[str(interaction.guild.id)]["admins"]:
                await interaction.response.send_message(f"<@{add_admin.id}> is already an admin.")
                return
            config[str(interaction.guild.id)]["admins"][str(add_admin.id)] = add_admin.id
            with open("config.json", "w") as f:
                json.dump(config, f, indent=4)
            await interaction.response.send_message(f"Added <@{add_admin.id}> as an admin.")
        else:
            await interaction.response.send_message("You do not have permission to use this command.")
    except discord.HTTPException:
        await interaction.response.send_message("An error occurred while trying to add the admin. Please try again later.")

#Remove admin / command
@client.tree.command(name="remove_admin", description="Remove a user as an admin.", guild=discord.Object(secret.GUILD_ID))
async def remove_admin(interaction: discord.Interaction, remove_admin: discord.User):
    try:
        if interaction.user.guild_permissions.administrator or interaction.user.id in config[str(interaction.guild.id)]["admins"]:
            if str(remove_admin.id) not in config[str(interaction.guild.id)]["admins"]:
                await interaction.response.send_message(f"<@{remove_admin.id}> is not an admin.")
                return
            del config[str(interaction.guild.id)]["admins"][str(remove_admin.id)]
            with open("config.json", "w") as f:
                json.dump(config, f, indent=4)
            await interaction.response.send_message(f"Removed <@{remove_admin.id}> as an admin.")
        else:
            await interaction.response.send_message("You do not have permission to use this command.")
    except discord.HTTPException:
        await interaction.response.send_message("An error occurred while trying to remove the admin. Please try again later.")

#Start the bot
if __name__ == "__main__":
    client.run(secret.TOKEN)
