from discord.utils import get
from dotenv import load_dotenv
import os
from discord.ext import tasks, commands
import discord
load_dotenv()


class WarzoneDiscordBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # an attribute we can access from our task
        self.counter = 0

        # start the task to run in the background
        self.notify_updates.start()

    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')

    @tasks.loop(seconds=2)
    async def notify_updates(self):
        for guild in client.guilds:
            channel = get(guild.text_channels, name='warzone-updates')
            if channel is None:
                channel = await guild.create_text_channel('warzone-updates')
            # await channel.send(f'alo romario')

    @notify_updates.before_loop
    async def before_my_task(self):
        await self.wait_until_ready()  # wait until the bot logs in


client = WarzoneDiscordBot()
client.run(os.environ.get('DISCORD_BOT_TOKEN'))
