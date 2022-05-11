from dotenv import load_dotenv
from config.Logging import saveLog
from database.Connection import Connection
from services.TwitterIntegration import get_updates, search_twitter_updates
from services.RavenCommunityScrapper import RavenCommunityScrapper
import os
import re
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

    async def on_message(self, message):
        try:
            author = message.author
            if message.content.startswith('!setlanguage'):
                if not author.guild_permissions.administrator:
                    return await message.channel.send(
                        'You do not have permission to change Warzone Updates language settings.')
                valid_expression = re.search('!setlanguage\s[a-zA-Z]{2}', message.content)
                if valid_expression is None:
                    return await message.channel.send('Invalid command. try !setlanguage en|pt|es')
                supported_languages = ['en', 'pt', 'es']
                language = valid_expression.group()
                language = language[-2:]
                if not language in supported_languages:
                    return await message.channel.send('We currently provide support in the following languages: ' + ', '.join(supported_languages))
                self.conn.save_guild_settings(message.guild.id, {'language': language})
                await message.channel.send(f'You now will receive Warzone Updates in {language}')
        except Exception as e:
            saveLog('WarzoneDiscordBot.log', str(e))


client = WarzoneDiscordBot()
client.run(os.environ.get('DISCORD_BOT_TOKEN'))
