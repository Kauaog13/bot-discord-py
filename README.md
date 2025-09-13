# 🎵 Bot de Música para Discord

Um bot de música avançado desenvolvido em **Python** para reprodução de áudio diretamente em canais de voz do **Discord**. O bot possui arquitetura modular com Cogs, interface moderna com botões interativos, gerenciamento robusto de estado e muitas funcionalidades avançadas!

## 🚀 Funcionalidades

### 🎵 Reprodução
- ✅ Reproduz músicas via link ou termos de busca do YouTube
- ✅ Busca interativa com seleção de resultados
- ✅ Controle de volume (0-100%)
- ✅ Sistema de loop para repetir músicas
- ✅ Pausa, retomar, pular e parar músicas

### 📋 Gerenciamento de Fila
- ✅ Filas de reprodução independentes por servidor
- ✅ Embaralhar fila de músicas
- ✅ Remover músicas específicas da fila
- ✅ Visualização paginada da fila
- ✅ Limite de músicas na fila para evitar spam

### 🎮 Interface Moderna
- ✅ Embeds ricos com thumbnails e informações detalhadas
- ✅ Botões interativos para controle de reprodução
- ✅ Mensagens de status em tempo real
- ✅ Sistema de busca com seleção por botões

### 🔧 Recursos Avançados
- ✅ Arquitetura modular com Cogs
- ✅ Gerenciamento robusto de estado por servidor
- ✅ Desconexão automática por inatividade
- ✅ Tratamento avançado de erros
- ✅ Suporte a múltiplos servidores simultaneamente
- ✅ Recuperação automática de falhas

## 🛠 Tecnologias usadas

- **Python 3.8+**
- **[discord.py](https://pypi.org/project/discord.py/)** (para integração com o Discord)
- **[yt-dlp](https://pypi.org/project/yt-dlp/)** (para extrair áudio do YouTube)
- **[PyNaCl](https://pypi.org/project/PyNaCl/)** (necessário para áudio no Discord)
- **[python-dotenv](https://pypi.org/project/python-dotenv/)** (para ler o token do arquivo `.env`)
- **[FFmpeg](https://ffmpeg.org/)** (ferramenta externa para processar áudio)

## 📂 Estrutura básica do projeto

```
📁 projeto/
├── 📄 main.py                 # Arquivo principal do bot
├── 📄 config.py              # Configurações centralizadas
├── 📄 .env                   # Token e variáveis de ambiente
├── 📄 requirements.txt       # Dependências do projeto
├── 📄 ambiente.md           # Guia de instalação detalhado
├── 📁 cogs/                 # Módulos do bot (Cogs)
│   ├── 📄 music.py          # Comandos de música
│   └── 📄 events.py         # Eventos do bot
└── 📁 utils/                # Utilitários
    ├── 📄 music_manager.py  # Gerenciador de estado
    ├── 📄 embeds.py         # Criação de embeds
    └── 📄 views.py          # Componentes de UI
```


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

4️⃣ **Execute o bot**
```bash
python main.py
```
## 🎮 Comandos disponíveis

### 🎵 Reprodução
- `!join` — Conecta ao seu canal de voz
- `!leave` — Desconecta do canal de voz
- `!play <música>` — Reproduz uma música
- `!search <termo>` — Busca e permite selecionar música
- `!pause` — Pausa a música atual
- `!resume` — Retoma a música pausada
- `!skip` — Pula para a próxima música
- `!stop` — Para a música e limpa a fila

### 📋 Fila
- `!queue` — Mostra a fila de músicas
- `!shuffle` — Embaralha a fila
- `!remove <número>` — Remove música da fila
- `!nowplaying` — Mostra a música atual

### 🔧 Controles
- `!volume [0-100]` — Ajusta/mostra o volume
- `!loop` — Ativa/desativa loop da música
- `!help [comando]` — Mostra ajuda geral ou específica

## 🎮 Controles Interativos

O bot possui botões interativos nas mensagens de "Tocando Agora":
- ⏯️ **Play/Pause** — Pausa ou retoma a música
- ⏭️ **Skip** — Pula para a próxima música
- ⏹️ **Stop** — Para e limpa a fila
- 🔀 **Shuffle** — Embaralha a fila
- 🔁 **Loop** — Ativa/desativa repetição
## 💡 Observações

- ✅ Suporte completo a múltiplos servidores
- ✅ Estado independente para cada servidor
- ✅ Desconexão automática após 5 minutos de inatividade
- ✅ Limite de 50 músicas por fila para evitar spam
- ✅ Recuperação automática de erros de reprodução

- ⚠️ Necessário o FFmpeg instalado e configurado no PATH do sistema

- 🔗 Painel Desenvolvedor do Discord: **[discord.dev](https://discord.com/developers/applications)**

## 🆕 Novidades da Versão Refatorada

- 🏗️ **Arquitetura Modular**: Código organizado em Cogs para melhor manutenção
- 🎨 **Interface Moderna**: Embeds ricos e botões interativos
- 🔧 **Gerenciamento Robusto**: Sistema de estado avançado por servidor
- 🛡️ **Tratamento de Erros**: Recuperação automática e mensagens claras
- 🔍 **Busca Interativa**: Seleção de músicas com botões
- 🎛️ **Controles Avançados**: Volume, loop, shuffle e mais
- ⚡ **Performance**: Otimizações e melhor uso de recursos
- 📱 **UX Melhorada**: Feedback visual e interações intuitivas