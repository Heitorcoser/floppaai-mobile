import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import base64
import requests
import os
import sys
import winreg
from PIL import Image
import io

# ── Configurações ─────────────────────────────────────────────────────────────
APP_NAME        = "FloppaAI"
APP_VERSION     = "1.0.0"
GROQ_API_KEY    = "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"
GROQ_URL        = "https://api.groq.com/openai/v1/chat/completions"
MODEL_TEXT      = "llama-3.1-8b-instant"
MODEL_VISION    = "llama-3.2-11b-vision-preview"
VERSION_URL     = "https://raw.githubusercontent.com/floppaai/releases/main/version.json"
DISCORD_WEBHOOK   = "https://discord.com/api/webhooks/1482758475896455382/nqptHsfVF4-i7D10lUEJGTgM_sWL_F0vya34nzk5i_XJeMhOaH_3fcRKyCpy8xYDFKre"
SUPPORT_WEBHOOK   = "https://discord.com/api/webhooks/1482758475896455382/nqptHsfVF4-i7D10lUEJGTgM_sWL_F0vya34nzk5i_XJeMhOaH_3fcRKyCpy8xYDFKre"
BUGS_FILE         = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bugs.json")
SUPPORT_FILE      = os.path.join(os.path.dirname(os.path.abspath(__file__)), "support.json")
NGROK_URL_FILE    = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ngrok_url.txt")

# ── Resolução automática da URL do servidor ───────────────────────────────────
# Funciona de QUALQUER PC, em QUALQUER lugar:
#   1. Tenta localhost:8080  (mesmo PC que roda o servidor)
#   2. Fallback: lê ngrok_url.txt (PC remoto / outro lugar)
# Nenhuma configuração manual necessária.

_cached_server_url = None   # cache em memória para não ficar testando a cada envio

def _read_ngrok_url():
    """Lê a URL do ngrok salva pelo Dev Mode."""
    try:
        with open(NGROK_URL_FILE, "r", encoding="utf-8") as f:
            return f.read().strip().rstrip("/")
    except Exception:
        return None

def get_server_url(force_recheck=False):
    """
    Retorna a URL correta do servidor automaticamente.
    - Mesmo PC  → http://localhost:8080
    - PC remoto → URL do ngrok_url.txt
    """
    global _cached_server_url
    if _cached_server_url and not force_recheck:
        return _cached_server_url

    # Tenta localhost primeiro (servidor rodando na mesma máquina)
    try:
        r = requests.get("http://localhost:8080/api/ping", timeout=2)
        if r.status_code == 200:
            _cached_server_url = "http://localhost:8080"
            return _cached_server_url
    except Exception:
        pass

    # Fallback: usa URL do ngrok configurada pelo Dev Mode
    ngrok = _read_ngrok_url()
    if ngrok:
        _cached_server_url = ngrok
        return _cached_server_url

    return None   # servidor não encontrado

def server_online():
    """Verifica se há servidor disponível (local ou ngrok)."""
    return get_server_url(force_recheck=True) is not None

SYSTEM_PROMPT = """Você é um assistente profissional especializado exclusivamente no jogo "Floppa's Schoolhouse 2" da plataforma Roblox.
Você NÃO conhece nenhum outro jogo ou tema. Se perguntarem sobre outro assunto, diga que só pode ajudar com Floppa's Schoolhouse 2.
NUNCA invente informações. Responda apenas o que está nas suas instruções.

INFORMAÇÕES GERAIS:
- Nome: Floppa's Schoolhouse 2 | Plataforma: Roblox
- Criadores: heitorcoser e heitordc2019 | Divulgador: Leandro
- Estilo: Escola no estilo de Baldi's Basics

TUTORIAL / INÍCIO:
- O jogo começa com o jogador na entrada da escola, onde o Baldi aparece.
- O jogador vai até as salas de aula e coleta os livros.
- Cada livro tem 3 questões para resolver.
- Se errar UMA questão: apenas aquela questão é marcada como errada (o livro NÃO é marcado como errado por uma questão só).
- O livro só é marcado como errado se o jogador errar TODAS as questões dele.
- Ao errar uma questão, aparece a cutscene do Baldi morrendo: o Floppa aparece no fundo da tela perto da diretoria e mata o Baldi.
- Após a cutscene, o Floppa começa a perseguir o jogador.
- Ao coletar um livro, ele desaparece do cenário e é marcado como concluído no menu no topo da tela.
- O objetivo é coletar e resolver as questões de 7 livros no total para conseguir escapar pela saída correta.

OBJETIVO: Coletar 7 livros espalhados pelo mapa e encontrar a saída correta para escapar da escola.
Se encontrar saída errada, ela desaparece e vira parede. Sem eventos no momento.

MECÂNICAS:
- Cada livro tem 3 questões. Errar uma = só a questão marcada errada. Errar TODAS = livro marcado errado.
- A cada erro nas questões, Floppa fica mais rápido.
- Ao coletar os 7 livros, Floppa também fica mais rápido.
- Floppa tem audição inteligente: detecta sons para rastrear o jogador.
- Stamina: recupera 100% a cada livro coletado. Bebedouros nos corredores também recuperam stamina.
- Swimming Doors: precisa de 2+ livros para passar. Baldi avisa sem aparecer fisicamente.

PERSONAGENS:
- BALDI: presente no início. Morre na cutscene se jogador errar questão.
- FLOPPA: perseguidor principal. Usa audição. Fica mais rápido a cada erro e ao coletar 7 livros.
- CARRO (vermelho): ativado após 2+ livros. A cada 20s percorre o mapa derrubando tudo.
  Não tem como fugir. Esperar 10-12s ou terminar o percurso para ficar livre.
- X9: personagem que ao chegar aproximadamente 10 metros do jogador, revela a POSIÇÃO DO JOGADOR ao Floppa por 60 segundos.

SALAS DO MAPA:
- Salas de aula (carpete azul, mesas amarelas): onde ficam os livros. Porta numerada cinza.
  Uma das salas tem um balão laranja. Quadro negro escrito "Floppa, Floppa."
- Sala do Carro (vermelho): porta amarela escrita "Supplies". Carro vermelho fica aqui.
- Cafeteria (chão branco, bancos amarelos): pode ter uma saída para escapar com 7 livros.
- Corredores: maioria tem armários ou bebedouros para recuperar stamina.
- Sala de Detenção: porta cinza numerada (ex: 67).
- Salas de funcionários: porta de madeira escrita "School Faculty Only".

ITENS:
- FITA (CASSETE): usada em máquina de fita cassete. Toca música que esconde o jogador do Floppa.
  Faz Floppa perseguir o som por 60 segundos.

CURIOSIDADES: O jogo possui sons secretos não utilizados.
SUPORTE A BUGS: Faça perguntas investigativas antes de concluir.
Quando tiver informações suficientes sobre o bug (após pelo menos 2 perguntas investigativas respondidas), inicie sua resposta EXATAMENTE com esta linha (sem nada antes):
🐛BUG_REPORT: [resumo do bug em uma linha]
E depois continue a resposta normalmente dizendo que o bug foi registrado e que a equipe irá analisar.
Se não souber algo: "Não tenho essa informação sobre Floppa's Schoolhouse 2."
Responda sempre em português do Brasil."""

