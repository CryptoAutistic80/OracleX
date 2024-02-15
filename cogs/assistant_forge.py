import nextcord
from nextcord import Interaction
from nextcord.ext import application_checks, commands
from nextcord.ext.application_checks import has_permissions

from database.database import fetch_guild_membership


class AssistantForge(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Staff commands ready")

    @nextcord.slash_command(name="staff", description="Root command for server staff operations.")
    @application_checks.has_permissions(administrator=True)
    async def staff(self, inter):
        guild_membership = await fetch_guild_membership(inter.guild.id)
        if guild_membership is None:
            await inter.response.send_message('Guild does not have a membership entry, cannot proceed.')
            return
    
        await inter.response.send_message('staff root command invoked')

    @staff.subcommand()
    @application_checks.has_permissions(administrator=True)
    async def create_qa_assistant(self, inter: nextcord.Interaction):

        await inter.response.send_message('Command under development')

   
def setup(client):
    client.add_cog(AssistantForge(client))
