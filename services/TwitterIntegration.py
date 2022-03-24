import requests
import os
from config.Logging import saveLog
import json
import urllib.parse
from dotenv import load_dotenv
from deep_translator import GoogleTranslator
load_dotenv()

bearer_token = os.environ.get("TWITTER_BEARER_TOKEN")
ravenSoftwareID = '19136295'


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
    url = create_url("(#warzone) (from:ravensoftware)")
    params = get_params()
    response = connect_to_endpoint(url, params)
    saveLog('twitterIntegration.log', response)
    format_tweet_result(response)
    return response

get_updates()
# (#warzone) (from:ravensoftware) until:2022-03-07 since:2022-03-07 -filter:replies