# ── Startup registration ──────────────────────────────────────────────────────
def add_to_startup():
    try:
        exe_path = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__)
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Software\Microsoft\Windows\CurrentVersion\Run",
                             0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, f'"{exe_path}"')
        winreg.CloseKey(key)
    except Exception:
        pass

def remove_from_startup():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Software\Microsoft\Windows\CurrentVersion\Run",
                             0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, APP_NAME)
        winreg.CloseKey(key)
    except Exception:
        pass

def is_in_startup():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Software\Microsoft\Windows\CurrentVersion\Run",
                             0, winreg.KEY_READ)
        winreg.QueryValueEx(key, APP_NAME)
        winreg.CloseKey(key)
        return True
    except Exception:
        return False

# ── Update check ──────────────────────────────────────────────────────────────
def check_update(callback):
    def _check():
        try:
            r = requests.get(VERSION_URL, timeout=5)
            data = r.json()
            remote = tuple(int(x) for x in data["version"].split("."))
            local  = tuple(int(x) for x in APP_VERSION.split("."))
            callback(remote > local, data.get("version"), data.get("notes", ""))
        except Exception:
            callback(False, None, "")
    threading.Thread(target=_check, daemon=True).start()

# ── Groq API ──────────────────────────────────────────────────────────────────
def compress_image_b64(b64_str, max_size=(800, 800), quality=75):
    try:
        img_bytes = base64.b64decode(b64_str)
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        img.thumbnail(max_size, Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=quality)
        return base64.b64encode(buf.getvalue()).decode()
    except Exception:
        return b64_str

def ask_groq(messages, image_b64=None, on_done=None, on_error=None):
    def _call():
        try:
            if image_b64:
                compressed = compress_image_b64(image_b64)
                text = messages[-1]["content"] if isinstance(messages[-1]["content"], str) else "Analise esta imagem."
                vision_messages = [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": [
                        {"type": "text", "text": text},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{compressed}"}}
                    ]}
                ]
                payload = {"model": MODEL_VISION, "messages": vision_messages, "max_tokens": 900, "temperature": 0.3}
            else:
                payload = {
                    "model": MODEL_TEXT,
                    "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + messages,
                    "max_tokens": 900, "temperature": 0.3
                }
            resp = requests.post(GROQ_URL,
                                 headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                                 json=payload, timeout=30)
            resp.raise_for_status()
            reply = resp.json()["choices"][0]["message"]["content"]
            if on_done: on_done(reply)
        except Exception as e:
            if on_error: on_error(str(e))
    threading.Thread(target=_call, daemon=True).start()


# ── Bug report helpers ────────────────────────────────────────────────────────
import json, datetime, uuid

