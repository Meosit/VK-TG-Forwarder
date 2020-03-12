import json


class Config:
    CONFIG_PATH = 'config.json'

    def __init__(self):
        self.config = self._load_config()

        self.vk_group_ids = self.config['vk_group_ids']
        self.vk_access_token = self.config['vk_access_token']

        self.telegram_chat_id = self.config['telegram_chat_id']
        self.telegram_bot_token = self.config['telegram_bot_token']

        self.fetch_posts_count = self.config['fetch_posts_count']
        self.fetch_threshold_minutes = self.config['fetch_threshold_minutes']
        self.fetch_overlap_seconds = self.config['fetch_overlap_seconds']

    @staticmethod
    def _load_config():
        with open(Config.CONFIG_PATH, 'r') as stream:
            data = json.load(stream)
            return data
