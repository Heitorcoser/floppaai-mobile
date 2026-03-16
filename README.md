# 🐱 FloppaAI — IA APP Floppa

Assistente de IA especializado em **Floppa's Schoolhouse 2** (Roblox).  
Disponível em 3 versões: **App Desktop (PC)**, **App Mobile (PWA)** e **Site Web (PC + Mobile)**.

---

## 🌐 Acesso Web

| Plataforma | Link |
|---|---|
| 🔀 Auto-detect | https://heitorcoser.github.io/floppaai-mobile/ |
| 🖥️ PC | https://heitorcoser.github.io/floppaai-mobile/desktop/ |
| 📱 Mobile (PWA) | https://heitorcoser.github.io/floppaai-mobile/mobile/ |

> O link principal detecta automaticamente se é PC ou celular e redireciona para a versão certa.

---

## 📁 Estrutura do Projeto

```
FloppaAI/
├── app.py                ← App desktop (Python + CustomTkinter)
├── dev_mode.py           ← Painel do desenvolvedor (senha protegida)
├── server.py             ← Servidor local (serve mobile/ e desktop/)
├── build.bat             ← Compila app.py para .exe
├── EXECUTAR.bat          ← Abre o app desktop
├── INICIAR_SERVIDOR.bat  ← Inicia servidor + ngrok
├── ABRIR_DEV.bat         ← Abre o modo desenvolvedor
├── requirements.txt      ← Dependências Python
├── version.json          ← Versão atual (update checker)
├── support.json          ← Tickets de suporte
├── bugs.json             ← Bug reports
├── announcements.json    ← Anúncios publicados
├── ngrok_url.txt         ← URL atual do ngrok (auto-gerado)
├── assets/
│   └── icon.ico          ← Ícone do app
├── mobile/               ← Versão PWA (celular)
│   ├── index.html
│   ├── manifest.json
│   ├── sw.js
│   ├── icon-192.png
│   └── icon-512.png
├── desktop/              ← Versão Web (PC)
│   └── index.html
└── index.html            ← Redirect automático PC/mobile
```

---

## 🚀 Como usar

### 🖥️ App Desktop (PC)
1. Instale as dependências: `pip install -r requirements.txt`
2. Execute `EXECUTAR.bat` ou `python app.py`
3. O app se registra no startup do Windows automaticamente

### 📱 App Mobile (PWA)
1. Acesse https://heitorcoser.github.io/floppaai-mobile/mobile/ no celular
2. Toque em **"Instalar"** quando o banner aparecer
3. O app vai aparecer na tela inicial como um ícone

### 🌐 Versão Web com servidor local
1. Execute `INICIAR_SERVIDOR.bat`
2. Copie a URL do ngrok exibida (ex: `https://xxxx.ngrok-free.app`)
3. Acesse essa URL no celular — conecta automaticamente!
4. No PC, acesse `http://localhost:8080`

---

## 🛠️ Modo Desenvolvedor
1. Execute `ABRIR_DEV.bat` ou `python dev_mode.py`
2. Senha padrão: `Heitor@cris`
3. Painéis disponíveis:
   - 📊 Dashboard com estatísticas
   - 📨 Inbox de tickets de suporte
   - 🐛 Bug reports
   - 👥 Gerenciamento de usuários
   - 🛡️ Anti-spam
   - 📢 Publicar anúncios
   - 🔖 Gerenciar versão
   - 📋 Logs de atividade
   - ⚙️ Configurações (ngrok, senha, anti-spam)

---

## ✅ Funcionalidades

- 💬 Chat com IA especializada (Groq / Llama 3.1)
- 📷 Upload de imagens para análise visual (versão PC)
- ⚡ Ações rápidas na barra lateral / botões de atalho
- 🔄 Sistema de verificação de updates automático
- 📱 Versão PWA instalável no celular
- 🎧 Sistema de suporte com tickets
- 🐛 Bug report automático detectado pela IA
- 📢 Anúncios em tempo real para todos os usuários
- 🛡️ Anti-spam integrado no servidor
- 🔀 Detecção automática PC/mobile no site

---

## 🧑‍💻 Criadores

- **heitorcoser** & **heitordc2019** — Criadores do FloppaAI e do jogo
- **Leandro** — Divulgador

---

*Floppa's Schoolhouse 2 — Roblox*
