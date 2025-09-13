"""
Cog de comandos de música
"""
import discord
from discord.ext import commands
import asyncio
import yt_dlp
from typing import Optional, List
from utils.music_manager import MusicManager, Song
from utils.embeds import MusicEmbeds
from utils.views import MusicControlView, SearchResultView, VolumeModal
from config import YTDL_OPTIONS, FFMPEG_OPTIONS, AUTO_DISCONNECT_TIMEOUT, SEARCH_RESULTS_LIMIT

class Music(commands.Cog):
    """Comandos relacionados à música"""
    
    def __init__(self, bot):
        self.bot = bot
        self.music_manager = MusicManager()
        
    async def cog_unload(self):
        """Limpa recursos quando o cog é descarregado"""
        await self.music_manager.cleanup_all()
    
    async def ensure_voice_connection(self, ctx) -> bool:
        """Garante que o bot está conectado ao canal de voz do usuário"""
        if not ctx.author.voice:
            embed = MusicEmbeds.error_embed("Erro", "Você precisa estar em um canal de voz!")
            await ctx.send(embed=embed)
            return False
            
        manager = self.music_manager.get_guild_manager(ctx.guild.id)
        
        if not manager.voice_client:
            try:
                manager.voice_client = await ctx.author.voice.channel.connect()
                manager.voice_channel = ctx.author.voice.channel
            except Exception as e:
                embed = MusicEmbeds.error_embed("Erro de Conexão", f"Não consegui conectar ao canal: {e}")
                await ctx.send(embed=embed)
                return False
        elif manager.voice_client.channel != ctx.author.voice.channel:
            try:
                await manager.voice_client.move_to(ctx.author.voice.channel)
                manager.voice_channel = ctx.author.voice.channel
            except Exception as e:
                embed = MusicEmbeds.error_embed("Erro", f"Não consegui mover para o canal: {e}")
                await ctx.send(embed=embed)
                return False
                
        return True
    
    async def play_next_song(self, ctx, manager):
        """Toca a próxima música da fila"""
        if manager._disconnect_task:
            manager._disconnect_task.cancel()
            manager._disconnect_task = None
            
        next_song = manager.get_next_song()
        if not next_song:
            # Agenda desconexão automática
            manager._disconnect_task = asyncio.create_task(self.auto_disconnect(ctx, manager))
            return
            
        manager.current_song = next_song
        
        try:
            with yt_dlp.YoutubeDL(YTDL_OPTIONS) as ydl:
                info = ydl.extract_info(next_song.url, download=False)
                audio_url = info['url']
                
            # Cria source de áudio com volume
            source = discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio(audio_url, **FFMPEG_OPTIONS),
                volume=manager.volume
            )
            
            def after_playing(error):
                if error:
                    print(f'Erro na reprodução: {error}')
                asyncio.run_coroutine_threadsafe(self.play_next_song(ctx, manager), self.bot.loop)
            
            manager.voice_client.play(source, after=after_playing)
            
            # Envia embed com controles
            embed = MusicEmbeds.now_playing(next_song)
            view = MusicControlView(self.music_manager, ctx.guild.id)
            await ctx.send(embed=embed, view=view)
            
        except Exception as e:
            embed = MusicEmbeds.error_embed("Erro de Reprodução", f"Não consegui reproduzir a música: {e}")
            await ctx.send(embed=embed)
            # Tenta próxima música
            asyncio.create_task(self.play_next_song(ctx, manager))
    
    async def auto_disconnect(self, ctx, manager):
        """Desconecta automaticamente após timeout"""
        try:
            await asyncio.sleep(AUTO_DISCONNECT_TIMEOUT)
            if manager.voice_client and not manager.voice_client.is_playing() and not manager.queue:
                await manager.cleanup()
                embed = MusicEmbeds.success_embed("Desconectado", "Saí do canal por inatividade")
                await ctx.send(embed=embed)
        except asyncio.CancelledError:
            pass
    
    @commands.command(name='join', help='Conecta o bot ao seu canal de voz')
    async def join(self, ctx):
        """Comando para conectar ao canal de voz"""
        if await self.ensure_voice_connection(ctx):
            manager = self.music_manager.get_guild_manager(ctx.guild.id)
            embed = MusicEmbeds.success_embed("Conectado", f"Entrei no canal **{manager.voice_channel.name}**!")
            await ctx.send(embed=embed)
    
    @commands.command(name='leave', help='Desconecta o bot do canal de voz')
    async def leave(self, ctx):
        """Comando para desconectar do canal de voz"""
        manager = self.music_manager.get_guild_manager(ctx.guild.id)
        
        if manager.voice_client:
            await manager.cleanup()
            embed = MusicEmbeds.success_embed("Desconectado", "Saí do canal de voz. Até a próxima!")
            await ctx.send(embed=embed)
        else:
            embed = MusicEmbeds.error_embed("Erro", "Não estou em um canal de voz!")
            await ctx.send(embed=embed)
    
    @commands.command(name='play', help='Reproduz uma música do YouTube')
    async def play(self, ctx, *, query: str):
        """Comando para reproduzir música"""
        if not await self.ensure_voice_connection(ctx):
            return
            
        manager = self.music_manager.get_guild_manager(ctx.guild.id)
        
        # Mensagem de carregamento
        loading_embed = discord.Embed(
            title="🔍 Buscando...",
            description=f"Procurando por: **{query}**",
            color=discord.Color.yellow()
        )
        message = await ctx.send(embed=loading_embed)
        
        try:
            song = await Song.from_url(query, ctx.author)
            
            # Verifica se já está tocando
            if manager.voice_client.is_playing() or manager.voice_client.is_paused():
                if manager.add_song(song):
                    embed = MusicEmbeds.song_added(song, len(manager.queue))
                    await message.edit(embed=embed)
                else:
                    embed = MusicEmbeds.error_embed("Fila Cheia", "A fila atingiu o limite máximo!")
                    await message.edit(embed=embed)
            else:
                manager.add_song(song)
                await message.delete()
                await self.play_next_song(ctx, manager)
                
        except Exception as e:
            embed = MusicEmbeds.error_embed("Erro de Busca", f"Não consegui encontrar a música: {e}")
            await message.edit(embed=embed)
    
    @commands.command(name='search', help='Busca músicas e permite seleção')
    async def search(self, ctx, *, query: str):
        """Comando para buscar e selecionar músicas"""
        if not await self.ensure_voice_connection(ctx):
            return
            
        loading_embed = discord.Embed(
            title="🔍 Buscando...",
            description=f"Procurando por: **{query}**",
            color=discord.Color.yellow()
        )
        message = await ctx.send(embed=loading_embed)
        
        try:
            with yt_dlp.YoutubeDL({**YTDL_OPTIONS, 'quiet': True}) as ydl:
                search_results = ydl.extract_info(f"ytsearch{SEARCH_RESULTS_LIMIT}:{query}", download=False)
                
            if not search_results or not search_results.get('entries'):
                embed = MusicEmbeds.error_embed("Sem Resultados", "Não encontrei nenhuma música com esse termo")
                await message.edit(embed=embed)
                return
                
            results = search_results['entries'][:SEARCH_RESULTS_LIMIT]
            embed = MusicEmbeds.search_results(results, query)
            view = SearchResultView(results, self.music_manager, ctx.guild.id, ctx.author)
            
            await message.edit(embed=embed, view=view)
            
        except Exception as e:
            embed = MusicEmbeds.error_embed("Erro de Busca", f"Erro ao buscar: {e}")
            await message.edit(embed=embed)
    
    @commands.command(name='queue', aliases=['q'], help='Mostra a fila de músicas')
    async def queue(self, ctx, page: int = 1):
        """Comando para mostrar a fila"""
        manager = self.music_manager.get_guild_manager(ctx.guild.id)
        embed = MusicEmbeds.queue_display(manager, page - 1)
        await ctx.send(embed=embed)
    
    @commands.command(name='nowplaying', aliases=['np'], help='Mostra a música atual')
    async def now_playing(self, ctx):
        """Comando para mostrar música atual"""
        manager = self.music_manager.get_guild_manager(ctx.guild.id)
        
        if manager.current_song:
            embed = MusicEmbeds.now_playing(manager.current_song)
            view = MusicControlView(self.music_manager, ctx.guild.id)
            await ctx.send(embed=embed, view=view)
        else:
            embed = MusicEmbeds.error_embed("Nada Tocando", "Nenhuma música está tocando no momento")
            await ctx.send(embed=embed)
    
    @commands.command(name='volume', help='Ajusta o volume (0-100)')
    async def volume(self, ctx, volume: int = None):
        """Comando para ajustar volume"""
        manager = self.music_manager.get_guild_manager(ctx.guild.id)
        
        if volume is None:
            current_volume = int(manager.volume * 100)
            embed = discord.Embed(
                title="🔊 Volume Atual",
                description=f"Volume: **{current_volume}%**",
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)
            return
            
        if not 0 <= volume <= 100:
            embed = MusicEmbeds.error_embed("Volume Inválido", "O volume deve estar entre 0 e 100")
            await ctx.send(embed=embed)
            return
            
        manager.volume = volume / 100.0
        
        if manager.voice_client and hasattr(manager.voice_client.source, 'volume'):
            manager.voice_client.source.volume = manager.volume
            
        embed = MusicEmbeds.success_embed("Volume Ajustado", f"Volume definido para **{volume}%**")
        await ctx.send(embed=embed)
    
    @commands.command(name='skip', help='Pula a música atual')
    async def skip(self, ctx):
        """Comando para pular música"""
        manager = self.music_manager.get_guild_manager(ctx.guild.id)
        
        if not manager.voice_client or not manager.voice_client.is_playing():
            embed = MusicEmbeds.error_embed("Nada Tocando", "Nenhuma música está tocando!")
            await ctx.send(embed=embed)
            return
            
        skipped_song = manager.current_song
        manager.voice_client.stop()
        
        if skipped_song:
            embed = MusicEmbeds.success_embed("Música Pulada", f"Pulei: **{skipped_song.title}**")
            await ctx.send(embed=embed)
    
    @commands.command(name='stop', help='Para a música e limpa a fila')
    async def stop(self, ctx):
        """Comando para parar música"""
        manager = self.music_manager.get_guild_manager(ctx.guild.id)
        
        if manager.voice_client:
            manager.voice_client.stop()
            manager.clear_queue()
            manager.current_song = None
            
            embed = MusicEmbeds.success_embed("Parado", "Música parada e fila limpa")
            await ctx.send(embed=embed)
        else:
            embed = MusicEmbeds.error_embed("Nada Tocando", "Não estou tocando nada!")
            await ctx.send(embed=embed)
    
    @commands.command(name='pause', help='Pausa a música atual')
    async def pause(self, ctx):
        """Comando para pausar música"""
        manager = self.music_manager.get_guild_manager(ctx.guild.id)
        
        if manager.voice_client and manager.voice_client.is_playing():
            manager.voice_client.pause()
            manager.is_paused = True
            embed = MusicEmbeds.success_embed("Pausado", "Música pausada")
            await ctx.send(embed=embed)
        else:
            embed = MusicEmbeds.error_embed("Nada Tocando", "Nenhuma música está tocando!")
            await ctx.send(embed=embed)
    
    @commands.command(name='resume', help='Retoma a música pausada')
    async def resume(self, ctx):
        """Comando para retomar música"""
        manager = self.music_manager.get_guild_manager(ctx.guild.id)
        
        if manager.voice_client and manager.voice_client.is_paused():
            manager.voice_client.resume()
            manager.is_paused = False
            embed = MusicEmbeds.success_embed("Retomado", "Música retomada")
            await ctx.send(embed=embed)
        else:
            embed = MusicEmbeds.error_embed("Não Pausado", "Nenhuma música pausada!")
            await ctx.send(embed=embed)
    
    @commands.command(name='shuffle', help='Embaralha a fila')
    async def shuffle(self, ctx):
        """Comando para embaralhar fila"""
        manager = self.music_manager.get_guild_manager(ctx.guild.id)
        
        if not manager.queue:
            embed = MusicEmbeds.error_embed("Fila Vazia", "A fila está vazia!")
            await ctx.send(embed=embed)
            return
            
        manager.shuffle_queue()
        embed = MusicEmbeds.success_embed("Embaralhado", "Fila embaralhada com sucesso!")
        await ctx.send(embed=embed)
    
    @commands.command(name='loop', help='Ativa/desativa loop da música atual')
    async def loop(self, ctx):
        """Comando para ativar/desativar loop"""
        manager = self.music_manager.get_guild_manager(ctx.guild.id)
        
        manager.is_looping = not manager.is_looping
        status = "ativado" if manager.is_looping else "desativado"
        emoji = "🔁" if manager.is_looping else "➡️"
        
        embed = MusicEmbeds.success_embed("Loop", f"{emoji} Loop {status}")
        await ctx.send(embed=embed)
    
    @commands.command(name='remove', help='Remove uma música da fila')
    async def remove(self, ctx, index: int):
        """Comando para remover música da fila"""
        manager = self.music_manager.get_guild_manager(ctx.guild.id)
        
        if index < 1 or index > len(manager.queue):
            embed = MusicEmbeds.error_embed("Índice Inválido", f"Use um número entre 1 e {len(manager.queue)}")
            await ctx.send(embed=embed)
            return
            
        removed_song = manager.remove_song(index - 1)
        if removed_song:
            embed = MusicEmbeds.success_embed("Removido", f"Removido: **{removed_song.title}**")
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Music(bot))