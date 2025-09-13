"""
Gerenciador de estado de música para cada servidor
"""
import asyncio
import discord
import yt_dlp
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from config import YTDL_OPTIONS, FFMPEG_OPTIONS, DEFAULT_VOLUME, MAX_QUEUE_SIZE

@dataclass
class Song:
    """Representa uma música na fila"""
    url: str
    title: str
    duration: Optional[int] = None
    thumbnail: Optional[str] = None
    requester: Optional[discord.Member] = None
    
    @classmethod
    async def from_url(cls, url: str, requester: discord.Member = None) -> 'Song':
        """Cria uma instância de Song a partir de uma URL"""
        try:
            with yt_dlp.YoutubeDL(YTDL_OPTIONS) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Se for uma playlist, pega a primeira música
                if 'entries' in info:
                    entries = [entry for entry in info['entries'] if entry is not None]
                    if not entries:
                        raise ValueError("Nenhum vídeo válido encontrado")
                    info = entries[0]
                
                return cls(
                    url=info.get('webpage_url', url),
                    title=info.get('title', 'Música Desconhecida'),
                    duration=info.get('duration'),
                    thumbnail=info.get('thumbnail'),
                    requester=requester
                )
        except Exception as e:
            raise ValueError(f"Erro ao processar URL: {e}")

class GuildMusicManager:
    """Gerencia o estado de música para um servidor específico"""
    
    def __init__(self, guild_id: int):
        self.guild_id = guild_id
        self.queue: List[Song] = []
        self.current_song: Optional[Song] = None
        self.voice_channel: Optional[discord.VoiceChannel] = None
        self.voice_client: Optional[discord.VoiceClient] = None
        self.volume: float = DEFAULT_VOLUME
        self.is_looping: bool = False
        self.is_paused: bool = False
        self._disconnect_task: Optional[asyncio.Task] = None
        
    def add_song(self, song: Song) -> bool:
        """Adiciona uma música à fila"""
        if len(self.queue) >= MAX_QUEUE_SIZE:
            return False
        self.queue.append(song)
        return True
        
    def remove_song(self, index: int) -> Optional[Song]:
        """Remove uma música da fila pelo índice"""
        if 0 <= index < len(self.queue):
            return self.queue.pop(index)
        return None
        
    def clear_queue(self):
        """Limpa a fila de músicas"""
        self.queue.clear()
        
    def get_next_song(self) -> Optional[Song]:
        """Obtém a próxima música da fila"""
        if self.is_looping and self.current_song:
            return self.current_song
        return self.queue.pop(0) if self.queue else None
        
    def shuffle_queue(self):
        """Embaralha a fila de músicas"""
        import random
        random.shuffle(self.queue)
        
    async def cleanup(self):
        """Limpa recursos e desconecta do canal de voz"""
        if self._disconnect_task:
            self._disconnect_task.cancel()
            
        if self.voice_client:
            if self.voice_client.is_playing():
                self.voice_client.stop()
            await self.voice_client.disconnect()
            
        self.voice_client = None
        self.voice_channel = None
        self.current_song = None
        self.clear_queue()

class MusicManager:
    """Gerenciador global de música para todos os servidores"""
    
    def __init__(self):
        self.guilds: Dict[int, GuildMusicManager] = {}
        
    def get_guild_manager(self, guild_id: int) -> GuildMusicManager:
        """Obtém ou cria um gerenciador para um servidor"""
        if guild_id not in self.guilds:
            self.guilds[guild_id] = GuildMusicManager(guild_id)
        return self.guilds[guild_id]
        
    async def cleanup_guild(self, guild_id: int):
        """Limpa recursos de um servidor específico"""
        if guild_id in self.guilds:
            await self.guilds[guild_id].cleanup()
            del self.guilds[guild_id]
            
    async def cleanup_all(self):
        """Limpa recursos de todos os servidores"""
        for guild_manager in self.guilds.values():
            await guild_manager.cleanup()
        self.guilds.clear()