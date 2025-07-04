# bot.py

import discord
from discord.ext import commands
import yt_dlp # Alterado de youtube_dl para yt_dlp
import asyncio
import os
from dotenv import load_dotenv
import nacl # Importado para garantir que PyNaCl seja reconhecido

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Obtém o token do bot
TOKEN = os.getenv('DISCORD_TOKEN')

# Define o prefixo dos comandos do bot (ex: !play, !stop)
client = commands.Bot(command_prefix='!', intents=discord.Intents.all())

# --- Configurações para yt-dlp ---
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
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

# Opções para o FFmpeg
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn', # -vn significa "no video", apenas áudio
}

# Dicionário para armazenar as filas de música por servidor (guild)
music_queues = {}

# --- Funções Auxiliares ---

async def play_next_song(ctx):
    guild_id = ctx.guild.id
    if guild_id in music_queues and music_queues[guild_id]['queue']:
        # Pega a próxima música da fila
        song_url = music_queues[guild_id]['queue'].pop(0)
        music_queues[guild_id]['current_song'] = song_url

        # Conecta ao canal de voz se ainda não estiver conectado
        voice_client = discord.utils.get(client.voice_clients, guild=ctx.guild)
        if voice_client is None:
            if music_queues[guild_id]['voice_channel']:
                voice_client = await music_queues[guild_id]['voice_channel'].connect()
            else:
                await ctx.send("Não estou em um canal de voz. Use `!join` primeiro.")
                music_queues[guild_id]['current_song'] = None
                return

        # Garante que o bot está no canal de voz correto
        if voice_client.channel != music_queues[guild_id]['voice_channel']:
            await voice_client.move_to(music_queues[guild_id]['voice_channel'])

        try:
            # Extrai a URL direta do áudio usando yt_dlp
            with yt_dlp.YoutubeDL(YTDL_OPTIONS) as ydl: # <-- CORREÇÃO AQUI
                info = ydl.extract_info(song_url, download=False)
                url = info['url'] # URL direta do stream de áudio
                title = info.get('title', 'Música Desconhecida')

            # Reproduz o áudio
            voice_client.play(discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS),
                              after=lambda e: client.loop.call_soon_threadsafe(play_next_song_callback, ctx, e))
            await ctx.send(f'Agora tocando: **{title}**')
        except Exception as e:
            await ctx.send(f"Ocorreu um erro ao tentar reproduzir a música: {e}")
            print(f"Erro de reprodução: {e}")
            music_queues[guild_id]['current_song'] = None
            # Tenta tocar a próxima música se houver um erro na atual
            client.loop.call_soon_threadsafe(play_next_song_callback, ctx, e)
    else:
        # Fila vazia, bot sai do canal de voz após um tempo
        await asyncio.sleep(60) # Espera 60 segundos antes de sair
        voice_client = discord.utils.get(client.voice_clients, guild=ctx.guild)
        if voice_client and not voice_client.is_playing() and not music_queues[guild_id]['queue']:
            await voice_client.disconnect()
            await ctx.send("Fila vazia, saí do canal de voz.")
            music_queues[guild_id]['voice_channel'] = None
            music_queues[guild_id]['current_song'] = None


def play_next_song_callback(ctx, error):
    if error:
        print(f'Erro na reprodução: {error}')
    # Chama a função assíncrona para tocar a próxima música
    asyncio.run_coroutine_threadsafe(play_next_song(ctx), client.loop)


# --- Eventos do Bot ---

@client.event
async def on_ready():
    """
    Este evento é disparado quando o bot se conecta com sucesso ao Discord.
    """
    print(f'Bot logado como {client.user}!')
    print(f'ID do Bot: {client.user.id}')
    print(f'Servidores conectados: {len(client.guilds)}')
    for guild in client.guilds:
        print(f'- {guild.name} (ID: {guild.id})')
        music_queues[guild.id] = {'queue': [], 'current_song': None, 'voice_channel': None} # Inicializa a fila para cada servidor

@client.event
async def on_command_error(ctx, error):
    """
    Tratamento de erros para comandos.
    """
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Comando não encontrado. Use `!help` para ver os comandos disponíveis.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Argumento faltando para o comando. Uso correto: `{ctx.prefix}{ctx.command.name} {ctx.command.signature}`")
    elif isinstance(error, commands.NotOwner):
        await ctx.send("Você não tem permissão para usar este comando.")
    else:
        print(f'Erro no comando {ctx.command}: {error}')
        await ctx.send(f"Ocorreu um erro ao executar o comando: {error}")


