import requests
from bs4 import BeautifulSoup
from datetime import datetime
import textwrap
import re
from services.DiscordMessager import notify_channels


class RavenCommunityScrapper:
    RAVEN_URI = 'https://www.ravensoftware.com'
    DISCORD_CHARACTERS_LIMIT = 2000

    def __init__(self):
        community_page = requests.get('https://www.ravensoftware.com/community/')
        community_soup = BeautifulSoup(community_page.text, 'html.parser')
        pfc = community_soup.find_all(class_='post-feature-container')
        pc = community_soup.find_all(class_='post-container')
        self.posts = pfc + pc

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

    async def send_updates_discord(self, posts_object, discord_client=None):
        for post in posts_object:
            if not posts_object[post]['text']:
                continue
            # TODO check post already sent
            if True:
                text_splitted = self.split_text_limit_characters(posts_object[post]['text'])
                for msg in text_splitted:
                    await notify_channels(discord_client, msg)
                for img in posts_object[post]['images']:
                    await notify_channels(discord_client, img)

    async def search_updates_raven_website(self, discord_client=None):
        for post in self.posts:
            updated_date = self.get_post_updated_date(post.find(class_='post-feature-date') or
                                                      post.find(class_='post-date'))
            if updated_date is None:
                continue
            if updated_date > datetime.fromisoformat('2022-04-05'):
                content = self.get_post_content(self.format_content_url(post.find('a').attrs['href']))
                if not content:
                    continue
                if content.find(class_='blog-body'):
                    posts_object = self.read_patch_notes(content.find(class_='blog-body'))
                    await self.send_updates_discord(posts_object, discord_client)

                if content.find(class_='blog-body-container'):
                    self.read_blog_article(content.find(class_='body-content'))