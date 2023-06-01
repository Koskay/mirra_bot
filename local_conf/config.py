from dotenv import load_dotenv
import os

load_dotenv()

ADMINS = os.getenv('ADMINS').split()
WORK_ID = int(os.getenv('WORK_PHONE_ID'))
DB_NAME = os.getenv('DB_NAME')
BOT_TOKEN = os.getenv('TOKEN')