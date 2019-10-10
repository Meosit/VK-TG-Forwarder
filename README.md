# VK-TG-Forwarder

Trivial GAE application designed to forward VK posts to the public channel using CRON job

### How to deploy (for beginners)

0. Create GCP project [here](https://console.cloud.google.com/projectcreate) and copy generated *project ID*, `<project_id>` will be used in this example
0. Create VK application [here](https://vk.com/editapp?act=create)
    * Platform: `Website`
    * Website: `<project_id>.appspot.com`
    * Copy **Service token** from the settings in the newly created app, `<vk_token>` in the config file
0. Create a new Telegram bot with [BotFather](https://core.telegram.org/bots#6-botfather) and copy provided **token**, `<tg_token>` in the config and cron files
0. Create a new public channel in telegram and add this bot as an admin to this channel (`<@channelname>` in the config file)
0. [Install](https://cloud.google.com/sdk/install) and [initialize](https://cloud.google.com/sdk/docs/initializing) Google Cloud Python 2.7 SDK
0. Clone repository:
   ```bash
   git clone https://github.com/Meosit/VK-TG-Forwarder.git
   cd VK-TG-Forwarder
   ```
0. Fill the `config.yaml` with all the credentials and [list of community ids](http://regvk.com/id/)
0. Fill `cron.yaml` with your `<tg_token>`
0. Deploy the application
   ```bash
   gcloud --project <project_id> app deploy --version 1 
   gcloud --project <project_id> app deploy cron.yaml
   ```
    

### Behavior

* Supported attachment types: `photo`, `gif`, `video`, `poll`
* Each post contains a link to the original message
* Only gif and photos are sent natively into the telegram, the rest of the content represented as text
* Video links hidden to their titles, go first and forward to the VK (even if it's a youtube video)