# --- Comandos do Bot ---

@client.command(name='join', help='Faz o bot entrar no seu canal de voz.')
async def join(ctx):
    """
    Comando para o bot entrar no canal de voz do usuário.
    """
    if not ctx.author.voice:
        await ctx.send(f'{ctx.author.name} não está conectado a um canal de voz.')
        return

    channel = ctx.author.voice.channel
    guild_id = ctx.guild.id

    if guild_id not in music_queues:
        music_queues[guild_id] = {'queue': [], 'current_song': None, 'voice_channel': None}

    # Se o bot já estiver em um canal de voz, move para o canal do usuário
    if ctx.voice_client:
        if ctx.voice_client.channel != channel:
            await ctx.voice_client.move_to(channel)
            music_queues[guild_id]['voice_channel'] = channel
            await ctx.send(f'Movi para o canal **{channel.name}**!')
        else:
            await ctx.send(f'Já estou no canal **{channel.name}**!')
    else:
        # Conecta-se ao canal de voz
        await channel.connect()
        music_queues[guild_id]['voice_channel'] = channel
        await ctx.send(f'Entrei no canal **{channel.name}**!')

@client.command(name='leave', help='Faz o bot sair do canal de voz.')
async def leave(ctx):
    """
    Comando para o bot sair do canal de voz.
    """
    guild_id = ctx.guild.id
    if ctx.voice_client:
        if guild_id in music_queues:
            ctx.voice_client.stop() # Parar qualquer música tocando
            music_queues[guild_id]['queue'].clear() # Limpa a fila ao sair
            music_queues[guild_id]['current_song'] = None
            music_queues[guild_id]['voice_channel'] = None
        await ctx.voice_client.disconnect()
        await ctx.send('Saí do canal de voz. Até a próxima!')
    else:
        await ctx.send('Não estou em um canal de voz.')

@client.command(name='play', help='Reproduz uma música a partir de um link do YouTube ou termo de busca.')
async def play(ctx, *, search_query: str):
    """
    Comando para reproduzir uma música.
    Aceita link do YouTube ou termo de busca.
    """
    guild_id = ctx.guild.id

    if not ctx.author.voice:
        await ctx.send(f'{ctx.author.name} não está conectado a um canal de voz.')
        return

    # Garante que o bot está no canal de voz do usuário
    if not ctx.voice_client:
        # Tenta conectar o bot ao canal de voz do autor
        try:
            await ctx.author.voice.channel.connect()
            await ctx.send(f'Entrei no canal **{ctx.author.voice.channel.name}**!')
        except Exception as e:
            await ctx.send(f"Não consegui entrar no canal de voz. Erro: {e}")
            return

    if guild_id not in music_queues:
        music_queues[guild_id] = {'queue': [], 'current_song': None, 'voice_channel': ctx.author.voice.channel}
    elif music_queues[guild_id]['voice_channel'] is None:
        music_queues[guild_id]['voice_channel'] = ctx.author.voice.channel


    await ctx.send(f'Procurando por: **{search_query}**...')

    try:
        with yt_dlp.YoutubeDL(YTDL_OPTIONS) as ydl: # <-- CORREÇÃO AQUI
            info = ydl.extract_info(search_query, download=False)
            # Se for uma playlist, pega a primeira música
            if 'entries' in info:
                # Filtrar para garantir que seja uma entrada de vídeo válida, não um erro
                entries = [entry for entry in info['entries'] if entry is not None]
                if not entries:
                    await ctx.send("Não encontrei vídeos válidos na playlist ou busca.")
                    return
                song_url = entries[0]['webpage_url']
                title = entries[0].get('title', 'Música da Playlist')
            else:
                song_url = info['webpage_url']
                title = info.get('title', 'Música Desconhecida')

        # Verifica se já está tocando
        if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
            # Se já estiver tocando, adiciona à fila
            music_queues[guild_id]['queue'].append(song_url)
            await ctx.send(f'**{title}** adicionada à fila. Posição: {len(music_queues[guild_id]["queue"])}')
        else:
            # Se não estiver tocando, adiciona à fila e inicia a reprodução
            music_queues[guild_id]['queue'].append(song_url)
            await play_next_song(ctx) # Inicia a reprodução
    except Exception as e:
        await ctx.send(f"Não consegui encontrar ou reproduzir a música. Erro: {e}")
        print(f"Erro ao buscar/reproduzir: {e}")


