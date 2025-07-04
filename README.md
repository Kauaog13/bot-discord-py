# 🎵 Bot de Música para Discord

Um bot de música desenvolvido em **Python** para reprodução de áudio diretamente em canais de voz do **Discord**. O bot suporta busca e reprodução de músicas do **YouTube**, gerenciamento de fila, e comandos como `play`, `pause`, `resume`, `skip`, `stop` e mais!

## 🚀 Funcionalidades

- ✅ Reproduz músicas via link ou termos de busca do YouTube
- ✅ Gerencia filas de reprodução (por servidor)
- ✅ Comandos intuitivos com prefixo `!`
- ✅ Conecta, desconecta e move entre canais de voz
- ✅ Suporte a múltiplos servidores ao mesmo tempo
- ✅ Mensagens informativas no chat sobre status da reprodução

## 🛠 Tecnologias usadas

- **Python 3.8+**
- **[discord.py](https://pypi.org/project/discord.py/)** (para integração com o Discord)
- **[yt-dlp](https://pypi.org/project/yt-dlp/)** (para extrair áudio do YouTube)
- **[PyNaCl](https://pypi.org/project/PyNaCl/)** (necessário para áudio no Discord)
- **[python-dotenv](https://pypi.org/project/python-dotenv/)** (para ler o token do arquivo `.env`)
- **[FFmpeg](https://ffmpeg.org/)** (ferramenta externa para processar áudio)

## 📂 Estrutura básica do projeto

| bot.py # Arquivo principal do bot  
| .env # Arquivo contendo o token do Discord  
| requirements.txt # Dependências do projeto
| ambiente.md ## Guia Passo a Passo detalhadamente de como executar o projeto


## ⚙️ Como executar o projeto

1️⃣ **Clone o repositório**
```bash
git clone https://github.com/Kauaog13/bot-discord-py.git
cd bot-discord-py
```

2️⃣ **Crie e edite o arquivo .env**  

```
DISCORD_TOKEN=seu_token_aqui
```

3️⃣ **Instale as dependências**  

```
pip install -r requirements.txt
```

## 🎮 Comandos disponíveis

- !join — Entra no seu canal de voz  
- !leave — Sai do canal de voz  
- !play <link ou termo> — Reproduz uma música  
- !pause — Pausa a música atual  
- !resume — Retoma a música pausada  
- !stop — Para a música e limpa a fila  
- !skip — Pula para a próxima música  
- !queue — Mostra as músicas na fila  
- !nowplaying — Mostra a música que está tocando

## 💡 Observações

- O bot suporta múltiplos servidores (guilds).  

- Necessário o FFmpeg instalado e configurado no PATH do sistema.  
