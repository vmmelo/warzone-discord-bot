import os
from discord.utils import get
from dotenv import load_dotenv
from config.Logging import saveLog

load_dotenv()


async def notify_channels(discord_client, msg_content):
    app_environ = os.environ.get('APP_ENV')
    if app_environ == 'development':
        return
    guilds = sorted(discord_client.guilds, key=lambda guild: guild.name == 'A Raleta', reverse=True)
    for guild in guilds:
        channel = get(guild.text_channels, name='warzone-updates')
        if app_environ == 'staging' and guild.name != 'A Raleta':
            continue
        if channel is None:
            channel = await guild.create_text_channel('warzone-updates')
            saveLog('WarzoneDiscordBot.log', f'created channel warzone-updates in guild {guild.name}')
        await channel.send(msg_content)


async def send_log_discord_user(client, content):
    user = await client.fetch_user(int(os.environ.get('USER_ID')))
    await user.send(content)
