import logging
import os

import nextcord
import openai
from nextcord.ext import application_checks, commands
from nextcord.ext.application_checks import has_permissions

# Assuming the database functions are in the same structure
from database.database import fetch_assistants_by_guild, fetch_guild_membership

# Set up logging
logger = logging.getLogger('discord')

# Initialize OpenAI Client
client = openai.OpenAI()

# Load the OpenAI API key from environment variables
openai.api_key = os.getenv('OPENAI_API_KEY')

class AssistantForge(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild_max_assistants = {}
        self.current_assistants_count = {}
        bot.loop.create_task(self.load_guild_data())

    async def load_guild_data(self):
        await self.bot.wait_until_ready()
        for guild in self.bot.guilds:
            guild_membership = await fetch_guild_membership(guild.id)
            if guild_membership:
                self.guild_max_assistants[guild.id] = guild_membership.get('max_assistants', 0)  # Ensure default is 0
                assistants = await fetch_assistants_by_guild(guild.id)
                self.current_assistants_count[guild.id] = len(assistants)
            else:
                self.guild_max_assistants[guild.id] = 0
                self.current_assistants_count[guild.id] = 0

    @nextcord.slash_command(name="staff", description="Root command for server staff operations.")
    @application_checks.has_permissions(administrator=True)
    async def staff(self, inter: nextcord.Interaction):
        await inter.response.send_message('Staff root command invoked. Use subcommands for specific actions.')

    @staff.subcommand(name="create_qa_assistant", description="Create a QA assistant for the server.")
    @application_checks.has_permissions(administrator=True)
    async def create_qa_assistant(self, inter: nextcord.Interaction):
        guild_id = inter.guild.id
        if guild_id not in self.guild_max_assistants or guild_id not in self.current_assistants_count:
            await inter.response.send_message('Guild data not loaded or guild is not recognized, please try again later.')
            return

        if self.current_assistants_count[guild_id] < self.guild_max_assistants[guild_id]:
            await inter.response.send_message('Creating a new assistant...')
            # Logic for creating a new assistant goes here
            # Remember to update self.current_assistants_count[guild_id] as necessary after creation
        else:
            await inter.response.send_message('Max assistants limit reached.')

def setup(bot):
    bot.add_cog(AssistantForge(bot))