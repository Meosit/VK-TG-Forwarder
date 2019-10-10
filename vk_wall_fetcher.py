import logging
import urllib
import urllib2

import ujson


class VkWallFetcher:
    VK_WALL_API_URL = 'https://api.vk.com/method/wall.get'
    VK_API_VERSION = '5.102'

    def __init__(self, config):
        self.config = config

    def fetch_wall_posts(self, group_id, fetch_threshold_date):
        wall_posts_json = self._fetch_posts_from_api(group_id)
        if wall_posts_json is None:
            return []
        wall_posts_object = ujson.loads(wall_posts_json)
        group_meta = next(({'title': o['name'], 'username': o['screen_name']}
                           for o in wall_posts_object['response']['groups'] if o['id'] == group_id), None)
        if group_meta is None:
            logging.error("Unable to retrieve group info from " + group_id)
            return []
        target_posts = filter(lambda p: self._is_valid_for_forward(fetch_threshold_date, group_id, p),
                              wall_posts_object['response']['items'])
        logging.info(u"Loaded {0} posts from {1}".format(str(len(target_posts)), str(group_meta)))
        return map(lambda p: self._map_wall_post(group_meta, p), target_posts)

    def _fetch_posts_from_api(self, group_id):
        params = {
            'owner_id': -group_id,
            'access_token': self.config.vk_access_token,
            'extended': 1,
            'offset': 0,
            'count': self.config.fetch_posts_count,
            'filter': 'owner',
            'v': VkWallFetcher.VK_API_VERSION
        }
        try:
            data = urllib.urlencode(params)
            req = urllib2.Request(VkWallFetcher.VK_WALL_API_URL, data)
            response = urllib2.urlopen(req)
            return response.read()
        except urllib2.HTTPError:
            logging.exception("Cannot load posts for group {}".format(group_id))
            return None

    # threshold by date, not an advertisement, posted by community, not a repost
    @staticmethod
    def _is_valid_for_forward(fetch_threshold_date, group_id, post_obj):
        return post_obj['date'] >= fetch_threshold_date \
               and post_obj['from_id'] == -group_id \
               and post_obj['marked_as_ads'] == 0 \
               and post_obj['post_type'] == 'post' \
               and 'copy_history' not in post_obj

    # simplify complicated response object
    @staticmethod
    def _map_wall_post(group_meta, post_obj):
        attachments = post_obj.get('attachments', [])
        return {
            'from': post_obj['from_id'],
            'title': group_meta['title'],
            'username': group_meta['username'],
            'date': post_obj['date'],
            'text': post_obj['text'],
            'origin_link': 'https://vk.com/wall{}_{}'.format(post_obj['from_id'], post_obj['id']),
            'photos': VkWallFetcher._find_photos(attachments),
            'videos': VkWallFetcher._find_videos(attachments),
            'links': VkWallFetcher._find_links(attachments),
            'gif': VkWallFetcher._find_gif(attachments),
            'poll': VkWallFetcher._find_pool(attachments)
        }

    # all photos with the largest resolution, returns [link] or None
    @staticmethod
    def _find_photos(attachments):
        photos = [next(iter(sorted(o['photo']['sizes'], reverse=True, key=lambda i: i['type'])))['url'] for o in
                  attachments if o['type'] == 'photo' and len(o['photo']['sizes']) > 0]
        return photos if len(photos) != 0 else None

    # all videos, returns [{title, link}] or None
    @staticmethod
    def _find_videos(attachments):
        videos = [{'title': o['video']['title'],
                   'link': 'https://vk.com/video{}_{}'.format(o['video']['owner_id'], o['video']['id'])}
                  for o in attachments if o['type'] == 'video']
        return videos if len(videos) != 0 else None

    # all links, returns [link] or None
    @staticmethod
    def _find_links(attachments):
        links = [o['link']['url'].replace('m.vk.com', 'vk.com') for o in attachments if
                 o['type'] == 'link' and "vk.com/audio" not in o['link']['url']]
        return links if len(links) != 0 else None

    # first found gif with size less than 10mb, returns just link or None
    @staticmethod
    def _find_gif(attachments):
        return next((o['doc']['url'] for o in attachments
                     if o['type'] == 'doc' and o['doc']['ext'] == 'gif' and o['doc']['size'] <= 10485760), None)

    # first found pool, returns {question, [answers]} or None
    @staticmethod
    def _find_pool(attachments):
        return next(({'question': o['poll']['question'], 'answers': map(lambda a: a['text'], o['poll']['answers'])}
                     for o in attachments if o['type'] == 'poll'), None)
