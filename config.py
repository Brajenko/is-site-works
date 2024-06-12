import json


with open('./settings.json') as file:
    data = json.load(file)

tg_user_tg_id: int = data['tg']['user_tg_id']
tg_bot_token: str = data['tg']['tg_bot_token']
primary_color: str = data['gui']['primary_color']
positive_color: str = data['gui']['positive_color']
negative_color: str = data['gui']['negative_color']
mysql_name: str = data['mysql']['name']
mysql_username: str = data['mysql']['username']
mysql_password: str = data['mysql']['password']
mysql_hostname: str = data['mysql']['hostname']
mysql_port: str = data['mysql']['port']
screenshots_folder: str = data['screenshots']['folder']
