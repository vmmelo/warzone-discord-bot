import requests
from bs4 import BeautifulSoup
from datetime import datetime
import textwrap
import re
from database.Connection import Connection
from services.DiscordMessenger import notify_channels
from googletrans import Translator


class RavenCommunityScrapper:
    RAVEN_URI = 'https://www.ravensoftware.com'
    DISCORD_CHARACTERS_LIMIT = 2000

    def __init__(self):
        community_page = requests.get('https://www.ravensoftware.com/community/')
        community_soup = BeautifulSoup(community_page.text, 'html.parser')
        pfc = community_soup.find_all(class_='post-feature-container')
        pc = community_soup.find_all(class_='post-container')
        self.posts = pfc + pc
        self.conn = Connection()

    def get_post_updated_date(self, date_div):
        if date_div is not None:
            date_text = date_div.text.strip()
            if date_text == '':
                return None
            return datetime.strptime(date_text, '%b %d, %Y')
        return None

    def format_content_url(self, text=''):
        if text.startswith('/community') or text.startswith('/content'):
            return self.RAVEN_URI + text
        return text

    def get_post_content(self, content_url=''):
        if not content_url:
            return ''
        content_page = requests.get(content_url)
        content_soup = BeautifulSoup(content_page.text, 'html.parser')
        return content_soup

    def read_blog_article(self, content):
        # TODO write function logic
        return

    def get_releases_sections(self, content):
        releases_sections = content.find_all('h2')
        releases_sections = list(map(lambda x: x.get_text(), releases_sections))
        return releases_sections

    def div_contains_section(self, div, sections):
        for section in sections:
            if section in div.get_text():
                return section
        return False

    def split_text_limit_characters(self, text, limit=DISCORD_CHARACTERS_LIMIT):
        remove_multiple_empty_lines = re.sub(r'\n\n+', '\n', text).strip()
        return textwrap.wrap(remove_multiple_empty_lines,
                             width=limit,
                             break_long_words=False,
                             replace_whitespace=False
                             )

    def read_patch_notes(self, content):
        notes_object = {}
        releases_sections = self.get_releases_sections(content)
        main_div = content.find('div', class_='aem-Grid aem-Grid--12 aem-Grid--default--12')
        actual_section = None
        for div in main_div.select('div[class*="aem-GridColumn aem-GridColumn--default--12"]'):
            is_section = self.div_contains_section(div, releases_sections)
            if not is_section and not actual_section:
                continue
            if is_section:
                actual_section = is_section
                notes_object[actual_section] = {'text': '', 'images': []}
            notes_object[actual_section]['text'] = notes_object[actual_section]['text'] + div.get_text()

            img_tags = div.find_all('img')
            for img in img_tags:
                if 'src' not in img.attrs:
                    continue
                src = img.attrs['src']
                if 'horizontal-long-line.png' in src:
                    continue
                notes_object[actual_section]['images'].append(self.format_content_url(src))
        return notes_object

    async def send_updates_discord(self, post_id, posts_object, discord_client=None):
        guild_settings = self.conn.get_guilds_settings()
        for post in posts_object:
            if not posts_object[post]['text']:
                continue
            id = post_id + post
            id = ''.join(e for e in id if e.isalnum())
            if self.conn.get_update(id) is None:
                translations = posts_object[post]['translations']
                guilds_not_english = []
                for language in translations:
                    guilds_language = self.get_guilds_use_language(language, guild_settings)
                    if language != 'en':
                        guilds_not_english = guilds_not_english + guilds_language
                    text = translations[language]
                    text_splitted = self.split_text_limit_characters(text)
                    for msg in text_splitted:
                        if language == 'en':
                            await notify_channels(discord_client, msg, dont_send_to=guilds_not_english)
                        else:
                            await notify_channels(discord_client, msg, send_only_to=guilds_language, restricted=True)
                for img in posts_object[post]['images']:
                    await notify_channels(discord_client, img)
                self.conn.save_update(id, posts_object[post])

    def get_guilds_use_language(self, language, guild_settings):
        guilds_language = []
        for (key, value) in guild_settings.items():
            if value['language'] == language:
                guilds_language.append(key)

        return guilds_language

    def get_translations(self, posts_object):
        translator = Translator()
        for post in posts_object:
            posts_object[post]['translations'] = {}
            target_languages = ['pt', 'fr', 'es']
            for target_language in target_languages:
                posts_object[post]['translations'][target_language] = \
                    translator.translate(posts_object[post]['text'], src='en', dest=target_language).text
        return posts_object

    async def search_updates_raven_website(self, discord_client=None):
        for post in self.posts:
            updated_date = self.get_post_updated_date(post.find(class_='post-feature-date') or
                                                      post.find(class_='post-date'))
            if updated_date is None:
                continue

            post_id = post.find(class_='post-header').get_text()
            post_id = str(updated_date.year) + ''.join(e for e in post_id if e.isalnum())
            if updated_date > datetime.fromisoformat('2022-05-03'):
                content = self.get_post_content(self.format_content_url(post.find('a').attrs['href']))
                if not content:
                    continue
                if content.find(class_='blog-body'):
                    posts_object = self.read_patch_notes(content.find(class_='blog-body'))
                    posts_object = self.get_translations(posts_object)
                    await self.send_updates_discord(post_id, posts_object, discord_client)

                if content.find(class_='blog-body-container'):
                    self.read_blog_article(content.find(class_='body-content'))