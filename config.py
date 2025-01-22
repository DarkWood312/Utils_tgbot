import os

from dotenv import load_dotenv

from SQL import DB
load_dotenv()

token = os.getenv('TOKEN')
sql_host = os.getenv('SQL_HOST')
sql_port = os.getenv('SQL_PORT')
sql_user = os.getenv('SQL_USER')
sql_database = os.getenv('SQL_DATABASE')
sql_password = os.getenv('SQL_PASSWORD')

dl_api_key = os.getenv('DL_API_KEY')

tg_api_server = os.getenv('TG_API_SERVER')
sql = DB(host=sql_host, port=sql_port, user=sql_user, database=sql_database, password=sql_password)
