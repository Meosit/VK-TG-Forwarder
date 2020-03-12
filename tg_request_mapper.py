# -*- coding: utf-8 -*-
import json
import re

import urllib2

ANY_URL_REGEX = re.compile(r"""(?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))""")
HTML_ESCAPE_TABLE = {
    u"&": u"&amp;",
    # u'"': u"&quot;",
    u">": u"&gt;",
    u"<": u"&lt;",
}


def _html_escape(text):
    return u"".join(HTML_ESCAPE_TABLE.get(c, c) for c in text)


def _url_count(text):
    return len(ANY_URL_REGEX.findall(text))
    # return len(re.findall(ANY_URL_REGEX, text))


class TgRequestMapper:
    TG_API_URL = 'https://api.telegram.org/bot'

    def __init__(self, config):
        self.config = config

    def convert_to_telegram_request_info(self, vk_post):
        request_creator = self._find_request_creator(vk_post)
        return {
            'date': vk_post['date'],
            'requests': request_creator(vk_post)
        }

    def _find_request_creator(self, vk_post):
        if vk_post['gif'] is not None:
            # gif require usage of different Telegram method
            return self._create_gif_request_info
        elif vk_post['photos'] is not None and len(vk_post['photos']) == 1:
            return self._create_photo_request_info
        elif vk_post['photos'] is not None and len(vk_post['photos']) > 1:
            return self._create_album_request_info
        else:
            return self._create_text_request_info

    def _create_gif_request_info(self, vk_post):
        url = u'{}{}/sendAnimation'.format(self.TG_API_URL, self.config.telegram_bot_token)
        caption = self._post_html(vk_post)
        gif_data = {
            'chat_id': self.config.telegram_chat_id,
            'caption': caption,
            'parse_mode': 'HTML',
            'animation': vk_post['gif']
        }
        if len(caption) >= 1024:
            gif_data['caption'] = self._short_media_caption(vk_post)
            return [(url, gif_data), self.simple_text_request_info(caption, disable_link_preview=True)]
        else:
            return [(url, gif_data)]

    def _create_photo_request_info(self, vk_post):
        url = u'{}{}/sendPhoto'.format(self.TG_API_URL, self.config.telegram_bot_token)
        caption = self._post_html(vk_post)
        photo_data = {
            'chat_id': self.config.telegram_chat_id,
            'caption': caption,
            'parse_mode': 'HTML',
            'photo': vk_post['photos'][0]
        }
        if len(caption) >= 1024:
            photo_data['caption'] = self._short_media_caption(vk_post)
            return [(url, photo_data), self.simple_text_request_info(caption, disable_link_preview=True)]
        else:
            return [(url, photo_data)]

    def _create_album_request_info(self, vk_post):
        url = u'{}{}/sendMediaGroup'.format(self.TG_API_URL, self.config.telegram_bot_token)
        caption = self._post_html(vk_post)
        if len(caption) >= 1024:
            short_caption = self._short_media_caption(vk_post)
            album = [{
                         'type': 'photo',
                         'media': ph,
                         'caption': short_caption,
                         'parse_mode': 'HTML'
                     }
                     if i == 0 else
                     {
                         'type': 'photo',
                         'media': ph
                     }
                     for i, ph in enumerate(vk_post['photos']) if i < 10]
            album_data = {
                'chat_id': self.config.telegram_chat_id,
                'media': ujson.dumps(album)
            }
            return [(url, album_data), self.simple_text_request_info(caption, disable_link_preview=True)]
        else:
            album = [{
                         'type': 'photo',
                         'media': ph,
                         'caption': caption,
                         'parse_mode': 'HTML'
                     }
                     if i == 0 else
                     {
                         'type': 'photo',
                         'media': ph
                     }
                     for i, ph in enumerate(vk_post['photos']) if i < 10]
            album_data = {
                'chat_id': self.config.telegram_chat_id,
                'media': json.dumps(album)
            }
            return [(url, album_data)]

    def _create_text_request_info(self, vk_post):
        post = self._post_html(vk_post)
        return [self.simple_text_request_info(post, disable_link_preview=_url_count(post) == 1)]

    def simple_text_request_info(self, text, disable_link_preview=False):
        url = u'{}{}/sendMessage'.format(self.TG_API_URL, self.config.telegram_bot_token)
        data = {
            'chat_id': self.config.telegram_chat_id,
            'text': text,
            'parse_mode': 'HTML',
            'disable_web_page_preview': disable_link_preview
        }
        return url, data

    @staticmethod
    def _short_media_caption(vk_post):
        header = u"<b>{}</b>".format(vk_post['title'])
        footer = u"<a href=\"{}\">Go to post</a>".format(vk_post['origin_link'])
        return u"{} {}\n🠟 This is media for the below 🠟".format(header, footer)

    @staticmethod
    def _post_html(vk_post):
        header = u"<b>{}</b>".format(vk_post['title'])
        footer = u"<a href=\"{}\">Go to post</a>".format(vk_post['origin_link'])

        # content textual parts
        pool = u"<b>Poll: {}</b>{}".format(
            _html_escape(vk_post['poll']['question']),
            u"".join(map(lambda a: u"\n<code>?&gt; </code>{}".format(_html_escape(a)), vk_post['poll']['answers']))
        ) if vk_post['poll'] is not None else u""
        videos = u"".join(map(lambda v: u"\n<b>Video: </b><a href=\"{}\">{}</a>"
                              .format(v['link'], _html_escape(v['title'])), vk_post['videos'])) \
            if vk_post['videos'] is not None else u""

        text = _html_escape(vk_post['text'])
        if vk_post['links'] is not None:
            for link in vk_post['links']:
                if link.replace('http://', '').replace('https://', '') not in text:
                    text = u'{}\n<b>Link: </b>{}'.format(text, link)

        content = u"{}\n{}\n{}".format(videos, text, pool).strip()

        if len(content) == 0:
            return u"{} {}".format(header, footer)
        else:
            return u"{}\n{}\n{}".format(header, content, footer)

    @staticmethod
    def post_request(url, data):
        response = None
        try:
            req = urllib2.Request(url)
            req.add_header('Content-Type', 'application/json')
            response = urllib2.urlopen(req, json.dumps(data))
            result = response.read()
        finally:
            if response:
                response.close()
        return result
