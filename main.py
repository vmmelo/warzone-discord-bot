from discord.utils import get
from dotenv import load_dotenv
from config.Logging import saveLog
from services.TwitterIntegration import get_updates
from database.Connection import Connection
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
        saveLog('WarzoneDiscordBot.log', f'begin search_updates task')
        warzone_recent_updates = get_updates()
        if 'data' in warzone_recent_updates and len(warzone_recent_updates['data']) > 0:
            for update in warzone_recent_updates['data']:
                if self.conn.get_tweet(update['id']) is None:
                    await self.check_and_notify_channels(update)
                    self.conn.put_tweet(update['id'], update)

    async def check_and_notify_channels(self, update):
        msg_content = f'{update["text"]}'
        for guild in client.guilds:
            channel = get(guild.text_channels, name='warzone-updates')
            if channel is None:
                channel = await guild.create_text_channel('warzone-updates')
                saveLog('WarzoneDiscordBot.log', f'created channel warzone-updates in guild {guild.name}')
            await channel.send(msg_content)
            if 'attachments' in update:
                await self.send_attachments(channel, update['attachments'])

    async def send_attachments(self, channel, attachments):
        for attachment in attachments:
            if attachment['type'] == 'photo':
                await channel.send(content=attachment['url'])

    @search_updates.before_loop
    async def before_my_task(self):
        await self.wait_until_ready()  # wait until the bot logs in


client = WarzoneDiscordBot()
client.run(os.environ.get('DISCORD_BOT_TOKEN'))