def load_bugs():
    try:
        with open(BUGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_bugs(bugs):
    try:
        with open(BUGS_FILE, "w", encoding="utf-8") as f:
            json.dump(bugs, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def send_bug_to_discord(summary, bug_id):
    """
    Envia bug ao servidor (local ou remoto via ngrok).
    Detecta automaticamente qual URL usar.
    Fallback para Discord se servidor indisponível.
    """
    def _send():
        srv = get_server_url()
        if srv:
            try:
                payload = {"id": bug_id, "summary": summary, "platform": "pc"}
                r = requests.post(f"{srv}/api/bugs", json=payload, timeout=6)
                if r.status_code == 200:
                    return  # sucesso
            except Exception:
                pass
        # Fallback: Discord
        try:
            payload = {
                "embeds": [{
                    "title": "🐛 Novo Bug — Floppa's Schoolhouse 2",
                    "description": summary,
                    "color": 0xFF2200,
                    "footer": {"text": f"ID: {bug_id} | PC"},
                    "timestamp": datetime.datetime.utcnow().isoformat()
                }]
            }
            requests.post(DISCORD_WEBHOOK, json=payload, timeout=10)
        except Exception:
            pass
    threading.Thread(target=_send, daemon=True).start()

# ── Suporte helpers ───────────────────────────────────────────────────────────
def load_support():
    try:
        with open(SUPPORT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_support(tickets):
    try:
        with open(SUPPORT_FILE, "w", encoding="utf-8") as f:
            json.dump(tickets, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def send_support_to_discord(username, message, ticket_id):
    """
    Envia ticket de suporte ao servidor (local ou remoto via ngrok).
    Detecta automaticamente qual URL usar.
    Fallback para Discord se servidor indisponível.
    """
    def _send():
        srv = get_server_url()
        if srv:
            try:
                payload = {
                    "id": ticket_id, "name": username,
                    "message": message, "platform": "pc",
                    "subject": "outro"
                }
                r = requests.post(f"{srv}/api/tickets", json=payload, timeout=6)
                if r.status_code == 200:
                    return  # sucesso
            except Exception:
                pass
        # Fallback: Discord
        try:
            payload = {
                "embeds": [{
                    "title": "🎧 Nova Mensagem de Suporte — Floppa's Schoolhouse 2",
                    "description": message,
                    "color": 0x0088FF,
                    "fields": [{"name": "Usuário", "value": username, "inline": True},
                               {"name": "ID", "value": ticket_id, "inline": True}],
                    "timestamp": datetime.datetime.utcnow().isoformat()
                }]
            }
            requests.post(SUPPORT_WEBHOOK, json=payload, timeout=10)
        except Exception:
            pass
    threading.Thread(target=_send, daemon=True).start()

PALAVROES = [
    "porra","caralho","merda","viado","idiota","imbecil","otário","otario",
    "fdp","vsf","sua mãe","sua mae","vai se foder","cuzão","cuzao","buceta",
    "pau no cu","arrombado","babaca","puta","lixo","inútil","inutl",
    "heitorcoser é lixo","heitordc é lixo","dono é lixo","dono lixo",
    "criador lixo","criador idiota","criador otário","jogo lixo","jogo merda",
    "fuck","shit","bitch","asshole","damn","crap","bastard"
]

def check_moderacao(texto):
    """Retorna True se o texto for impróprio."""
    t = texto.lower()
    for p in PALAVROES:
        if p in t:
            return True, p
    return False, None

# ── UI Principal ──────────────────────────────────────────────────────────────
class FloppaAI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"FloppaAI — Assistente v{APP_VERSION}")
        self.geometry("960x680")
        self.minsize(700, 500)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.history          = []
        self.pending_image    = None
        self.pending_img_path = None
        self._thinking_bubble = None
        self.bugs             = load_bugs()
        self._selected_bug_id = None

        self._load_icon()
        self._build_ui()
        self._add_bubble("system", "Bem-vindo ao FloppaAI!\nSou especializado em Floppa's Schoolhouse 2.\nUse as ações rápidas ou digite sua pergunta.\nVocê pode enviar imagens usando o botão 📷.")

        if not is_in_startup():
            add_to_startup()
        check_update(self._on_update_check)

    def _load_icon(self):
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "icon.ico")
        if os.path.exists(icon_path):
            try: self.iconbitmap(icon_path)
            except Exception: pass

    # ── Layout ────────────────────────────────────────────────────────────────
    def _build_ui(self):
        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=210, corner_radius=0, fg_color="#0f0f0f")
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        ctk.CTkLabel(self.sidebar, text="🐱 FloppaAI",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color="#ff4422").pack(pady=(20, 2))
        ctk.CTkLabel(self.sidebar, text=f"v{APP_VERSION}",
                     font=ctk.CTkFont(size=11), text_color="#666").pack(pady=(0, 12))

        actions = [
            ("🎯  Objetivo",             "Qual é o objetivo do jogo?"),
            ("👾  Personagens",          "Me fale sobre todos os personagens."),
            ("📖  Tutorial",             "Como funciona o tutorial/início do jogo?"),
            ("🗺️  Salas do mapa",        "Quais são as salas do mapa?"),
            ("📚  Livros e questões",    "Como funcionam os livros e as questões?"),
            ("🚗  O Carro",             "Como funciona o Carro?"),
            ("📼  Fita Cassete",         "Como funciona a fita cassete?"),
            ("💡  Dicas",               "Me dê dicas para sobreviver no jogo."),
            ("🐛  Reportar bug",         "Quero reportar um bug no jogo."),
            ("❓  Curiosidades",         "Quais são as curiosidades do jogo?"),
        ]
        ctk.CTkLabel(self.sidebar, text="Ações rápidas",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color="#888").pack(pady=(4, 4))
        for label, prompt in actions:
            ctk.CTkButton(self.sidebar, text=label, height=30,
                          font=ctk.CTkFont(size=12), anchor="w",
                          fg_color="transparent", hover_color="#2a0000",
                          text_color="#ccc",
                          command=lambda p=prompt: self._quick_action(p)
                          ).pack(fill="x", padx=8, pady=1)

        ctk.CTkFrame(self.sidebar, height=1, fg_color="#222").pack(fill="x", padx=8, pady=10)

        self.update_btn = ctk.CTkButton(self.sidebar, text="✅ Atualizado",
                                         height=28, fg_color="#1a3a1a",
                                         hover_color="#2a5a2a",
                                         font=ctk.CTkFont(size=11),
                                         state="disabled", command=self._show_update)
        self.update_btn.pack(fill="x", padx=8, pady=2)

        self.startup_var = ctk.BooleanVar(value=is_in_startup())
        ctk.CTkCheckBox(self.sidebar, text="Iniciar com o PC",
                        variable=self.startup_var, font=ctk.CTkFont(size=11),
                        command=self._toggle_startup).pack(padx=12, pady=4)

        ctk.CTkButton(self.sidebar, text="🗑  Limpar chat", height=28,
                      fg_color="#2a2a2a", hover_color="#3a0000",
                      font=ctk.CTkFont(size=11),
                      command=self._clear_chat).pack(fill="x", padx=8, pady=2)

        ctk.CTkFrame(self.sidebar, height=1, fg_color="#222").pack(fill="x", padx=8, pady=8)

        self.bugs_btn = ctk.CTkButton(self.sidebar, text="🐛  Respostas de Bug",
                                       height=32, fg_color="#2a0a00",
                                       hover_color="#4a1500",
                                       font=ctk.CTkFont(size=12, weight="bold"),
                                       text_color="#ff8844",
                                       command=self._show_bugs_panel)
        self.bugs_btn.pack(fill="x", padx=8, pady=2)

        self.support_btn = ctk.CTkButton(self.sidebar, text="🎧  Suporte",
                                          height=32, fg_color="#0a1a2a",
                                          hover_color="#152a40",
                                          font=ctk.CTkFont(size=12, weight="bold"),
                                          text_color="#44aaff",
                                          command=self._show_support_panel)
        self.support_btn.pack(fill="x", padx=8, pady=2)

        # ── Área principal (chat + input) ────────────────────────────────────
        self.main = ctk.CTkFrame(self, fg_color="transparent")
        self.main.pack(side="right", fill="both", expand=True)

        # ── Painel CHAT ───────────────────────────────────────────────────────
        self.chat_panel = ctk.CTkFrame(self.main, fg_color="transparent")
        self.chat_panel.pack(fill="both", expand=True)

        # Header estilo WhatsApp
        header = ctk.CTkFrame(self.chat_panel, height=56, corner_radius=0, fg_color="#1a0000")
        header.pack(fill="x")
        header.pack_propagate(False)
        ctk.CTkLabel(header, text="🐱", font=ctk.CTkFont(size=22)).pack(side="left", padx=(14, 6), pady=8)
        info = ctk.CTkFrame(header, fg_color="transparent")
        info.pack(side="left", fill="y", pady=8)
        ctk.CTkLabel(info, text="FloppaAI",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color="#fff").pack(anchor="w")
        ctk.CTkLabel(info, text="Assistente de Floppa's Schoolhouse 2",
                     font=ctk.CTkFont(size=10), text_color="#ff8866").pack(anchor="w")
        self.online_dot = ctk.CTkLabel(header, text="● online",
                                        font=ctk.CTkFont(size=10), text_color="#00dd66")
        self.online_dot.pack(side="right", padx=14)
        # Label de status do servidor (auto-detectado)
        self.srv_status_lbl = ctk.CTkLabel(header, text="🔌 verificando servidor...",
                                            font=ctk.CTkFont(size=9), text_color="#666")
        self.srv_status_lbl.pack(side="right", padx=(0, 4))
        # Inicia verificação em background
        threading.Thread(target=self._check_server_status, daemon=True).start()

        # Área de chat scrollável (bolhas)
        self.chat_scroll = ctk.CTkScrollableFrame(self.chat_panel, fg_color="#0d0d0d", corner_radius=0)
        self.chat_scroll.pack(fill="both", expand=True)
        self.chat_scroll.columnconfigure(0, weight=1)

        # Preview de imagem
        self.img_frame = ctk.CTkFrame(self.chat_panel, height=58, fg_color="#151515", corner_radius=0)
        self.img_label = ctk.CTkLabel(self.img_frame, text="")
        self.img_label.pack(side="left", padx=10)
        self.img_name_lbl = ctk.CTkLabel(self.img_frame, text="", font=ctk.CTkFont(size=11), text_color="#aaa")
        self.img_name_lbl.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(self.img_frame, text="✕ Remover", width=90, height=26,
                      fg_color="#550000", hover_color="#880000", font=ctk.CTkFont(size=11),
                      command=self._remove_image).pack(side="right", padx=10)

        # Barra de input
        input_row = ctk.CTkFrame(self.chat_panel, fg_color="#111111", height=60, corner_radius=0)
        input_row.pack(fill="x")
        input_row.pack_propagate(False)

        self.img_btn = ctk.CTkButton(input_row, text="📷", width=44, height=44,
                                      fg_color="#1e1e1e", hover_color="#2a2a2a",
                                      font=ctk.CTkFont(size=18),
                                      command=self._pick_image)
        self.img_btn.pack(side="left", padx=(10, 6), pady=8)

        self.input_box = ctk.CTkEntry(input_row,
                                       placeholder_text="Digite sua mensagem...",
                                       height=44, font=ctk.CTkFont(size=13),
                                       fg_color="#1e1e1e", border_color="#333",
                                       corner_radius=22)
        self.input_box.pack(side="left", fill="x", expand=True, padx=(0, 6), pady=8)
        self.input_box.bind("<Return>", lambda e: self._send())

        self.send_btn = ctk.CTkButton(input_row, text="➤", width=44, height=44,
                                       fg_color="#cc2200", hover_color="#ff3300",
                                       font=ctk.CTkFont(size=18),
                                       corner_radius=22,
                                       command=self._send)
        self.send_btn.pack(side="left", padx=(0, 10), pady=8)

    # ── Painel de Bugs ────────────────────────────────────────────────────────
    def _check_server_status(self):
        """
        Verifica automaticamente qual servidor usar e atualiza o label no header.
        Roda em background ao iniciar. Tenta localhost → ngrok_url.txt.
        """
        import time
        while True:
            url = get_server_url(force_recheck=True)
            def _update(u=url):
                if not hasattr(self, 'srv_status_lbl'): return
                if u == "http://localhost:8080":
                    self.srv_status_lbl.configure(text="🟢 servidor local", text_color="#44ff88")
                elif u:
                    short = u.replace("https://","").replace("http://","")[:28]
                    self.srv_status_lbl.configure(text=f"🟢 ngrok: {short}", text_color="#44aaff")
                else:
                    self.srv_status_lbl.configure(text="🔴 servidor offline", text_color="#ff4444")
            try:
                self.after(0, _update)
            except Exception:
                break
            time.sleep(15)  # re-verifica a cada 15s

    def _build_bugs_panel(self):
        """Cria o painel de Respostas de Bug (oculto inicialmente)."""
        self.bugs_panel = ctk.CTkFrame(self.main, fg_color="transparent")

        # Header
        hdr = ctk.CTkFrame(self.bugs_panel, height=56, corner_radius=0, fg_color="#1a0000")
        hdr.pack(fill="x"); hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text="🐛  Respostas de Bug",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color="#ff8844").pack(side="left", padx=14, pady=8)
        ctk.CTkButton(hdr, text="← Chat", width=70, height=32,
                      fg_color="#2a0000", hover_color="#440000",
                      font=ctk.CTkFont(size=12),
                      command=self._show_chat_panel).pack(side="right", padx=10)

        # Lista de bugs
        ctk.CTkLabel(self.bugs_panel, text="Bugs reportados:",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color="#888").pack(anchor="w", padx=12, pady=(10, 4))

        self.bugs_list_frame = ctk.CTkScrollableFrame(self.bugs_panel, fg_color="#0d0d0d",
                                                       height=200, corner_radius=8)
        self.bugs_list_frame.pack(fill="x", padx=10, pady=(0, 8))

        # Área de resposta
        ctk.CTkLabel(self.bugs_panel, text="Resposta da equipe:",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color="#888").pack(anchor="w", padx=12, pady=(4, 4))

        self.bug_response_box = ctk.CTkTextbox(self.bugs_panel, height=140,
                                                fg_color="#0d0d0d", corner_radius=8,
                                                font=ctk.CTkFont(size=13),
                                                text_color="#e0e0e0", state="disabled")
        self.bug_response_box.pack(fill="both", expand=True, padx=10, pady=(0, 6))

        # Input para adicionar resposta manualmente
        ctk.CTkLabel(self.bugs_panel, text="Colar resposta do Discord:",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color="#888").pack(anchor="w", padx=12, pady=(4, 2))

        resp_row = ctk.CTkFrame(self.bugs_panel, fg_color="transparent")
        resp_row.pack(fill="x", padx=10, pady=(0, 10))

        self.resp_entry = ctk.CTkEntry(resp_row, placeholder_text="Cole aqui a resposta do Discord...",
                                        height=38, font=ctk.CTkFont(size=12))
        self.resp_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
        ctk.CTkButton(resp_row, text="✔ Salvar", width=80, height=38,
                      fg_color="#1a3a00", hover_color="#2a5a00",
                      font=ctk.CTkFont(size=12),
                      command=self._save_bug_response).pack(side="left")

    def _show_bugs_panel(self):
        self.chat_panel.pack_forget()
        if not hasattr(self, 'bugs_panel'):
            self._build_bugs_panel()
        self._refresh_bugs_list()
        self.bugs_panel.pack(fill="both", expand=True)

    def _show_chat_panel(self):
        if hasattr(self, 'bugs_panel'):
            self.bugs_panel.pack_forget()
        self.chat_panel.pack(fill="both", expand=True)

    def _refresh_bugs_list(self):
        for w in self.bugs_list_frame.winfo_children():
            w.destroy()
        self.bugs = load_bugs()
        if not self.bugs:
            ctk.CTkLabel(self.bugs_list_frame, text="Nenhum bug reportado ainda.",
                         font=ctk.CTkFont(size=12), text_color="#555").pack(pady=10)
            return
        for bug in reversed(self.bugs):
            has_resp = bool(bug.get("response"))
            color = "#1a3a00" if has_resp else "#2a0a00"
            icon  = "✅" if has_resp else "⏳"
            preview = bug['summary'][:55] + ("..." if len(bug['summary']) > 55 else "")
            btn = ctk.CTkButton(
                self.bugs_list_frame,
                text=f"{icon}  {bug['date']}  —  {preview}",
                anchor="w", height=36,
                fg_color=color,
                hover_color="#2a2a2a",
                font=ctk.CTkFont(size=11),
                command=lambda b=bug: self._select_bug(b)
            )
            btn.pack(fill="x", pady=2, padx=4)

    def _select_bug(self, bug):
        self._selected_bug_id = bug["id"]
        self.bug_response_box.configure(state="normal")
        self.bug_response_box.delete("1.0", "end")
        self.bug_response_box.insert("end", f"🐛 Bug: {bug['summary']}\n\n")
        if bug.get("response"):
            self.bug_response_box.insert("end", f"💬 Resposta:\n{bug['response']}")
        else:
            self.bug_response_box.insert("end", "⏳ Aguardando resposta da equipe...")
        self.bug_response_box.configure(state="disabled")

    def _save_bug_response(self):
        resp = self.resp_entry.get().strip()
        if not resp or not self._selected_bug_id:
            return
        bugs = load_bugs()
        for bug in bugs:
            if bug["id"] == self._selected_bug_id:
                bug["response"] = resp
                break
        save_bugs(bugs)
        self.resp_entry.delete(0, "end")
        self._refresh_bugs_list()
        # Mostra resposta atualizada
        for bug in bugs:
            if bug["id"] == self._selected_bug_id:
                self._select_bug(bug)
                break

    def _register_bug(self, summary):
        """Registra o bug localmente e envia ao Discord."""
        bug = {
            "id":       str(uuid.uuid4())[:8],
            "date":     datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
            "summary":  summary,
            "response": ""
        }
        bugs = load_bugs()
        bugs.append(bug)
        save_bugs(bugs)
        send_bug_to_discord(summary, bug["id"])
        # Atualiza badge do botão
        self.bugs_btn.configure(text=f"🐛  Respostas de Bug ({len(bugs)})")

    def _show_support_panel(self):
        self.chat_panel.pack_forget()
        if hasattr(self, 'bugs_panel'):
            self.bugs_panel.pack_forget()
        if not hasattr(self, 'support_panel'):
            self._build_support_panel()
        self._refresh_support_list()
        self.support_panel.pack(fill="both", expand=True)

    def _build_support_panel(self):
        self.support_panel = ctk.CTkFrame(self.main, fg_color="transparent")

        # Header fixo no topo
        hdr = ctk.CTkFrame(self.support_panel, height=52, corner_radius=0, fg_color="#001a2a")
        hdr.pack(fill="x", side="top")
        hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text="🎧  Suporte",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color="#44aaff").pack(side="left", padx=14)
        ctk.CTkButton(hdr, text="← Chat", width=70, height=32,
                      fg_color="#002244", hover_color="#003366",
                      font=ctk.CTkFont(size=12),
                      command=self._show_chat_from_support).pack(side="right", padx=10)

        # Todo conteúdo dentro de um ScrollableFrame para nunca sumir
        scroll = ctk.CTkScrollableFrame(self.support_panel, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=0, pady=0)

        # ── Nova mensagem ──────────────────────────────────────────────────
        ctk.CTkLabel(scroll, text="✉️  Nova mensagem de suporte:",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color="#44aaff").pack(anchor="w", padx=12, pady=(12, 4))

        name_row = ctk.CTkFrame(scroll, fg_color="transparent")
        name_row.pack(fill="x", padx=10, pady=(0, 4))
        ctk.CTkLabel(name_row, text="Seu nome:", font=ctk.CTkFont(size=11),
                     text_color="#aaa", width=80).pack(side="left")
        self.support_name = ctk.CTkEntry(name_row, placeholder_text="Ex: HeitorDanielS",
                                          height=36, font=ctk.CTkFont(size=12))
        self.support_name.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(scroll, text="Mensagem:", font=ctk.CTkFont(size=11),
                     text_color="#aaa").pack(anchor="w", padx=12)
        self.support_msg = ctk.CTkTextbox(scroll, height=70, fg_color="#111",
                                           corner_radius=8, font=ctk.CTkFont(size=12))
        self.support_msg.pack(fill="x", padx=10, pady=(2, 4))

        self.support_status = ctk.CTkLabel(scroll, text="",
                                            font=ctk.CTkFont(size=11), text_color="#888")
        self.support_status.pack(anchor="w", padx=12)

        ctk.CTkButton(scroll, text="📨  Enviar para Suporte",
                      height=40, fg_color="#003a7a", hover_color="#0055bb",
                      font=ctk.CTkFont(size=13, weight="bold"),
                      command=self._send_support).pack(fill="x", padx=10, pady=(4, 10))

        # ── Divisor ────────────────────────────────────────────────────────
        ctk.CTkFrame(scroll, height=1, fg_color="#333").pack(fill="x", padx=10, pady=4)
        ctk.CTkLabel(scroll, text="📋  Tickets enviados:",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color="#44aaff").pack(anchor="w", padx=12, pady=(6, 4))

        self.support_list_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        self.support_list_frame.pack(fill="x", padx=10, pady=(0, 8))

        # ── Divisor ────────────────────────────────────────────────────────
        ctk.CTkFrame(scroll, height=1, fg_color="#333").pack(fill="x", padx=10, pady=4)
        ctk.CTkLabel(scroll, text="💬  Resposta da equipe:",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color="#44aaff").pack(anchor="w", padx=12, pady=(6, 4))

        self.support_response_box = ctk.CTkTextbox(scroll, height=110,
                                                    fg_color="#0d0d0d", corner_radius=8,
                                                    font=ctk.CTkFont(size=13),
                                                    text_color="#e0e0e0", state="disabled")
        self.support_response_box.pack(fill="x", padx=10, pady=(0, 6))

        ctk.CTkLabel(scroll, text="Colar resposta do Discord:",
                     font=ctk.CTkFont(size=11), text_color="#888").pack(anchor="w", padx=12)
        resp_row = ctk.CTkFrame(scroll, fg_color="transparent")
        resp_row.pack(fill="x", padx=10, pady=(4, 16))
        self.support_resp_entry = ctk.CTkEntry(resp_row,
                                                placeholder_text="Cole a resposta aqui...",
                                                height=38, font=ctk.CTkFont(size=12))
        self.support_resp_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
        ctk.CTkButton(resp_row, text="✔ Salvar", width=90, height=38,
                      fg_color="#003300", hover_color="#005500",
                      font=ctk.CTkFont(size=12, weight="bold"),
                      command=self._save_support_response).pack(side="left")


    def _send_support(self):
        name = self.support_name.get().strip() or "Anônimo"
        msg  = self.support_msg.get("1.0", "end").strip()
        if not msg:
            self.support_status.configure(text="⚠️ Escreva uma mensagem antes de enviar.", text_color="#ff8800")
            return

        # Moderação
        impr, palavra = check_moderacao(msg)
        if impr:
            self.support_status.configure(
                text=f"❌ Mensagem bloqueada: conteúdo impróprio detectado.", text_color="#ff3300")
            return

        # Salva localmente
        ticket = {
            "id":       str(uuid.uuid4())[:8],
            "date":     datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
            "name":     name,
            "message":  msg,
            "response": ""
        }
        tickets = load_support()
        tickets.append(ticket)
        save_support(tickets)
        self._selected_ticket_id = ticket["id"]

        # Envia ao Discord
        send_support_to_discord(name, msg, ticket["id"])

        # Limpa campos
        self.support_msg.delete("1.0", "end")
        self.support_name.delete(0, "end")
        self.support_status.configure(text="✅ Mensagem enviada! Aguarde a resposta da equipe.", text_color="#00cc66")
        self.support_btn.configure(text=f"🎧  Suporte ({len(tickets)})")
        self._refresh_support_list()

    def _refresh_support_list(self):
        for w in self.support_list_frame.winfo_children():
            w.destroy()
        tickets = load_support()
        if not tickets:
            ctk.CTkLabel(self.support_list_frame, text="Nenhum ticket enviado ainda.",
                         font=ctk.CTkFont(size=12), text_color="#555").pack(pady=8)
            return
        for item in reversed(tickets):
            has_resp = bool(item.get("response"))
            icon  = "✅" if has_resp else "⏳"
            preview = item['message'][:45] + ("..." if len(item['message']) > 45 else "")

            row = ctk.CTkFrame(self.support_list_frame, fg_color="#111", corner_radius=8)
            row.pack(fill="x", pady=3, padx=2)

            # Botão principal (seleciona e mostra resposta)
            ctk.CTkButton(
                row,
                text=f"{icon}  {item['date']}  —  {preview}",
                anchor="w", height=36,
                fg_color="#001a33" if has_resp else "#1a0a00",
                hover_color="#223355" if has_resp else "#331500",
                font=ctk.CTkFont(size=11),
                command=lambda i=item: self._select_ticket(i)
            ).pack(side="left", fill="x", expand=True, padx=(4, 2), pady=4)

            # Botão ver mensagem inteira
            ctk.CTkButton(
                row,
                text="👁 Ver",
                width=60, height=36,
                fg_color="#1a1a2a",
                hover_color="#2a2a4a",
                font=ctk.CTkFont(size=11),
                command=lambda i=item: self._view_full_ticket(i)
            ).pack(side="right", padx=(2, 4), pady=4)

    def _select_ticket(self, ticket):
        self._selected_ticket_id = ticket["id"]
        self.support_response_box.configure(state="normal")
        self.support_response_box.delete("1.0", "end")
        self.support_response_box.insert("end", f"👤 {ticket['name']}: {ticket['message']}\n\n")
        if ticket.get("response"):
            self.support_response_box.insert("end", f"💬 Resposta:\n{ticket['response']}")
        else:
            self.support_response_box.insert("end", "⏳ Aguardando resposta da equipe...")
        self.support_response_box.configure(state="disabled")

    def _view_full_ticket(self, ticket):
        """Abre janela popup com a mensagem completa do ticket."""
        popup = ctk.CTkToplevel(self)
        popup.title(f"Ticket {ticket['id']} — Mensagem completa")
        popup.geometry("520x360")
        popup.configure(fg_color="#0d0d0d")
        popup.grab_set()

        ctk.CTkLabel(popup, text=f"👤 {ticket['name']}  •  {ticket['date']}",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color="#44aaff").pack(anchor="w", padx=16, pady=(14, 4))

        ctk.CTkLabel(popup, text="Mensagem:",
                     font=ctk.CTkFont(size=11), text_color="#888").pack(anchor="w", padx=16)
        msg_box = ctk.CTkTextbox(popup, height=140, fg_color="#111",
                                  corner_radius=8, font=ctk.CTkFont(size=13),
                                  text_color="#e8e8e8")
        msg_box.pack(fill="x", padx=16, pady=(4, 10))
        msg_box.insert("end", ticket['message'])
        msg_box.configure(state="disabled")

        if ticket.get("response"):
            ctk.CTkLabel(popup, text="💬 Resposta da equipe:",
                         font=ctk.CTkFont(size=11), text_color="#888").pack(anchor="w", padx=16)
            resp_box = ctk.CTkTextbox(popup, height=100, fg_color="#111",
                                      corner_radius=8, font=ctk.CTkFont(size=13),
                                      text_color="#00cc66")
            resp_box.pack(fill="x", padx=16, pady=(4, 10))
            resp_box.insert("end", ticket['response'])
            resp_box.configure(state="disabled")
        else:
            ctk.CTkLabel(popup, text="⏳ Aguardando resposta da equipe...",
                         font=ctk.CTkFont(size=12), text_color="#888").pack(pady=8)

        ctk.CTkButton(popup, text="Fechar", height=36,
                      fg_color="#2a0000", hover_color="#440000",
                      command=popup.destroy).pack(pady=(4, 14))

    def _save_support_response(self):
        resp = self.support_resp_entry.get().strip()
        if not resp or not hasattr(self, '_selected_ticket_id'): return
        tickets = load_support()
        for t in tickets:
            if t["id"] == self._selected_ticket_id:
                t["response"] = resp
                break
        save_support(tickets)
        self.support_resp_entry.delete(0, "end")
        self._refresh_support_list()
        for t in tickets:
            if t["id"] == self._selected_ticket_id:
                self._select_ticket(t)
                break

    def _show_chat_from_support(self):
        self.support_panel.pack_forget()
        self.chat_panel.pack(fill="both", expand=True)

    # ── Bolhas de chat ────────────────────────────────────────────────────────
    def _add_bubble(self, role, text, return_ref=False):
        """Adiciona uma bolha de mensagem estilo WhatsApp."""
        row = ctk.CTkFrame(self.chat_scroll, fg_color="transparent")
        row.pack(fill="x", padx=10, pady=3)

        if role == "user":
            bubble = ctk.CTkFrame(row, fg_color="#1a3a0a", corner_radius=16)
            bubble.pack(side="right", anchor="e", padx=(60, 0))
            name_color = "#88ff44"
            name = "Você"
        elif role == "ai":
            bubble = ctk.CTkFrame(row, fg_color="#2a0000", corner_radius=16)
            bubble.pack(side="left", anchor="w", padx=(0, 60))
            name_color = "#ff4422"
            name = "FloppaAI 🐱"
        else:
            bubble = ctk.CTkFrame(row, fg_color="#1a1a1a", corner_radius=10)
            bubble.pack(anchor="center")
            name_color = "#888"
            name = "ℹ Sistema"

        ctk.CTkLabel(bubble, text=name,
                     font=ctk.CTkFont(size=10, weight="bold"),
                     text_color=name_color).pack(anchor="w", padx=12, pady=(8, 0))

        self._render_markdown(bubble, text)

        # Scroll até o fim
        self.after(50, lambda: self.chat_scroll._parent_canvas.yview_moveto(1.0))

        if return_ref:
            return row
        return None

    def _render_markdown(self, parent, text):
        """Renderiza texto com **negrito** e *itálico* usando tk.Text."""
        import tkinter as tk
        import re
        # Pega a cor de fundo do bubble pai para simular transparência
        try:
            bg_color = parent.cget("fg_color")
            if isinstance(bg_color, (list, tuple)):
                bg_color = bg_color[1]  # modo escuro
        except Exception:
            bg_color = "#2a0000"

        txt = tk.Text(parent, wrap="word", bg=bg_color,
                      bd=0, highlightthickness=0,
                      relief="flat", cursor="arrow",
                      font=("Segoe UI", 12),
                      fg="#e8e8e8", state="normal",
                      width=48, height=1)
        txt.tag_configure("bold",   font=("Segoe UI", 12, "bold"),   foreground="#ffffff")
        txt.tag_configure("italic", font=("Segoe UI", 12, "italic"),  foreground="#dddddd")
        txt.tag_configure("normal", font=("Segoe UI", 12),            foreground="#e8e8e8")

        # Parse simples: **bold**, *italic*, resto normal
        pattern = re.compile(r'(\*\*(.+?)\*\*|\*(.+?)\*)', re.DOTALL)
        last = 0
        for m in pattern.finditer(text):
            if m.start() > last:
                txt.insert("end", text[last:m.start()], "normal")
            if m.group(0).startswith("**"):
                txt.insert("end", m.group(2), "bold")
            else:
                txt.insert("end", m.group(3), "italic")
            last = m.end()
        if last < len(text):
            txt.insert("end", text[last:], "normal")

        txt.configure(state="disabled")
        # Ajusta altura dinamicamente
        lines = text.count("\n") + 1
        approx = max(1, int(len(text) / 46) + lines)
        txt.configure(height=approx)
        txt.pack(padx=12, pady=(2, 10), anchor="w", fill="x")

    def _remove_bubble(self, ref):
        """Remove uma bolha pelo frame de referência."""
        if ref:
            ref.destroy()

    # ── Limpar chat ───────────────────────────────────────────────────────────
    def _clear_chat(self):
        self.history = []
        for widget in self.chat_scroll.winfo_children():
            widget.destroy()
        self._add_bubble("system", "Chat limpo! Como posso ajudar?")

    # ── Imagem ────────────────────────────────────────────────────────────────
    def _pick_image(self):
        messagebox.showinfo("Imagens", "O envio de imagens não está disponível no momento.\nUse o chat de texto para descrever o que está vendo no jogo! 🐱")

    def _remove_image(self):
        self.pending_image    = None
        self.pending_img_path = None
        self.img_frame.pack_forget()

    # ── Enviar mensagem ───────────────────────────────────────────────────────
    def _send(self):
        text = self.input_box.get().strip()
        if not text: return
        self.input_box.delete(0, "end")
        self.send_btn.configure(state="disabled", text="⏳")

        display = text
        if self.pending_img_path:
            display += f"\n📷 {os.path.basename(self.pending_img_path)}"
        self._add_bubble("user", display)
        self.history.append({"role": "user", "content": text})

        self._remove_image()

        # Bolha de "digitando..."
        self._thinking_bubble = self._add_bubble("ai", "⏳ Digitando...", return_ref=True)

        def done(reply):
            # Detecta bug report automático da IA
            if reply.startswith("🐛BUG_REPORT:"):
                lines = reply.split("\n", 1)
                summary = lines[0].replace("🐛BUG_REPORT:", "").strip()
                clean_reply = lines[1].strip() if len(lines) > 1 else reply
                self.after(0, lambda: self._register_bug(summary))
                self.history.append({"role": "assistant", "content": clean_reply})
                self.after(0, lambda: self._replace_thinking(clean_reply))
            else:
                self.history.append({"role": "assistant", "content": reply})
                self.after(0, lambda: self._replace_thinking(reply))

        def err(e):
            self.after(0, lambda: self._replace_thinking(f"⚠️ Erro: {e}"))

        ask_groq(list(self.history), on_done=done, on_error=err)

    def _replace_thinking(self, text):
        """Remove a bolha de 'digitando' e adiciona a resposta real."""
        self._remove_bubble(self._thinking_bubble)
        self._thinking_bubble = None
        self._add_bubble("ai", text)
        self.send_btn.configure(state="normal", text="➤")

    def _quick_action(self, prompt):
        self.input_box.delete(0, "end")
        self.input_box.insert(0, prompt)
        self._send()

    # ── Atualização ───────────────────────────────────────────────────────────
    def _on_update_check(self, has_update, version, notes):
        if has_update:
            self.update_btn.configure(text=f"🆕 Update v{version}",
                                       state="normal", fg_color="#3a2a00",
                                       hover_color="#5a4400")
            self._update_info = (version, notes)

    def _show_update(self):
        v, notes = getattr(self, "_update_info", ("?", ""))
        messagebox.showinfo("Atualização disponível",
                            f"Nova versão: {v}\n\n{notes}\n\nBaixe no site do jogo.")

    def _toggle_startup(self):
        if self.startup_var.get():
            add_to_startup()
        else:
            remove_from_startup()

# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = FloppaAI()
    app.mainloop()
