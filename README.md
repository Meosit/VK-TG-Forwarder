# VK-TG-Forwarder

Trivial GAE application designed to forward VK posts to the public channel using CRON job

### How to deploy (for beginners)

0. Create GCP project [here](https://console.cloud.google.com/projectcreate) and copy generated *project ID*, `<project_id>` will be used in this example
0. Create VK application [here](https://vk.com/editapp?act=create)
    * Platform: `Website`
    * Website: `<project_id>.appspot.com`
    * Copy **Service token** from the settings in the newly created app, `<vk_token>` will be used in this example
0. Create a new Telegram bot with [BotFather](https://core.telegram.org/bots#6-botfather) and copy provided **token**, , `<tg_token>` will be used in this example
0. Create a new public channel in telegram and add this bot as an admin to this channel (`<@channelname>` will be used in this example)
0. [Install](https://cloud.google.com/sdk/install) and [initialize](https://cloud.google.com/sdk/docs/initializing) Google Cloud Python 2.7 SDK
0. Clone repository:
   ```bash
   git clone https://github.com/Meosit/VK-TG-Forwarder.git
   cd VK-TG-Forwarder
   ```
0. Fill the `config.yaml` with all the credentials and [list of community ids](http://regvk.com/id/)
0. Fill `cron.yaml` with yours `<tg_token>` 
0. Deploy the application
   ```bash
   gcloud --project <project_id> app deploy --version 1 
   gcloud --project <project_id> app deploy cron.yaml
   ```
    

### Behavior

* Supported attachment types: `photo`, `gif`, `video`
* Media type priority: `gif` -> `video` -> `photo` (only one media type per post supported) 
* If the post contains either photo or gif, the text will be truncated to 1024 chars (telegram restriction)
* Video link pasted _as is_ and forwards to the VK domain (even if it's a youtube video)  