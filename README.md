# VK-TG-Forwarder

Trivial AWS Lambda + AWS CloudWatch application designed to forward VK posts to the public channel using CRON job

### How to deploy

0. Create VK application [here](https://vk.com/editapp?act=create)
    * Platform: `Website`
    * Website: `<project_id>.appspot.com`
    * Copy **Service token** from the settings in the newly created app, `<vk_token>` in the config file
0. Create a new Telegram bot with [BotFather](https://core.telegram.org/bots#6-botfather) and copy provided **token**, `<tg_token>` in the config and cron files
0. Create a new public channel in telegram and add this bot as an admin to this channel (`<@channelname>` in the config file)
0. Clone repository:
   ```bash
   git clone https://github.com/Meosit/VK-TG-Forwarder.git
   cd VK-TG-Forwarder
   ```
0. Fill the `config.json` with all the **credentials** and [list of community ids](http://regvk.com/id/)
0. Create a zip file with the bot code 
   ```bash
   zip -0 lambda.zip config.py config.json main.py tg_request_mapper.py vk_wall_fetcher.py
   ```
0. Create AWS Lambda Function triggered by [AWS EventBridge](https://eu-west-3.console.aws.amazon.com/events/) scheduled rule
   0. Go to [AWS Lambda Console](console.aws.amazon.com/lambda) and create Python 3.9 runtime function
   0. Upload `lambda.zip` file to the lambda and set the Handler field to `main.update_feed` 
   0. At the Designer, press 'Add trigger' button, select `EventBridge (CloudWatch Events)` and create a new rule with the following schedule expression: `rate(10 minutes)`

### Behavior

* Supported attachment types: `photo`, `gif`, `video`, `poll`
* Each post contains a link to the original message
* Only gif and photos are sent natively into the telegram, the rest of the content represented as text
* VK has only its own video links available from the API (even if it's a youtube video)