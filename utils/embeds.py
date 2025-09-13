"""
Utilitários para criar embeds do Discord
"""
import discord
from typing import List, Optional
from utils.music_manager import Song, GuildMusicManager

class MusicEmbeds:
    """Classe para criar embeds relacionados à música"""
    
    @staticmethod
    def now_playing(song: Song, position: int = 0, duration: int = None) -> discord.Embed:
        """Cria embed para música atual"""
        embed = discord.Embed(
            title="🎵 Tocando Agora",
            description=f"**{song.title}**",
            color=discord.Color.green()
        )
        
        if song.thumbnail:
            embed.set_thumbnail(url=song.thumbnail)
            
        if song.requester:
            embed.add_field(
                name="Solicitado por",
                value=song.requester.mention,
                inline=True
            )
            
        if duration:
            embed.add_field(
                name="Duração",
                value=f"{duration // 60}:{duration % 60:02d}",
                inline=True
            )
            
        embed.set_footer(text="Use os botões abaixo para controlar a reprodução")
        return embed
    
    @staticmethod
    def queue_display(manager: GuildMusicManager, page: int = 0, per_page: int = 10) -> discord.Embed:
        """Cria embed para exibir a fila"""
        embed = discord.Embed(
            title="📋 Fila de Música",
            color=discord.Color.blue()
        )
        
        if manager.current_song:
            embed.add_field(
                name="🎵 Tocando Agora",
                value=f"**{manager.current_song.title}**",
                inline=False
            )
        
        if not manager.queue:
            embed.add_field(
                name="Fila",
                value="A fila está vazia",
                inline=False
            )
        else:
            start = page * per_page
            end = start + per_page
            queue_slice = manager.queue[start:end]
            
            queue_text = ""
            for i, song in enumerate(queue_slice, start + 1):
                queue_text += f"`{i}.` **{song.title}**\n"
                if song.requester:
                    queue_text += f"    Solicitado por {song.requester.mention}\n"
            
            embed.add_field(
                name=f"Próximas ({len(manager.queue)} na fila)",
                value=queue_text or "Nenhuma música na fila",
                inline=False
            )
            
            if len(manager.queue) > per_page:
                embed.set_footer(text=f"Página {page + 1}/{(len(manager.queue) - 1) // per_page + 1}")
        
        return embed
    
    @staticmethod
    def song_added(song: Song, position: int) -> discord.Embed:
        """Cria embed para música adicionada à fila"""
        embed = discord.Embed(
            title="✅ Música Adicionada",
            description=f"**{song.title}**",
            color=discord.Color.green()
        )
        
        if song.thumbnail:
            embed.set_thumbnail(url=song.thumbnail)
            
        embed.add_field(
            name="Posição na fila",
            value=f"{position}",
            inline=True
        )
        
        if song.requester:
            embed.add_field(
                name="Solicitado por",
                value=song.requester.mention,
                inline=True
            )
            
        return embed
    
    @staticmethod
    def error_embed(title: str, description: str) -> discord.Embed:
        """Cria embed de erro"""
        embed = discord.Embed(
            title=f"❌ {title}",
            description=description,
            color=discord.Color.red()
        )
        return embed
    
    @staticmethod
    def success_embed(title: str, description: str) -> discord.Embed:
        """Cria embed de sucesso"""
        embed = discord.Embed(
            title=f"✅ {title}",
            description=description,
            color=discord.Color.green()
        )
        return embed
    
    @staticmethod
    def search_results(results: List[dict], query: str) -> discord.Embed:
        """Cria embed para resultados de busca"""
        embed = discord.Embed(
            title="🔍 Resultados da Busca",
            description=f"Busca por: **{query}**",
            color=discord.Color.blue()
        )
        
        for i, result in enumerate(results[:5], 1):
            duration = result.get('duration', 0)
            duration_str = f"{duration // 60}:{duration % 60:02d}" if duration else "N/A"
            
            embed.add_field(
                name=f"{i}. {result.get('title', 'Título Desconhecido')}",
                value=f"Duração: {duration_str}",
                inline=False
            )
        
        embed.set_footer(text="Reaja com o número correspondente para selecionar")
        return embed