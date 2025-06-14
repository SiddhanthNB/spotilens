import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

APP_ENV = os.getenv('APP_ENV', 'production')

SUPABASE_DB_PASSWORD = os.getenv('SUPABASE_DB_PASSWORD')
SUPABASE_DB_URL = os.getenv('SUPABASE_DB_URL').replace('[YOUR-PASSWORD]', quote_plus(SUPABASE_DB_PASSWORD))
