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
        for _x in client.guilds:
            print(f"Clearing {_x.name}")
            GUILD=discord.Object(_x.id)
            client.tree.clear_commands(guild=GUILD)
            client.tree.copy_global_to(guild=GUILD)
        print("Cleared all commands")
        client.tree.add_command(maintenance, guild=GUILD)
        print("Added maintenance command")
        client.tree.add_command(add_admin, guild=GUILD)
        print("Added add admin command")
        print("Syncing commands")
        await client.tree.sync()
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
@client.command()
async def configure_list(ctx: commands.Context):
    if ctx.author.guild_permissions.administrator or ctx.author.id in config[str(ctx.guild.id)]["admins"]:
        await ctx.send(f"Current configuration:\n{json.dumps(config[str(ctx.guild.id)], indent=4)}")
    else:
        await ctx.send("You do not have permission to use this command.")

# #Ping pong command
# @client.command()
# async def ping(ctx: commands.Context):
#     await ctx.send(f"Pong!")

# #Maintenance Request Command
# @client.command(name="request", help="Send a maintenance request to the maintenance team.")
# async def request(ctx: commands.Context, *, message: str):
#     channel = ctx.channel
#     role = ctx.guild.get_role(config[str(ctx.guild.id)]["roles"]["maintenance_team"])
#     await channel.send(f"{role.mention} Maintenance request from {ctx.author}: {message}")
#     await ctx.send("Your request has been sent to the maintenance team.")

# #Add user as bot admin
# @client.command()
# async def add_bot_admin(ctx: commands.Context, add_admin: int):
#     if ctx.author.guild_permissions.administrator:
#         if str(add_admin) in config[str(ctx.guild.id)]["admins"]:
#             await ctx.send(f"<@{add_admin}> is already an admin.")
#             return
#         config[str(ctx.guild.id)]["admins"][str(add_admin)] = add_admin
#         with open("config.json", "w") as f:
#             json.dump(config, f, indent=4)
#         await ctx.send(f"Added <@{add_admin}> as an admin.")
#     else:
#         await ctx.send("You do not have permission to use this command.")

# #Remove user as bot admin
# @client.command()
# async def remove_admin(ctx: commands.Context, remove_admin: int):
#     if ctx.author.guild_permissions.administrator:
#         if str(remove_admin) not in config[str(ctx.guild.id)]["admins"]:
#             await ctx.send(f"<@{remove_admin}> is not an admin.")
#         else:
#             del config[str(ctx.guild.id)]["admins"][str(remove_admin)]
#             with open("config.json", "w") as f:
#                 json.dump(config, f, indent=4)
#             await ctx.send(f"Removed <@{remove_admin}> as an admin.")
#     else:
#         await ctx.send("You do not have permission to use this command.")

#Maintenance / Command
@discord.app_commands.command(name="maintenance", description="Send a maintenance request to the maintenance team.")
async def maintenance(interaction: discord.Interaction, message: str):
    channel = interaction.channel
    role = interaction.guild.get_role(config[str(interaction.guild.id)]["roles"]["maintenance_team"])
    await channel.send(f"{role.mention} Maintenance request from <@{int(interaction.user.id)}>: {message}")
    await interaction.response.send_message("Your request has been sent to the maintenance team.")

#Add admin / command
@discord.app_commands.command(name="add_admin", description="Add a user as an admin.")
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

#Start the bot
if __name__ == "__main__":
    client.run(secret.TOKEN)
