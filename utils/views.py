"""
Views e componentes de UI do Discord
"""
import discord
from discord.ext import commands
from typing import Optional
from utils.music_manager import MusicManager

class MusicControlView(discord.ui.View):
    """View com botões de controle de música"""
    
    def __init__(self, music_manager: MusicManager, guild_id: int):
        super().__init__(timeout=300)
        self.music_manager = music_manager
        self.guild_id = guild_id
    
    @discord.ui.button(emoji="⏯️", style=discord.ButtonStyle.primary)
    async def play_pause(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Botão de play/pause"""
        manager = self.music_manager.get_guild_manager(self.guild_id)
        
        if not manager.voice_client:
            await interaction.response.send_message("❌ Não estou conectado a um canal de voz!", ephemeral=True)
            return
            
        if manager.voice_client.is_playing():
            manager.voice_client.pause()
            manager.is_paused = True
            await interaction.response.send_message("⏸️ Música pausada", ephemeral=True)
        elif manager.voice_client.is_paused():
            manager.voice_client.resume()
            manager.is_paused = False
            await interaction.response.send_message("▶️ Música retomada", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Nenhuma música está tocando!", ephemeral=True)
    
    @discord.ui.button(emoji="⏭️", style=discord.ButtonStyle.secondary)
    async def skip(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Botão de skip"""
        manager = self.music_manager.get_guild_manager(self.guild_id)
        
        if not manager.voice_client or not manager.voice_client.is_playing():
            await interaction.response.send_message("❌ Nenhuma música está tocando!", ephemeral=True)
            return
            
        manager.voice_client.stop()
        await interaction.response.send_message("⏭️ Música pulada", ephemeral=True)
    
    @discord.ui.button(emoji="⏹️", style=discord.ButtonStyle.danger)
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Botão de stop"""
        manager = self.music_manager.get_guild_manager(self.guild_id)
        
        if manager.voice_client:
            manager.voice_client.stop()
            manager.clear_queue()
            manager.current_song = None
            await interaction.response.send_message("⏹️ Reprodução parada e fila limpa", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Não estou tocando nada!", ephemeral=True)
    
    @discord.ui.button(emoji="🔀", style=discord.ButtonStyle.secondary)
    async def shuffle(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Botão de shuffle"""
        manager = self.music_manager.get_guild_manager(self.guild_id)
        
        if not manager.queue:
            await interaction.response.send_message("❌ A fila está vazia!", ephemeral=True)
            return
            
        manager.shuffle_queue()
        await interaction.response.send_message("🔀 Fila embaralhada", ephemeral=True)
    
    @discord.ui.button(emoji="🔁", style=discord.ButtonStyle.secondary)
    async def loop(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Botão de loop"""
        manager = self.music_manager.get_guild_manager(self.guild_id)
        
        manager.is_looping = not manager.is_looping
        status = "ativado" if manager.is_looping else "desativado"
        emoji = "🔁" if manager.is_looping else "➡️"
        
        await interaction.response.send_message(f"{emoji} Loop {status}", ephemeral=True)

class SearchResultView(discord.ui.View):
    """View para seleção de resultados de busca"""
    
    def __init__(self, results: list, music_manager: MusicManager, guild_id: int, requester: discord.Member):
        super().__init__(timeout=60)
        self.results = results
        self.music_manager = music_manager
        self.guild_id = guild_id
        self.requester = requester
        
        # Adiciona botões numerados para cada resultado
        for i in range(min(len(results), 5)):
            button = discord.ui.Button(
                label=str(i + 1),
                style=discord.ButtonStyle.primary,
                custom_id=f"select_{i}"
            )
            button.callback = self.create_callback(i)
            self.add_item(button)
    
    def create_callback(self, index: int):
        """Cria callback para botão específico"""
        async def callback(interaction: discord.Interaction):
            if interaction.user != self.requester:
                await interaction.response.send_message("❌ Apenas quem fez a busca pode selecionar!", ephemeral=True)
                return
                
            # Aqui você implementaria a lógica para adicionar a música selecionada
            result = self.results[index]
            await interaction.response.send_message(f"✅ Selecionado: **{result.get('title', 'Música')}**", ephemeral=True)
            self.stop()
            
        return callback

class VolumeModal(discord.ui.Modal):
    """Modal para ajuste de volume"""
    
    def __init__(self, music_manager: MusicManager, guild_id: int):
        super().__init__(title="Ajustar Volume")
        self.music_manager = music_manager
        self.guild_id = guild_id
        
        self.volume_input = discord.ui.TextInput(
            label="Volume (0-100)",
            placeholder="Digite um valor entre 0 e 100",
            min_length=1,
            max_length=3
        )
        self.add_item(self.volume_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            volume = int(self.volume_input.value)
            if not 0 <= volume <= 100:
                raise ValueError("Volume deve estar entre 0 e 100")
                
            manager = self.music_manager.get_guild_manager(self.guild_id)
            manager.volume = volume / 100.0
            
            if manager.voice_client and hasattr(manager.voice_client.source, 'volume'):
                manager.voice_client.source.volume = manager.volume
                
            await interaction.response.send_message(f"🔊 Volume ajustado para {volume}%", ephemeral=True)
            
        except ValueError as e:
            await interaction.response.send_message(f"❌ Erro: {e}", ephemeral=True)