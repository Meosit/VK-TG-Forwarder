# -*- coding: utf-8 -*-
import re
import ujson
import urllib2


class Sender:
    TG_API_URL = 'https://api.telegram.org/bot'
    ANY_URL_REGEX = r"""(?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))"""

    def __init__(self, config):
        self.config = config

    def send_posts(self, posts):
        for post in posts:
            if post['gif'] is not None:
                self._send_animation(post)
            elif post['videos'] is not None and len(post['videos']) > 0:
                self._send_text_with_video(post)
            elif post['photos'] is None or len(post['photos']) == 0:
                self.send_text(post)
            elif len(post['photos']) == 1:
                self._send_single_photo(post)
            else:
                self._send_album(post)

    def send_text(self, post, escape_html=True, with_origin=True):
        url = u'{}{}/sendMessage'.format(self.TG_API_URL, self.config.telegram_token)

        post_text = u"<b>{}</b>\n{}\n<a href=\"{}\">Go to post</a>".format(
            post['name'], Sender.html_escape(post['text']) if escape_html else post['text'], post['origin_link']
        ) if with_origin else\
            u"<b>{}</b>\n{}\n".format(post['name'], Sender.html_escape(post['text']) if escape_html else post['text'])
        data = {
            'chat_id': self.config.telegram_chat_id,
            'text': post_text,
            'parse_mode': 'HTML',
            'disable_web_page_preview': Sender.url_count(post_text) == 1
        }
        return Sender._post_request(url, data)

    def _send_text_with_video(self, post):
        url = u'{}{}/sendMessage'.format(self.TG_API_URL, self.config.telegram_token)
        videos_part = u""
        for title, link in post['videos']:
            videos_part = u"{}\n<a href=\"{}\">{}</a>".format(videos_part, link, Sender.html_escape(title))
        data = {
            'chat_id': self.config.telegram_chat_id,
            'text': u"<b>{}</b>{}\n{}\n<a href=\"{}\">Go to post</a>".format(
                post['name'], videos_part, Sender.html_escape(post['text']), post['origin_link']
            ),
            'parse_mode': 'HTML'
        }
        return Sender._post_request(url, data)

    def _send_single_photo(self, post):
        url = u'{}{}/sendPhoto'.format(self.TG_API_URL, self.config.telegram_token)
        data = {
            'chat_id': self.config.telegram_chat_id,
            'caption': Sender._caption(post),
            'parse_mode': 'HTML',
            'photo': post['photos'][0]
        }
        return Sender._post_request(url, data)

    def _send_animation(self, post):
        url = u'{}{}/sendAnimation'.format(self.TG_API_URL, self.config.telegram_token)
        data = {
            'chat_id': self.config.telegram_chat_id,
            'caption': Sender._caption(post),
            'parse_mode': 'HTML',
            'animation': post['gif']
        }
        return Sender._post_request(url, data)

    def _send_album(self, post):
        url = u'{}{}/sendMediaGroup'.format(self.TG_API_URL, self.config.telegram_token)
        album = [{
                     'type': 'photo',
                     'media': ph,
                     'caption': Sender._caption(post),
                     'parse_mode': 'HTML'
                 } if i == 0 else {
            'type': 'photo',
            'media': ph
        } for i, ph in enumerate(post['photos']) if i < 10]
        data = {
            'chat_id': self.config.telegram_chat_id,
            'media': ujson.dumps(album)
        }
        return Sender._post_request(url, data)

    def _send_audios(self, post):
        url = u'{}{}/sendAudio'.format(self.TG_API_URL, self.config.telegram_token)
        for audio in post['audios']:
            data = {
                'chat_id': self.config.telegram_chat_id,
                'audio': audio['url'],
                'duration': audio['duration'],
                'performer': audio['performer'],
                'title': audio['title'],
                'thumb': audio['thumb']
            }
            Sender._post_request(url, data)

    @staticmethod
    def _caption(post):
        def cut_text(p):
            return Sender.html_escape(p['text'])[:1024 - len(p['name']) - 8 - 4 - len(p['origin_link']) - 25]

        text = (u"<b>{}</b>\n{}\n<a href=\"{}\">Go to post</a>" if len(
            post['text']) > 0 else u"<b>{}</b>{} <a href=\"{}\">Go to post</a>") \
            .format(post['name'], Sender.html_escape(post['text']), post['origin_link'])
        if len(text) > 1024:
            text = u"<b>{}</b>\n{}...\n<a href=\"{}\">Go to post</a>".format(
                post['name'], cut_text(post), post['origin_link']
            )
        return text[:1021] + '...' if len(text) > 1024 else text

    HTML_ESCAPE_TABLE = {
        u"&": u"&amp;",
        u'"': u"&quot;",
        u">": u"&gt;",
        u"<": u"&lt;",
    }

    @staticmethod
    def html_escape(text):
        return u"".join(Sender.HTML_ESCAPE_TABLE.get(c, c) for c in text)

    @staticmethod
    def _post_request(url, data):
        req = urllib2.Request(url)
        req.add_header('Content-Type', 'application/json')
        return urllib2.urlopen(req, ujson.dumps(data)).read()

    @staticmethod
    def url_count(text):
        return len(re.findall(Sender.ANY_URL_REGEX, text))
