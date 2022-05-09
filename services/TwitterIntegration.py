import requests
import os
from config.Logging import saveLog
from discord.utils import get
import urllib.parse
from dotenv import load_dotenv
from deep_translator import GoogleTranslator

from database.Connection import Connection
from services.DiscordMessager import send_log_discord_user

load_dotenv()

bearer_token = os.environ.get("TWITTER_BEARER_TOKEN")
ravenSoftwareID = '19136295'
conn = Connection()


def create_url(query="all"):
    # Replace with user ID below
    # user_id = 19136295
    # return "https://api.twitter.com/2/users/{}/tweets".format(user_id)
    return "https://api.twitter.com/2/tweets/search/recent?expansions=attachments.media_keys&query={}".format(
        urllib.parse.quote(query))


def get_params():
    # Tweet fields are adjustable.
    # Options include:
    # attachments, author_id, context_annotations,
    # conversation_id, created_at, entities, geo, id,
    # in_reply_to_user_id, lang, non_public_metrics, organic_metrics,
    # possibly_sensitive, promoted_metrics, public_metrics, referenced_tweets,
    # source, text, and withheld
    return {"media.fields": "preview_image_url,url"}


def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2UserTweetsPython"
    return r


def connect_to_endpoint(url, params):
    response = requests.request("GET", url, auth=bearer_oauth, params=params)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()


def format_attachments(tweet, result):
    attachmentsList = []
    if 'attachments' in tweet and 'media_keys' in tweet['attachments'] and 'includes' in result and 'media' in result[
        'includes']:
        for media_key in tweet['attachments']['media_keys']:
            for media in result['includes']['media']:
                if media['media_key'] == media_key:
                    attachmentsList.append(media)
        tweet['attachments'] = attachmentsList
    return tweet


def get_translations(content):
    target_languages = ['pt', 'fr', 'es']
    translations = {}
    for target_language in target_languages:
        translations[target_language] = GoogleTranslator(source='auto', target=target_language).translate(content)
    return translations


def format_tweet_result(result):
    if 'data' in result:
        for tweet in result['data']:
            content = tweet['text']
            tweet['translations'] = get_translations(content)
            tweet['tweet_url'] = "https://twitter.com/RavenSoftware/status/{}".format(tweet['id'])
            tweet = format_attachments(tweet, result)
    return result


def get_updates():
    url = create_url("(#warzone OR caldera OR rebirth) (from:ravensoftware)")
    params = get_params()
    response = connect_to_endpoint(url, params)
    saveLog('twitterIntegration.log', response)
    format_tweet_result(response)
    return response


async def check_and_notify_channels(client, update):
    msg_content = f'{update["text"]}'
    app_environ = os.environ.get('APP_ENV')
    if app_environ == 'development':
        return
    guilds = sorted(client.guilds, key=lambda guild: guild.name == 'A Raleta', reverse=True)
    for guild in guilds:
        channel = get(guild.text_channels, name='warzone-updates')
        if app_environ == 'staging' and guild.name != 'A Raleta':
            continue
        if channel is None:
            channel = await guild.create_text_channel('warzone-updates')
            saveLog('WarzoneDiscordBot.log', f'created channel warzone-updates in guild {guild.name}')
        await channel.send(msg_content)
        if 'attachments' in update:
            await send_attachments(channel, update['attachments'])


async def send_attachments(channel, attachments):
    for attachment in attachments:
        if attachment['type'] == 'photo':
            await channel.send(content=attachment['url'])


async def search_twitter_updates(client):
    try:
        await send_log_discord_user(client, "Searching updates.....")
        saveLog('WarzoneDiscordBot.log', f'begin search_updates task')
        warzone_recent_updates = get_updates()
        number_of_updates_sent = 0
        if 'data' in warzone_recent_updates and len(warzone_recent_updates['data']) > 0:
            for update in warzone_recent_updates['data']:
                if conn.get_tweet(update['id']) is None:
                    await check_and_notify_channels(client, update)
                    conn.save_tweet(update['id'], update)
                    number_of_updates_sent = number_of_updates_sent + 1
                    await send_log_discord_user(client, "New updates sent :)")
        else:
            await send_log_discord_user(client, "Didn't found warzone updates")

        if number_of_updates_sent == 0:
            await send_log_discord_user(client, "All updates already sent")
    except Exception as e:
        saveLog('WarzoneDiscordBot.log', 'Failed to search updates: ' + str(e), 'error')
