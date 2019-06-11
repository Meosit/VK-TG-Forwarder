import time
import ujson
import urllib
import urllib2
import logging


class Loader:
    VK_WALL_API_URL = 'https://api.vk.com/method/wall.get'
    VK_API_VERSION = '5.95'

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

        groups = {o['id']: (o['name'], o['screen_name']) for o in posts_obj['response']['groups'] if o['id'] == wall_id}

        # not ads, not repost, from the community, created recently
        def check(o):
            return o['from_id'] == -wall_id\
                   and o['marked_as_ads'] == 0\
                   and o['date'] >= fetch_threshold\
                   and o['post_type'] == 'post'\
                   and 'copy_history' not in o

        logging.info("Loaded " + str(len(posts_obj['response']['items'])) + " from " + unicode(groups[wall_id][0]))
        posts = [{
            'from': o['from_id'],
            'name': groups[-o['from_id']][0],
            'date': o['date'],
            'text': Loader._create_text(o),
            'origin_link': 'https://vk.com/{}?w=wall{}_{}'.format(groups[-o['from_id']][1], o['from_id'], o['id']),
            'photos': Loader._find_photos(o.get('attachments', [])),
            'gif': Loader._find_gif(o.get('attachments', [])),
            'videos': Loader._find_videos(o.get('attachments', []))
        } for o in posts_obj['response']['items'] if check(o)]
        logging.info("Chosen " + str(len(posts)) + " from " + unicode(groups[wall_id]))
        return posts

    @staticmethod
    def _create_text(post):
        links = Loader._find_links(post.get('attachments', []))
        text = post['text']
        for link in links:
            if link.replace('http://', '').replace('https://', '') not in text:
                text = u'{}\n{}'.format(text, link)
        return text

    # all links
    @staticmethod
    def _find_links(attachments):
        return [o['link']['url'].replace('m.vk.com', 'vk.com') for o in attachments
                if o['type'] == 'link' and "vk.com/audio" not in o['link']['url']]

    # all photos with the largest resolution
    @staticmethod
    def _find_photos(attachments):
        return [next(iter(sorted(o['photo']['sizes'], reverse=True, key= lambda i: i['type'])))['url'] for o in attachments
                if o['type'] == 'photo' and len(o['photo']['sizes']) > 0]

    # first found gif
    @staticmethod
    def _find_gif(attachments):
        return next((o['doc']['url'] for o in attachments if o['type'] == 'doc' and o['doc']['ext'] == 'gif'), None)

    # all videos
    @staticmethod
    def _find_videos(attachments):
        return [(o['video']['title'], 'https://vk.com/video{}_{}'.format(o['video']['owner_id'], o['video']['id']))
                for o in attachments if o['type'] == 'video']