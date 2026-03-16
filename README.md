# FloppaAI — Assistente IA

Assistente especializado em **Floppa's Schoolhouse 2** com versão PC (.exe) e Mobile (PWA).

---

## 📁 Estrutura
```
FloppaAI/
├── app.py              ← App desktop (Python)
├── build.bat           ← Compila para .exe
├── make_icon.py        ← Gera ícones a partir da imagem
├── make_icon.bat       ← Executa o make_icon.py
├── requirements.txt    ← Dependências Python
├── version.json        ← Versão atual (para update checker)
├── assets/
│   └── icon.ico        ← Ícone do app (gerado pelo make_icon)
└── mobile/
    ├── index.html      ← App mobile (PWA instalável)
    ├── manifest.json   ← Manifesto PWA
    ├── icon-192.png    ← Ícone mobile (gerado pelo make_icon)
    └── icon-512.png    ← Ícone mobile grande
```

---

## 🚀 Como usar

### PC — Gerar o .exe
1. Salve a imagem da porta do Floppa como `icon_source.png` nesta pasta
2. Execute `make_icon.bat` para gerar os ícones
3. Execute `build.bat` para compilar
4. O `.exe` estará em `dist\FloppaAI.exe`
5. O app se instala automaticamente no startup do PC na primeira execução

### Mobile — Instalar no celular
1. Abra `mobile/index.html` em um servidor local ou hospede online
2. No celular, acesse a URL e toque em "Instalar" quando o banner aparecer
3. O app será instalado como um ícone na tela inicial

### Update Checker
- Hospede o `version.json` online (GitHub, etc.)
- Atualize a URL em `app.py` na variável `VERSION_URL`
- Faça o mesmo em `mobile/index.html` na variável `VER_URL`

---

## ✅ Funcionalidades
- 💬 Chat com IA especializada (Groq/Llama)
- 📷 Upload de imagens do jogo para análise visual
- ⚡ Ações rápidas na barra lateral
- 🔄 Sistema de verificação de updates
- 🚀 Auto-startup no Windows
- 📱 Versão PWA instalável no celular
