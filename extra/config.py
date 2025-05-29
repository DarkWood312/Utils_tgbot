import os

import requests
from dotenv import load_dotenv
from requests import ConnectTimeout

from extra.SQL import DB

load_dotenv()

token = os.getenv('TOKEN')

webhook_host = os.getenv('WEBHOOK_HOST')
webhook_path = os.getenv('WEBHOOK_PATH')

sql_host = os.getenv('SQL_HOST')
sql_port = os.getenv('SQL_PORT')
sql_user = os.getenv('SQL_USER')
sql_database = os.getenv('SQL_DATABASE')
sql_password = os.getenv('SQL_PASSWORD')

dl_api_key = os.getenv('DL_API_KEY')
dl_api_url = os.getenv('DL_API_URL')

tg_api_server = os.getenv('TG_API_SERVER')

steam_api_key = os.getenv('STEAM_API_KEY')
faceit_api_key = os.getenv('FACEIT_API_KEY')

sql = DB(host=sql_host, port=int(sql_port), user=sql_user, database=sql_database, password=sql_password)

try:
    url_shortener_status = True if 200 <= requests.get('https://spoo.me').status_code <= 299 else False
except:
    url_shortener_status = False

try:
    get_file_direct_url_status = True if 200 <= requests.get('https://pomf.lain.la/').status_code <= 299 else False
except:
    get_file_direct_url_status = False

try:
    dl_api_url_status = True if 200 <= requests.get(dl_api_url).status_code <= 399 else False
except:
    dl_api_url_status = False