@client.command(name='stop', help='Para a música atual e limpa a fila.')
async def stop(ctx):
    """
    Comando para parar a música atual e limpar a fila.
    """
    guild_id = ctx.guild.id
    if ctx.voice_client and (ctx.voice_client.is_playing() or ctx.voice_client.is_paused()):
        ctx.voice_client.stop()
        if guild_id in music_queues:
            music_queues[guild_id]['queue'].clear()
            music_queues[guild_id]['current_song'] = None
        await ctx.send('Música parada e fila limpa.')
    else:
        await ctx.send('Nenhuma música está tocando.')

@client.command(name='skip', help='Pula para a próxima música na fila.')
async def skip(ctx):
    """
    Comando para pular para a próxima música na fila.
    """
    guild_id = ctx.guild.id
    if ctx.voice_client and (ctx.voice_client.is_playing() or ctx.voice_client.is_paused()):
        ctx.voice_client.stop() # Parar a música atual aciona o `after` callback para tocar a próxima
        await ctx.send('Pulando para a próxima música...')
    elif guild_id in music_queues and music_queues[guild_id]['queue']:
        await ctx.send('Nenhuma música tocando, mas há músicas na fila. Iniciando a próxima.')
        await play_next_song(ctx)
    else:
        await ctx.send('Nenhuma música tocando e nenhuma música na fila.')

@client.command(name='queue', help='Mostra as músicas na fila.')
async def show_queue(ctx):
    """
    Comando para mostrar as músicas na fila.
    """
    guild_id = ctx.guild.id
    if guild_id in music_queues and music_queues[guild_id]['queue']:
        # Mostra o título da música se disponível, ou a URL
        queue_titles = []
        for i, song_url in enumerate(music_queues[guild_id]['queue']):
            try:
                # Tenta extrair o título novamente para exibição
                with yt_dlp.YoutubeDL({'quiet': True, 'no_warnings': True}) as ydl:
                    info = ydl.extract_info(song_url, download=False)
                    title = info.get('title', song_url)
                queue_titles.append(f"{i+1}. {title}")
            except Exception:
                queue_titles.append(f"{i+1}. {song_url} (Erro ao obter título)")
        
        queue_list = "\n".join(queue_titles)
        await ctx.send(f'**Fila de Música:**\n{queue_list}')
    else:
        await ctx.send('A fila de música está vazia.')

@client.command(name='nowplaying', help='Mostra a música que está tocando agora.')
async def now_playing(ctx):
    """
    Comando para mostrar a música que está tocando agora.
    """
    guild_id = ctx.guild.id
    if guild_id in music_queues and music_queues[guild_id]['current_song']:
        song_url = music_queues[guild_id]['current_song']
        try:
            with yt_dlp.YoutubeDL({'quiet': True, 'no_warnings': True}) as ydl:
                info = ydl.extract_info(song_url, download=False)
                title = info.get('title', song_url)
            await ctx.send(f"Tocando agora: **{title}**")
        except Exception:
            await ctx.send(f"Tocando agora: **{song_url}** (Título não disponível)")
    else:
        await ctx.send("Nenhuma música está tocando no momento.")

@client.command(name='pause', help='Pausa a música atual.')
async def pause(ctx):
    """
    Comando para pausar a música atual.
    """
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send('Música pausada.')
    else:
        await ctx.send('Nenhuma música está tocando para pausar.')

@client.command(name='resume', help='Retoma a música pausada.')
async def resume(ctx):
    """
    Comando para retomar a música pausada.
    """
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send('Música retomada.')
    else:
        await ctx.send('Nenhuma música pausada para retomar.')


# --- Inicia o Bot ---
if __name__ == '__main__':
    if TOKEN is None:
        print("Erro: O token do Discord não foi encontrado. Certifique-se de que a variável de ambiente DISCORD_TOKEN esteja definida no arquivo .env.")
    else:
        try:
            client.run(TOKEN)
        except discord.errors.LoginFailure:
            print("Erro de login: O token do Discord é inválido. Verifique se o token está correto no arquivo .env.")
        except Exception as e:
            print(f"Ocorreu um erro ao iniciar o bot: {e}")