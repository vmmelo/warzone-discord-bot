import logging
import os, os.path

from dotenv import load_dotenv

load_dotenv()


def saveLog(filename, content, log_type='info'):
    if not os.path.exists("logs/"):
        os.makedirs("logs/")

    logging.basicConfig(handlers=[logging.FileHandler('logs/' + filename, 'w+', 'utf-8')],
                        level=40 if os.environ.get('APP_ENV') == 'production' else 10)
    logging.getLogger().addHandler(logging.StreamHandler())
    if log_type == 'error':
        logging.error(content)
    elif log_type == 'warning':
        logging.warning(content)
    else:
        logging.info(content)


async def sendLogDiscordUser(client, content):
    user = await client.fetch_user(int(os.environ.get('USER_ID')))
    await user.send(content)
