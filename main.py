"""
Bot de Música para Discord - Arquivo Principal
Versão refatorada com melhorias de arquitetura e UX
"""
import discord
from discord.ext import commands
import asyncio
import os
from config import DISCORD_TOKEN

class MusicBot(commands.Bot):
    """Classe principal do bot de música"""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.voice_states = True
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None  # Vamos criar um comando help customizado
        )
    
    async def setup_hook(self):
        """Carrega os cogs quando o bot inicia"""
        try:
            await self.load_extension('cogs.music')
            await self.load_extension('cogs.events')
            print("✅ Todos os cogs foram carregados com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao carregar cogs: {e}")
    
    async def close(self):
        """Limpa recursos antes de fechar"""
        music_cog = self.get_cog('Music')
        if music_cog and hasattr(music_cog, 'music_manager'):
            await music_cog.music_manager.cleanup_all()
        await super().close()

# Comando help customizado
@commands.command(name='help')
async def help_command(ctx, command_name: str = None):
    """Comando de ajuda customizado"""
    if command_name:
        # Ajuda para comando específico
        command = ctx.bot.get_command(command_name)
        if command:
            embed = discord.Embed(
                title=f"Ajuda - !{command.name}",
                description=command.help or "Sem descrição disponível",
                color=discord.Color.blue()
            )
            if command.aliases:
                embed.add_field(
                    name="Aliases",
                    value=", ".join([f"!{alias}" for alias in command.aliases]),
                    inline=False
                )
            embed.add_field(
                name="Uso",
                value=f"`!{command.name} {command.signature}`",
                inline=False
            )
        else:
            embed = discord.Embed(
                title="❌ Comando não encontrado",
                description=f"O comando `{command_name}` não existe.",
                color=discord.Color.red()
            )
    else:
        # Ajuda geral
        embed = discord.Embed(
            title="🎵 Bot de Música - Comandos",
            description="Aqui estão todos os comandos disponíveis:",
            color=discord.Color.blue()
        )
        
        # Comandos básicos
        embed.add_field(
            name="🎵 Reprodução",
            value=(
                "`!join` - Conectar ao canal de voz\n"
                "`!leave` - Desconectar do canal\n"
                "`!play <música>` - Tocar uma música\n"
                "`!search <termo>` - Buscar e selecionar música\n"
                "`!pause` - Pausar música\n"
                "`!resume` - Retomar música\n"
                "`!skip` - Pular música\n"
                "`!stop` - Parar e limpar fila"
            ),
            inline=False
        )
        
        # Comandos de fila
        embed.add_field(
            name="📋 Fila",
            value=(
                "`!queue` - Ver fila de músicas\n"
                "`!shuffle` - Embaralhar fila\n"
                "`!remove <número>` - Remover música da fila\n"
                "`!nowplaying` - Música atual"
            ),
            inline=False
        )
        
        # Comandos de controle
        embed.add_field(
            name="🔧 Controles",
            value=(
                "`!volume [0-100]` - Ajustar/ver volume\n"
                "`!loop` - Ativar/desativar loop\n"
            ),
            inline=False
        )
        
        embed.set_footer(text="Use !help <comando> para mais detalhes sobre um comando específico")
    
    await ctx.send(embed=embed)

async def main():
    """Função principal"""
    if not DISCORD_TOKEN:
        print("❌ Erro: Token do Discord não encontrado!")
        print("Certifique-se de que a variável DISCORD_TOKEN está definida no arquivo .env")
        return
    
    bot = MusicBot()
    bot.add_command(help_command)
    
    try:
        print("🚀 Iniciando bot...")
        await bot.start(DISCORD_TOKEN)
    except discord.LoginFailure:
        print("❌ Erro de login: Token inválido!")
    except KeyboardInterrupt:
        print("\n🛑 Bot interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
    finally:
        if not bot.is_closed():
            await bot.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Até logo!")