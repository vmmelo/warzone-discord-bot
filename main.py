from dotenv import load_dotenv
from config.Logging import saveLog
from services.TwitterIntegration import get_updates, search_twitter_updates
from database.Connection import Connection
from services.RavenCommunityScrapper import RavenCommunityScrapper
import os
from discord.ext import tasks, commands
import discord

load_dotenv()


class WarzoneDiscordBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # start the task to run in the background
        self.search_updates.start()
        self.conn = Connection()

    async def on_ready(self):
        saveLog('WarzoneDiscordBot.log', f'Logged in as {self.user.name} ({self.user.id})')

    @tasks.loop(seconds=300)
    async def search_updates(self):
        source = os.environ.get('UPDATES_SOURCE')
        if source == 'twitter':
            await search_twitter_updates(client)
        else:
            raven_community_scrapper = RavenCommunityScrapper()
            await raven_community_scrapper.search_updates_raven_website(client)

    @search_updates.before_loop
    async def before_my_task(self):
        await self.wait_until_ready()  # wait until the bot logs in


client = WarzoneDiscordBot()
client.run(os.environ.get('DISCORD_BOT_TOKEN'))
