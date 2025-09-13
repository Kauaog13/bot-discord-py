"""
Cog de eventos do bot
"""
import discord
from discord.ext import commands
from utils.embeds import MusicEmbeds

class Events(commands.Cog):
    """Eventos do bot"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        """Evento disparado quando o bot está pronto"""
        print(f'🎵 Bot {self.bot.user} está online!')
        print(f'ID: {self.bot.user.id}')
        print(f'Servidores: {len(self.bot.guilds)}')
        
        # Define atividade do bot
        activity = discord.Activity(
            type=discord.ActivityType.listening,
            name="música | !help"
        )
        await self.bot.change_presence(activity=activity)
        
        for guild in self.bot.guilds:
            print(f'  - {guild.name} (ID: {guild.id})')
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Tratamento global de erros"""
        if isinstance(error, commands.CommandNotFound):
            embed = MusicEmbeds.error_embed(
                "Comando Não Encontrado",
                f"O comando `{ctx.invoked_with}` não existe. Use `!help` para ver os comandos disponíveis."
            )
            await ctx.send(embed=embed, delete_after=10)
            
        elif isinstance(error, commands.MissingRequiredArgument):
            embed = MusicEmbeds.error_embed(
                "Argumento Faltando",
                f"Uso correto: `!{ctx.command.name} {ctx.command.signature}`"
            )
            await ctx.send(embed=embed, delete_after=10)
            
        elif isinstance(error, commands.BadArgument):
            embed = MusicEmbeds.error_embed(
                "Argumento Inválido",
                f"Verifique os argumentos do comando. Use `!help {ctx.command.name}` para mais informações."
            )
            await ctx.send(embed=embed, delete_after=10)
            
        elif isinstance(error, commands.CommandOnCooldown):
            embed = MusicEmbeds.error_embed(
                "Comando em Cooldown",
                f"Aguarde {error.retry_after:.1f} segundos antes de usar este comando novamente."
            )
            await ctx.send(embed=embed, delete_after=5)
            
        elif isinstance(error, commands.BotMissingPermissions):
            perms = ', '.join(error.missing_permissions)
            embed = MusicEmbeds.error_embed(
                "Permissões Insuficientes",
                f"Preciso das seguintes permissões: {perms}"
            )
            await ctx.send(embed=embed)
            
        elif isinstance(error, commands.MissingPermissions):
            perms = ', '.join(error.missing_permissions)
            embed = MusicEmbeds.error_embed(
                "Sem Permissão",
                f"Você precisa das seguintes permissões: {perms}"
            )
            await ctx.send(embed=embed, delete_after=10)
            
        else:
            # Log do erro para debug
            print(f'Erro não tratado no comando {ctx.command}: {error}')
            
            embed = MusicEmbeds.error_embed(
                "Erro Interno",
                "Ocorreu um erro inesperado. Tente novamente em alguns instantes."
            )
            await ctx.send(embed=embed, delete_after=10)
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Evento de mudança de estado de voz"""
        # Se o bot foi desconectado do canal
        if member == self.bot.user and before.channel and not after.channel:
            # Limpa o estado do servidor
            music_cog = self.bot.get_cog('Music')
            if music_cog and hasattr(music_cog, 'music_manager'):
                await music_cog.music_manager.cleanup_guild(before.channel.guild.id)
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """Evento quando o bot entra em um servidor"""
        print(f'📥 Entrei no servidor: {guild.name} (ID: {guild.id})')
        
        # Tenta encontrar um canal para enviar mensagem de boas-vindas
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                embed = discord.Embed(
                    title="🎵 Olá! Sou um bot de música",
                    description="Obrigado por me adicionar ao servidor!\n\nUse `!help` para ver todos os comandos disponíveis.",
                    color=discord.Color.green()
                )
                embed.add_field(
                    name="Comandos Básicos",
                    value="`!join` - Entrar no canal de voz\n`!play <música>` - Tocar uma música\n`!queue` - Ver a fila",
                    inline=False
                )
                embed.set_footer(text="Desenvolvido com ❤️ em Python")
                await channel.send(embed=embed)
                break
    
    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        """Evento quando o bot sai de um servidor"""
        print(f'📤 Saí do servidor: {guild.name} (ID: {guild.id})')
        
        # Limpa recursos do servidor
        music_cog = self.bot.get_cog('Music')
        if music_cog and hasattr(music_cog, 'music_manager'):
            await music_cog.music_manager.cleanup_guild(guild.id)

async def setup(bot):
    await bot.add_cog(Events(bot))