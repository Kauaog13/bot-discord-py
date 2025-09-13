"""
Configurações do bot de música Discord
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Token do Discord
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

# Configurações do yt-dlp
YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'extractaudio': True,
    'audioformat': 'mp3',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

# Configurações do FFmpeg
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

# Configurações gerais
DEFAULT_VOLUME = 0.5
MAX_QUEUE_SIZE = 50
SEARCH_RESULTS_LIMIT = 5
AUTO_DISCONNECT_TIMEOUT = 300  # 5 minutos