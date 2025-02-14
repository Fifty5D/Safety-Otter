import json
import re
import discord
from discord.ext import commands
from discord import ui

import secret

class Checklist(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print("Checklist cog ready.")


    #Daily checklist to be completed by each store. Logsa list of tasks that need to be completed each day and opening funds.
    @discord.app_commands.command(name="daily_checklist", description="Daily checklist to be completed by each store.")
    @discord.app_commands.guilds(secret.GUILD_ID)
    async def daily_checklist(self, interaction: discord.Interaction):
        try:
            view = discord.ui.View()
            view.add_item(ChecklistButton(style=discord.ButtonStyle.danger, label="Open Sign", custom_id="t1"))
            view.add_item(ChecklistButton(style=discord.ButtonStyle.danger, label="Drive Around", custom_id="t2"))
            view.add_item(ChecklistButton(style=discord.ButtonStyle.danger, label="U-Haul", custom_id="t3"))
            view.add_item(ChecklistButton(style=discord.ButtonStyle.danger, label="Count Drawer", custom_id="t4"))
            view.add_item(ChecklistButton(style=discord.ButtonStyle.success, label="Submitt", custom_id="submitt", row=1))
            view.add_item(ChecklistButton(style=discord.ButtonStyle.secondary, label="Cancel", custom_id="cancel", row=1))
            embed = discord.Embed(title="Daily Checklist", description="1. Turn on the open sign.\n2. Drive around property and inspect for changes.\n3. If you are a U-Haul Dealer, check in equipment.\n4. Count opening funds.", color=discord.Color.green())
            await interaction.response.send_message("Please complete the following checklist and submit your opening funds.", embed=embed, view=view)
        except:
            await interaction.response.send_message("An error occurred while trying to log daily checklist. Please try again later.")


class ChecklistButton(discord.ui.Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def callback(self, interaction: discord.Interaction):
        custom_id = interaction.data["custom_id"]
        view = discord.ui.View.from_message(interaction.message)
        try:
            match custom_id:
                case "t1":
                    self.style = discord.ButtonStyle.success
                    self.disabled = True
                    await interaction.response.edit_message(view=self.view)
                case "t2":
                    self.style = discord.ButtonStyle.success
                    self.disabled = True
                    await interaction.response.edit_message(view=self.view)
                case "t3":
                    self.style = discord.ButtonStyle.success
                    self.disabled = True
                    await interaction.response.edit_message(view=self.view)
                case "t4":
                    self.style = discord.ButtonStyle.success
                    self.disabled = True
                    modal = ChecklistModal(interaction.message, title="Opening Funds", custom_id="funds")
                    modal.add_item(discord.ui.TextInput(label="Enter opening funds here", custom_id="funds"))
                    custom_id = interaction.data["custom_id"]
                    await interaction.response.send_modal(modal)
                case "submitt":
                    await interaction.response.send_message(":) Submitt")
                case "cancel":
                    await interaction.response.edit_message(view=self.view)
                    await interaction.message.delete()
        except:
            await interaction.response.send_message("Shit Broke")


class ChecklistModal(discord.ui.Modal):
    def __init__(self, message: discord.Message, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message = message

    async def on_submit(self, interaction: discord.Interaction):
        value: str = self.children[0].value.strip()
        view = discord.ui.View.from_message(self.message)
        view.children[3].style = discord.ButtonStyle.success
        view.children[3].disabled = True
        await interaction.response.edit_message(view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(Checklist(bot))
