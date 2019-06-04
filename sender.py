import ujson
import urllib2


class Sender:
    TG_API_URL = 'https://api.telegram.org/bot'

    def __init__(self, config):
        self.config = config

    def send_posts(self, posts):
        for post in posts:
            if post['gif'] is not None:
                self._send_animation(post)
            elif post['video'] is not None:
                self._send_text_with_video(post)
            elif post['photos'] is None or len(post['photos']) == 0:
                self.send_text(post)
            elif len(post['photos']) == 1:
                self._send_single_photo(post)
            else:
                self._send_album(post)

    def send_text(self, post):
        url = u'{}{}/sendMessage'.format(self.TG_API_URL, self.config.telegram_token)
        data = {
            'chat_id': self.config.telegram_chat_id,
            'text': u"*{}*\n{}".format(post['name'], post['text']),
            'parse_mode': 'Markdown'
        }
        return Sender._post_request(url, data)

    def _send_text_with_video(self, post):
        url = u'{}{}/sendMessage'.format(self.TG_API_URL, self.config.telegram_token)
        data = {
            'chat_id': self.config.telegram_chat_id,
            'text': u"*{}*\n{}\n{}".format(post['name'], post['text'], post['video']),
            'parse_mode': 'Markdown'
        }
        return Sender._post_request(url, data)

    def _send_single_photo(self, post):
        url = u'{}{}/sendPhoto'.format(self.TG_API_URL, self.config.telegram_token)
        data = {
            'chat_id': self.config.telegram_chat_id,
            'caption': Sender.caption(post),
            'parse_mode': 'Markdown',
            'photo': post['photos'][0]
        }
        return Sender._post_request(url, data)

    def _send_animation(self, post):
        url = u'{}{}/sendAnimation'.format(self.TG_API_URL, self.config.telegram_token)
        data = {
            'chat_id': self.config.telegram_chat_id,
            'caption': Sender.caption(post),
            'parse_mode': 'Markdown',
            'animation': post['gif']
        }
        return Sender._post_request(url, data)

    def _send_album(self, post):
        url = u'{}{}/sendMediaGroup'.format(self.TG_API_URL, self.config.telegram_token)
        album = [{
                     'type': 'photo',
                     'media': ph,
                     'caption': Sender.caption(post),
                     'parse_mode': 'Markdown'
                 } if i == 0 else {
            'type': 'photo',
            'media': ph
        } for i, ph in enumerate(post['photos']) if i < 10]
        data = {
            'chat_id': self.config.telegram_chat_id,
            'media': ujson.dumps(album)
        }
        return Sender._post_request(url, data)

    @staticmethod
    def caption(post):
        text = u"*{}*\n{}".format(post['name'], post['text'])
        return text[:1021] + '...' if len(text) > 1024 else text

    @staticmethod
    def _post_request(url, data):
        req = urllib2.Request(url)
        req.add_header('Content-Type', 'application/json')
        return urllib2.urlopen(req, ujson.dumps(data)).read()
