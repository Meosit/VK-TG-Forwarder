import time
import ujson
import urllib
import urllib2
import logging


class Loader:
    VK_WALL_API_URL = 'https://api.vk.com/method/wall.get'
    VK_VIDEO_URL = 'https://vk.com/video'
    VK_API_VERSION = '5.45'

    def __init__(self, config):
        self.config = config

    def load_communities_feed(self, group_ids):
        fetch_threshold = int(time.time()) - self.config.for_last_mins * 60
        logging.info("Threshold is " + str(fetch_threshold))
        return sorted([post for wall_id in group_ids for post in self._load_posts(wall_id, fetch_threshold)], key=lambda p: p['date'])

    def _load_posts(self, wall_id, fetch_threshold):
        params = {
            'owner_id': -wall_id,
            'access_token': self.config.access_token,
            'extended': 1,
            'offset': 0,
            'count': 10,
            'filter': 'owner',
            'v': Loader.VK_API_VERSION
        }
        data = urllib.urlencode(params)
        req = urllib2.Request(Loader.VK_WALL_API_URL, data)
        response = urllib2.urlopen(req)
        posts_json = response.read()
        posts_obj = ujson.loads(posts_json)

        groups = {o['id']: o['name'] for o in posts_obj['response']['groups'] if o['id'] == wall_id}

        # not ads, not repost, from the community, created recently
        def check(o):
            return o['from_id'] == -wall_id\
                   and o['marked_as_ads'] == 0\
                   and o['date'] >= fetch_threshold\
                   and o['post_type'] == 'post'\
                   and 'copy_history' not in o

        logging.info("Loaded " + str(len(posts_obj['response']['items'])) + " from " + unicode(groups[wall_id]))
        posts = [{
            'from': o['from_id'],
            'name': groups[-o['from_id']],
            'date': o['date'],
            'text': o['text'],
            'photos': Loader.find_photos(o.get('attachments', [])),
            'gif': Loader.find_gif(o.get('attachments', [])),
            'video': Loader.find_video(o.get('attachments', []))
        } for o in posts_obj['response']['items'] if check(o)]
        logging.info("Chosen " + str(len(posts)) + " from " + unicode(groups[wall_id]))
        return posts

    # all photos with the largest resolution
    @staticmethod
    def find_photos(attachments):
        return [o['photo']['photo_' + str(
            max([(int(key[6:]) if key.startswith('photo_') else 0) for key in o['photo'].keys()]))] for o in attachments
                if o['type'] == 'photo']

    # first found gif
    @staticmethod
    def find_gif(attachments):
        return next((o['doc']['url'] for o in attachments if o['type'] == 'doc' and o['doc']['ext'] == 'gif'), None)

    # first found video
    @staticmethod
    def find_video(attachments):
        return next(('{}{}_{}'.format(Loader.VK_VIDEO_URL, o['video']['owner_id'], o['video']['id'])
                     for o in attachments if o['type'] == 'video'), None)
