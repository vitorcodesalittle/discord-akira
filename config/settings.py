import os

from dotenv import load_dotenv

load_dotenv()

DEBUG = bool(os.getenv("DEBUG"))
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
LICHESS_TOKEN = os.getenv("LICHESS_TOKEN")

if not DISCORD_TOKEN:
    raise Exception("DISCORD_TOKEN not found")

if not LICHESS_TOKEN:
    print("Can't run $chess commands because the LICHESS_TOKEN is missing")