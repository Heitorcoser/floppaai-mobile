# ═══════════════════════════════════════════════════════════════════════════
#   FloppaAI — Modo Desenvolvedor  🛠
#   ⚠️  ACESSO RESTRITO — Senha: Heitor@cris
#   Usa Supabase como banco online. Logs/config ficam locais.
# ═══════════════════════════════════════════════════════════════════════════
import customtkinter as ctk
from tkinter import messagebox
import json, os, datetime, uuid, threading, time, subprocess, sys, hashlib, requests

# ── Supabase (hardcoded) ──────────────────────────────────────────────────
SB_URL = "https://klcdgksyddlyfazowheb.supabase.co"
SB_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtsY2Rna3N5ZGRseWZhem93aGViIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM2MzAwMTAsImV4cCI6MjA4OTIwNjAxMH0.pYqDAbpYWvnr0sf2pQJ5BBx1dAU9HUX2Amd69RWvSSg"
SB_HDR = {
    "apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json", "Prefer": "return=representation"
}

def sb_get(table, params=""):
    try:
        r = requests.get(f"{SB_URL}/rest/v1/{table}{params}", headers=SB_HDR, timeout=8)
        return r.json() if r.ok else []
    except: return []

def sb_post(table, data):
    try:
        r = requests.post(f"{SB_URL}/rest/v1/{table}", headers=SB_HDR, json=data, timeout=8)
        return r.ok
    except: return False

def sb_patch(table, row_id, data):
    try:
        r = requests.patch(f"{SB_URL}/rest/v1/{table}?id=eq.{row_id}", headers=SB_HDR, json=data, timeout=8)
        return r.ok
    except: return False

def sb_delete(table, row_id):
    try:
        r = requests.delete(f"{SB_URL}/rest/v1/{table}?id=eq.{row_id}", headers=SB_HDR, timeout=8)
        return r.ok
    except: return False


# ── Caminhos locais (config, logs, spam — não precisam de nuvem) ──────────
BASE_DIR          = os.path.dirname(os.path.abspath(__file__))
SPAM_FILE         = os.path.join(BASE_DIR, "spam_log.json")
DEV_CONFIG_FILE   = os.path.join(BASE_DIR, "dev_config.json")
VERSION_FILE      = os.path.join(BASE_DIR, "version.json")
ACTIVITY_LOG_FILE = os.path.join(BASE_DIR, "activity_log.json")

# ── Senha SHA-256 — padrão: Heitor@cris ──────────────────────────────────
DEFAULT_PWD_HASH = "0f5fdb20028e7514a755f4c2648b7fc26a888b8fed25edfafb3fc1287ac420e6"

def _hash_pwd(s): return hashlib.sha256(s.strip().encode()).hexdigest()

def _load(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f: return json.load(f)
    except: return default

def _save(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=2)
    except: pass

# ── Helpers Supabase ──────────────────────────────────────────────────────
def load_support():        return sb_get("tickets", "?select=*&order=date.desc") or []
def load_bugs():           return sb_get("bugs",    "?select=*&order=date.desc") or []
def load_announcements():  return sb_get("announcements", "?select=*&order=date.desc") or []

def save_announcements(lst):
    pass  # usa sb_post/sb_delete individualmente

def delete_ticket(tid):    return sb_delete("tickets", tid)
def delete_bug(bid):       return sb_delete("bugs", bid)
def delete_ann(aid):       return sb_delete("announcements", aid)
def reply_ticket(tid, r):  return sb_patch("tickets", tid, {"response": r})
def reply_bug(bid, r, st): return sb_patch("bugs",    bid, {"response": r, "status": st})
def post_ann(data):        return sb_post("announcements", data)

# ── Locais (spam, config, versão, logs) ───────────────────────────────────
def load_spam():           return _load(SPAM_FILE, {"blocked": [], "log": []})
def save_spam(d):          _save(SPAM_FILE, d)
def load_version():        return _load(VERSION_FILE, {"version":"1.0.0","build":1,"notes":"","download_pc":"","download_apk":""})
def save_version(d):       _save(VERSION_FILE, d)
def load_activity():       return _load(ACTIVITY_LOG_FILE, [])
def save_activity(d):      _save(ACTIVITY_LOG_FILE, d)

def load_dev_config():
    default = {"password_hash": DEFAULT_PWD_HASH, "spam_limit": 3,
               "spam_window_min": 10, "min_msg_len": 3, "auto_block_after": 5}
    data = _load(DEV_CONFIG_FILE, default)
    if "password" in data and "password_hash" not in data:
        data["password_hash"] = _hash_pwd(data.pop("password")); _save(DEV_CONFIG_FILE, data)
    for k, v in default.items(): data.setdefault(k, v)
    return data

def save_dev_config(d):    _save(DEV_CONFIG_FILE, d)

def log_activity(action, detail=""):
    logs = load_activity()
    logs.append({"time": datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                 "action": action, "detail": detail})
    if len(logs) > 200: logs = logs[-200:]
    save_activity(logs)

def now_str(): return datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

def get_stats():
    tickets = load_support(); bugs = load_bugs(); spam = load_spam()
    t_total = len(tickets); t_pend = sum(1 for t in tickets if not t.get("response"))
    b_total = len(bugs);    b_pend = sum(1 for b in bugs if not b.get("response"))
    today   = datetime.datetime.now().strftime("%d/%m/%Y")
    names   = set(t.get("name","?").lower() for t in tickets)
    return {
        "tickets_total": t_total, "tickets_pendentes": t_pend,
        "tickets_resp": t_total - t_pend,
        "tickets_hoje": sum(1 for t in tickets if t.get("date","").startswith(today)),
        "bugs_total": b_total, "bugs_pendentes": b_pend, "bugs_resp": b_total - b_pend,
        "usuarios": len(names),
        "spam_bloqueados": len(spam.get("blocked",[])),
        "spam_tentativas": len(spam.get("log",[])),
    }


# ═══════════════════════════════════════════════════════════════════════════
class DevMode(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("FloppaAI — Modo Desenvolvedor 🛠")
        self.geometry("1260x800"); self.minsize(1000, 650)
        ctk.set_appearance_mode("dark"); ctk.set_default_color_theme("dark-blue")
        self._sel_ticket_id = None; self._sel_bug_id = None
        self._active_panel = None; self._auto_refresh = True
        self._build_login()

    # ── LOGIN ────────────────────────────────────────────────────────────
    def _build_login(self):
        self.login_frame = ctk.CTkFrame(self, fg_color="#050505")
        self.login_frame.pack(fill="both", expand=True)
        center = ctk.CTkFrame(self.login_frame, fg_color="#111", corner_radius=20, width=430, height=400)
        center.place(relx=0.5, rely=0.5, anchor="center"); center.pack_propagate(False)
        ctk.CTkLabel(center, text="🛠", font=ctk.CTkFont(size=52)).pack(pady=(36,4))
        ctk.CTkLabel(center, text="FloppaAI — Modo Desenvolvedor",
                     font=ctk.CTkFont(size=17, weight="bold"), text_color="#ff8844").pack()
        ctk.CTkLabel(center, text="⚠️  Acesso restrito à equipe",
                     font=ctk.CTkFont(size=11), text_color="#555").pack(pady=(2,18))
        self.pwd_entry = ctk.CTkEntry(center, placeholder_text="🔑 Senha de desenvolvedor",
                                      show="●", height=46, width=300, font=ctk.CTkFont(size=13),
                                      fg_color="#1a1a1a", border_color="#333", corner_radius=12)
        self.pwd_entry.pack(pady=(0,8))
        self.pwd_entry.bind("<Return>", lambda e: self._verify_pwd())
        ctk.CTkButton(center, text="🔓  Entrar", height=46, width=300,
                      fg_color="#cc2200", hover_color="#ff3300",
                      font=ctk.CTkFont(size=13, weight="bold"), corner_radius=12,
                      command=self._verify_pwd).pack(pady=4)
        self.login_err = ctk.CTkLabel(center, text="", font=ctk.CTkFont(size=11), text_color="#ff4444")
        self.login_err.pack(pady=6)
        ctk.CTkButton(center, text="↗ Abrir FloppaAI Normal", height=32, width=220,
                      fg_color="transparent", hover_color="#1a1a1a", text_color="#666",
                      font=ctk.CTkFont(size=11), command=self._open_main_app).pack(pady=(4,16))

    def _verify_pwd(self):
        hash_dig = _hash_pwd(self.pwd_entry.get())
        hash_ok  = load_dev_config().get("password_hash", DEFAULT_PWD_HASH)
        if hash_dig == hash_ok:
            self.login_frame.destroy()
            log_activity("LOGIN", "Desenvolvedor autenticado")
            self._build_main()
        else:
            self.login_err.configure(text="❌ Senha incorreta!")
            self.pwd_entry.delete(0, "end")

    def _open_main_app(self):
        app = os.path.join(BASE_DIR, "app.py")
        if os.path.exists(app): subprocess.Popen([sys.executable, app])


    # ── LAYOUT PRINCIPAL ─────────────────────────────────────────────────
    def _build_main(self):
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True)
        self._build_sidebar()
        self.content = ctk.CTkFrame(self.main_frame, fg_color="#0a0a0a", corner_radius=0)
        self.content.pack(side="right", fill="both", expand=True)
        self._navigate("dashboard")
        self._start_auto_refresh()

    # ── SIDEBAR ──────────────────────────────────────────────────────────
    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self.main_frame, width=230, fg_color="#0d0d0d", corner_radius=0)
        self.sidebar.pack(side="left", fill="y"); self.sidebar.pack_propagate(False)
        ctk.CTkLabel(self.sidebar, text="🛠 Dev Mode",
                     font=ctk.CTkFont(size=20, weight="bold"), text_color="#ff6633").pack(pady=(22,2))
        ctk.CTkLabel(self.sidebar, text="FloppaAI — Painel Interno",
                     font=ctk.CTkFont(size=10), text_color="#444").pack()
        ctk.CTkFrame(self.sidebar, height=1, fg_color="#222").pack(fill="x", padx=10, pady=14)
        self._nav_btns = {}
        for key, label in [
            ("dashboard",    "📊  Dashboard"),
            ("inbox",        "📨  Inbox de Tickets"),
            ("bugs",         "🐛  Bug Reports"),
            ("usuarios",     "👥  Usuários"),
            ("spam",         "🛡  Anti-Spam"),
            ("announcements","📢  Anúncios"),
            ("version",      "🔖  Versão"),
            ("logs",         "📋  Logs"),
            ("config",       "⚙️  Configurações"),
        ]:
            btn = ctk.CTkButton(self.sidebar, text=label, height=38, anchor="w",
                                font=ctk.CTkFont(size=12), fg_color="transparent",
                                hover_color="#1a0a00", text_color="#bbbbbb", corner_radius=8,
                                command=lambda k=key: self._navigate(k))
            btn.pack(fill="x", padx=8, pady=2); self._nav_btns[key] = btn
        ctk.CTkFrame(self.sidebar, height=1, fg_color="#222").pack(fill="x", padx=10, pady=10)
        self.badge_t = ctk.CTkLabel(self.sidebar, text="", font=ctk.CTkFont(size=10), text_color="#44aaff")
        self.badge_t.pack(anchor="w", padx=16)
        self.badge_b = ctk.CTkLabel(self.sidebar, text="", font=ctk.CTkFont(size=10), text_color="#ff8844")
        self.badge_b.pack(anchor="w", padx=16)
        ctk.CTkFrame(self.sidebar, height=1, fg_color="#222").pack(fill="x", padx=10, pady=8)
        self.ref_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(self.sidebar, text="Auto-refresh (10s)", variable=self.ref_var,
                        font=ctk.CTkFont(size=11), text_color="#666",
                        command=lambda: setattr(self,"_auto_refresh",self.ref_var.get())
                        ).pack(padx=12, pady=2)
        ctk.CTkButton(self.sidebar, text="🔄 Atualizar Agora", height=30,
                      fg_color="#1a1a1a", hover_color="#2a2a2a", font=ctk.CTkFont(size=11),
                      text_color="#888",
                      command=lambda: self._navigate(self._active_panel)).pack(fill="x",padx=8,pady=2)
        ctk.CTkButton(self.sidebar, text="↗ Abrir App", height=30,
                      fg_color="#0a1a0a", hover_color="#1a2a1a", font=ctk.CTkFont(size=11),
                      text_color="#888", command=self._open_main_app).pack(fill="x",padx=8,pady=2)
        ctk.CTkButton(self.sidebar, text="🚪 Logout", height=30,
                      fg_color="#1a0000", hover_color="#2a0000", font=ctk.CTkFont(size=11),
                      text_color="#ff4444", command=self.destroy).pack(fill="x",padx=8,pady=(2,16))
        self._update_badges()

    def _update_badges(self):
        s = get_stats()
        self.badge_t.configure(text=f"  📨 {s['tickets_pendentes']} pendentes")
        self.badge_b.configure(text=f"  🐛 {s['bugs_pendentes']} bugs pendentes")
        if "inbox" in self._nav_btns:
            self._nav_btns["inbox"].configure(fg_color="#001a33" if s["tickets_pendentes"]>0 else "transparent")
        if "bugs" in self._nav_btns:
            self._nav_btns["bugs"].configure(fg_color="#1a0800" if s["bugs_pendentes"]>0 else "transparent")

    def _navigate(self, key):
        for w in self.content.winfo_children(): w.destroy()
        self._active_panel = key
        for k, btn in self._nav_btns.items():
            btn.configure(text_color="#ffffff" if k==key else "#bbbbbb",
                          fg_color="#2a1000" if k==key else "transparent")
        panels = {
            "dashboard":     self._build_dashboard,
            "inbox":         self._build_inbox,
            "bugs":          self._build_bugs_panel,
            "usuarios":      self._build_users,
            "spam":          self._build_spam,
            "announcements": self._build_announcements,
            "version":       self._build_version,
            "logs":          self._build_logs,
            "config":        self._build_config,
        }
        if key in panels: panels[key]()
        self._update_badges()

    def _panel_header(self, title):
        hdr = ctk.CTkFrame(self.content, height=56, corner_radius=0, fg_color="#111")
        hdr.pack(fill="x"); hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text=title, font=ctk.CTkFont(size=15, weight="bold"),
                     text_color="#ff8844").pack(side="left", padx=18, pady=10)
        ctk.CTkLabel(hdr, text=f"🕐 {now_str()} | ☁️ Supabase",
                     font=ctk.CTkFont(size=10), text_color="#444").pack(side="right", padx=14)

    def _start_auto_refresh(self):
        def _loop():
            while True:
                time.sleep(10)
                if self._auto_refresh and self._active_panel:
                    try: self.after(0, self._update_badges)
                    except: break
        threading.Thread(target=_loop, daemon=True).start()


    # ── DASHBOARD ────────────────────────────────────────────────────────
    def _build_dashboard(self):
        s = get_stats(); self._panel_header("📊  Dashboard — Visão Geral")
        body = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=16, pady=8)
        def card_row(cards):
            frame = ctk.CTkFrame(body, fg_color="transparent"); frame.pack(fill="x", pady=6)
            for title, value, bg, fg in cards:
                col = ctk.CTkFrame(frame, fg_color=bg, corner_radius=14, height=96)
                col.pack(side="left", fill="x", expand=True, padx=5); col.pack_propagate(False)
                ctk.CTkLabel(col, text=value, font=ctk.CTkFont(size=34,weight="bold"), text_color=fg).pack(pady=(12,0))
                ctk.CTkLabel(col, text=title, font=ctk.CTkFont(size=10), text_color="#888").pack()
        card_row([
            ("📨 Tickets Totais",  str(s["tickets_total"]),    "#003a5a","#44aaff"),
            ("⏳ Pendentes",       str(s["tickets_pendentes"]), "#3a1a00","#ffaa44"),
            ("✅ Respondidos",     str(s["tickets_resp"]),      "#003a00","#44ff88"),
            ("📅 Hoje",           str(s["tickets_hoje"]),      "#1a1a3a","#aa88ff"),
        ])
        card_row([
            ("🐛 Bugs Totais",    str(s["bugs_total"]),        "#2a0800","#ff8844"),
            ("🐛 Pendentes",      str(s["bugs_pendentes"]),    "#3a0000","#ff4444"),
            ("✅ Corrigidos",     str(s["bugs_resp"]),         "#003300","#44ff44"),
            ("👥 Usuários",       str(s["usuarios"]),          "#1a0a2a","#cc88ff"),
        ])
        ctk.CTkLabel(body, text="📋  Atividade Recente",
                     font=ctk.CTkFont(size=13,weight="bold"), text_color="#888").pack(anchor="w",pady=(18,6))
        for entry in list(reversed(load_activity()[-15:])):
            row = ctk.CTkFrame(body, fg_color="#111", corner_radius=8); row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=f"[{entry['time']}]", font=ctk.CTkFont(size=10),
                         text_color="#555", width=135).pack(side="left", padx=8)
            ctk.CTkLabel(row, text=entry["action"], font=ctk.CTkFont(size=10,weight="bold"),
                         text_color="#ff8844", width=180).pack(side="left")
            ctk.CTkLabel(row, text=entry.get("detail","")[:70],
                         font=ctk.CTkFont(size=10), text_color="#aaa").pack(side="left",padx=4)

    # ── INBOX ────────────────────────────────────────────────────────────
    def _build_inbox(self):
        self._panel_header("📨  Inbox — Tickets de Suporte")
        tickets = load_support()
        pane = ctk.CTkFrame(self.content, fg_color="transparent"); pane.pack(fill="both", expand=True)
        left = ctk.CTkFrame(pane, fg_color="#0d0d0d", width=380, corner_radius=0)
        left.pack(side="left", fill="y"); left.pack_propagate(False)
        ctk.CTkLabel(left, text=f"{len(tickets)} tickets", font=ctk.CTkFont(size=10),
                     text_color="#555").pack(anchor="w", padx=12, pady=8)
        tlist = ctk.CTkScrollableFrame(left, fg_color="transparent"); tlist.pack(fill="both", expand=True)
        self._render_ticket_list(tlist, tickets)
        right = ctk.CTkFrame(pane, fg_color="#0a0a0a", corner_radius=0)
        right.pack(side="right", fill="both", expand=True)
        self._inbox_detail = right
        ctk.CTkLabel(right, text="← Selecione um ticket",
                     font=ctk.CTkFont(size=13), text_color="#333").pack(expand=True)

    def _render_ticket_list(self, container, tickets):
        for w in container.winfo_children(): w.destroy()
        for t in tickets:
            has_r = bool(t.get("response"))
            row = ctk.CTkFrame(container, fg_color="#001422" if has_r else "#1a0500", corner_radius=10)
            row.pack(fill="x", padx=8, pady=3)
            ctk.CTkLabel(row, text=f"{'✅' if has_r else '⏳'} {t.get('name','?')[:14]}",
                         font=ctk.CTkFont(size=11,weight="bold"),
                         text_color="#44aaff" if has_r else "#ffaa44").pack(anchor="w",padx=10,pady=(8,1))
            ctk.CTkLabel(row, text=(t.get("message","")[:42]+"..."),
                         font=ctk.CTkFont(size=10), text_color="#888").pack(anchor="w",padx=10)
            ctk.CTkLabel(row, text=t.get("date",""), font=ctk.CTkFont(size=9),
                         text_color="#444").pack(anchor="e",padx=10,pady=(0,6))
            for w in [row]+list(row.winfo_children()):
                w.bind("<Button-1>", lambda e, tk=t: self._open_ticket(tk))

    def _open_ticket(self, ticket):
        d = self._inbox_detail
        for w in d.winfo_children(): w.destroy()
        hdr = ctk.CTkFrame(d, fg_color="#001a2a", height=60, corner_radius=0)
        hdr.pack(fill="x"); hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text=f"👤 {ticket.get('name','?')}  •  #{ticket.get('id','')}  •  {ticket.get('date','')}",
                     font=ctk.CTkFont(size=12), text_color="#44aaff").pack(side="left",padx=14,pady=10)
        acts = ctk.CTkFrame(hdr, fg_color="transparent"); acts.pack(side="right",padx=10)
        ctk.CTkButton(acts, text="🗑 Deletar", width=80, height=30,
                      fg_color="#2a0000", hover_color="#440000", font=ctk.CTkFont(size=10),
                      command=lambda: self._del_ticket(ticket["id"])).pack(side="left",padx=3)
        body = ctk.CTkScrollableFrame(d, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=16, pady=10)
        ctk.CTkLabel(body, text="📩  Mensagem:", font=ctk.CTkFont(size=11,weight="bold"),
                     text_color="#888").pack(anchor="w")
        mb = ctk.CTkTextbox(body, height=110, fg_color="#111", corner_radius=8, font=ctk.CTkFont(size=12))
        mb.pack(fill="x", pady=(4,12)); mb.insert("end",ticket.get("message","")); mb.configure(state="disabled")
        if ticket.get("response"):
            ctk.CTkLabel(body, text="💬  Resposta enviada:", font=ctk.CTkFont(size=11,weight="bold"),
                         text_color="#44ff88").pack(anchor="w")
            rb = ctk.CTkTextbox(body, height=70, fg_color="#0a1a0a", corner_radius=8, font=ctk.CTkFont(size=12))
            rb.pack(fill="x", pady=(4,12)); rb.insert("end",ticket["response"]); rb.configure(state="disabled")
        ctk.CTkLabel(body, text="✍️  Sua resposta:", font=ctk.CTkFont(size=11,weight="bold"),
                     text_color="#888").pack(anchor="w")
        resp_e = ctk.CTkTextbox(body, height=90, fg_color="#111", corner_radius=8, font=ctk.CTkFont(size=12))
        if ticket.get("response"): resp_e.insert("end",ticket["response"])
        resp_e.pack(fill="x", pady=(4,6))
        tbar = ctk.CTkFrame(body, fg_color="transparent"); tbar.pack(fill="x", pady=(2,10))
        for lbl, txt in [("✅ Recebido","Olá! Recebemos sua mensagem e responderemos em breve!"),
                         ("🔧 Em análise","Mensagem encaminhada para a equipe técnica. Aguarde!"),
                         ("✔ Resolvido","Problema resolvido! Se precisar de mais ajuda, envie outra mensagem."),
                         ("❓ Mais info","Pode detalhar melhor o problema para que possamos ajudar?")]:
            ctk.CTkButton(tbar, text=lbl, height=28, width=105,
                          fg_color="#1a1a2a", hover_color="#2a2a3a", font=ctk.CTkFont(size=10),
                          command=lambda t=txt,e=resp_e: (e.delete("1.0","end"),e.insert("end",t))
                          ).pack(side="left", padx=3)
        def _send():
            resp = resp_e.get("1.0","end").strip()
            if not resp: return
            if reply_ticket(ticket["id"], resp):
                log_activity("RESPOSTA TICKET", f"#{ticket['id']} {ticket.get('name','?')}")
                messagebox.showinfo("✅","Resposta salva no Supabase!")
                self._navigate("inbox")
            else:
                messagebox.showerror("Erro","Falha ao salvar no Supabase.")
        ctk.CTkButton(body, text="📨  Salvar Resposta", height=44,
                      fg_color="#003a7a", hover_color="#0055bb",
                      font=ctk.CTkFont(size=13,weight="bold"), command=_send).pack(fill="x",pady=6)

    def _del_ticket(self, tid):
        if messagebox.askyesno("Deletar?",f"Deletar ticket #{tid}?"):
            delete_ticket(tid); log_activity("DELETOU TICKET",f"#{tid}"); self._navigate("inbox")


    # ── BUGS ─────────────────────────────────────────────────────────────
    def _build_bugs_panel(self):
        self._panel_header("🐛  Bug Reports")
        bugs = load_bugs()
        pane = ctk.CTkFrame(self.content, fg_color="transparent"); pane.pack(fill="both",expand=True)
        left = ctk.CTkFrame(pane, fg_color="#0d0d0d", width=380, corner_radius=0)
        left.pack(side="left", fill="y"); left.pack_propagate(False)
        ctk.CTkLabel(left, text=f"{len(bugs)} bugs", font=ctk.CTkFont(size=10),
                     text_color="#555").pack(anchor="w",padx=12,pady=8)
        blist = ctk.CTkScrollableFrame(left, fg_color="transparent"); blist.pack(fill="both",expand=True)
        detail = ctk.CTkFrame(pane, fg_color="#0a0a0a", corner_radius=0)
        detail.pack(side="right",fill="both",expand=True)
        ctk.CTkLabel(detail, text="← Selecione um bug",
                     font=ctk.CTkFont(size=13), text_color="#333").pack(expand=True)
        if not bugs:
            ctk.CTkLabel(blist, text="Nenhum bug.", font=ctk.CTkFont(size=11), text_color="#444").pack(pady=20)
        for bug in bugs:
            has_r = bool(bug.get("response"))
            row = ctk.CTkFrame(blist, fg_color="#001a00" if has_r else "#1a0800", corner_radius=10)
            row.pack(fill="x", padx=8, pady=3)
            ctk.CTkLabel(row, text=f"{'✅' if has_r else '⏳'} #{bug.get('id','')}",
                         font=ctk.CTkFont(size=10,weight="bold"),
                         text_color="#88ff44" if has_r else "#ff8844").pack(anchor="w",padx=10,pady=(8,1))
            ctk.CTkLabel(row, text=bug.get("summary","")[:44],
                         font=ctk.CTkFont(size=10), text_color="#888").pack(anchor="w",padx=10)
            ctk.CTkLabel(row, text=bug.get("date",""), font=ctk.CTkFont(size=9),
                         text_color="#444").pack(anchor="e",padx=10,pady=(0,6))
            for w in [row]+list(row.winfo_children()):
                w.bind("<Button-1>", lambda e, b=bug, d=detail: self._open_bug(b,d))

    def _open_bug(self, bug, detail):
        for w in detail.winfo_children(): w.destroy()
        hdr = ctk.CTkFrame(detail, fg_color="#1a0800", height=56, corner_radius=0)
        hdr.pack(fill="x"); hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text=f"🐛 #{bug.get('id','')} • {bug.get('date','')} • {bug.get('platform','?')}",
                     font=ctk.CTkFont(size=12), text_color="#ff8844").pack(side="left",padx=14)
        ctk.CTkButton(hdr, text="🗑", width=50, height=30,
                      fg_color="#2a0000", hover_color="#440000", font=ctk.CTkFont(size=10),
                      command=lambda: (delete_bug(bug["id"]),log_activity("DELETOU BUG",f"#{bug['id']}"),self._navigate("bugs"))
                      ).pack(side="right",padx=10)
        body = ctk.CTkScrollableFrame(detail, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=16, pady=10)
        ctk.CTkLabel(body, text="📝  Sumário:", font=ctk.CTkFont(size=11,weight="bold"), text_color="#888").pack(anchor="w")
        sb2 = ctk.CTkTextbox(body, height=70, fg_color="#111", corner_radius=8, font=ctk.CTkFont(size=12))
        sb2.pack(fill="x", pady=(4,12)); sb2.insert("end",bug.get("summary","")); sb2.configure(state="disabled")
        if bug.get("response"):
            rb = ctk.CTkTextbox(body, height=60, fg_color="#0a1a0a", corner_radius=8, font=ctk.CTkFont(size=12))
            rb.pack(fill="x", pady=(0,12)); rb.insert("end",bug["response"]); rb.configure(state="disabled")
        ctk.CTkLabel(body, text="✍️  Resposta:", font=ctk.CTkFont(size=11,weight="bold"), text_color="#888").pack(anchor="w")
        resp_e = ctk.CTkTextbox(body, height=90, fg_color="#111", corner_radius=8, font=ctk.CTkFont(size=12))
        if bug.get("response"): resp_e.insert("end",bug["response"])
        resp_e.pack(fill="x", pady=(4,6))
        st_var = ctk.StringVar(value=bug.get("status","pendente"))
        srow = ctk.CTkFrame(body, fg_color="transparent"); srow.pack(fill="x",pady=4)
        for sv in ["pendente","em análise","corrigido","não reproduzível"]:
            ctk.CTkRadioButton(srow, text=sv, variable=st_var, value=sv,
                               font=ctk.CTkFont(size=10)).pack(side="left",padx=6)
        def _save():
            resp = resp_e.get("1.0","end").strip()
            if not resp: return
            if reply_bug(bug["id"], resp, st_var.get()):
                log_activity("RESPOSTA BUG",f"#{bug['id']}")
                messagebox.showinfo("✅","Resposta salva no Supabase!"); self._navigate("bugs")
            else:
                messagebox.showerror("Erro","Falha ao salvar.")
        ctk.CTkButton(body, text="📨  Salvar Resposta", height=44,
                      fg_color="#1a3a00", hover_color="#2a5a00",
                      font=ctk.CTkFont(size=13,weight="bold"), command=_save).pack(fill="x",pady=6)

    # ── USUÁRIOS ─────────────────────────────────────────────────────────
    def _build_users(self):
        self._panel_header("👥  Usuários")
        tickets = load_support(); spam = load_spam()
        blocked = [b["name"] for b in spam.get("blocked",[])]
        from collections import defaultdict
        ud = defaultdict(lambda:{"tickets":0,"pendentes":0,"ultimo":""})
        for t in tickets:
            n = t.get("name","?").lower()
            ud[n]["tickets"] += 1
            if not t.get("response"): ud[n]["pendentes"] += 1
            if t.get("date","") > ud[n]["ultimo"]: ud[n]["ultimo"] = t.get("date","")
        body = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=16, pady=10)
        if not ud:
            ctk.CTkLabel(body, text="Nenhum usuário ainda.", text_color="#444",
                         font=ctk.CTkFont(size=12)).pack(pady=20); return
        for name, data in sorted(ud.items(), key=lambda x:-x[1]["tickets"]):
            is_bl = name in blocked
            row = ctk.CTkFrame(body, fg_color="#1a0000" if is_bl else "#111", corner_radius=8, height=36)
            row.pack(fill="x", pady=2); row.pack_propagate(False)
            ctk.CTkLabel(row, text=f"👤 {name[:20]}", width=175, font=ctk.CTkFont(size=11)).pack(side="left",padx=6)
            ctk.CTkLabel(row, text=str(data["tickets"]), width=60, text_color="#44aaff",
                         font=ctk.CTkFont(size=11)).pack(side="left")
            ctk.CTkLabel(row, text=str(data["pendentes"]), width=60,
                         text_color="#ffaa44" if data["pendentes"]>0 else "#555",
                         font=ctk.CTkFont(size=11)).pack(side="left")
            ctk.CTkLabel(row, text=data["ultimo"][:16], width=125,
                         text_color="#666", font=ctk.CTkFont(size=10)).pack(side="left")
            ctk.CTkLabel(row, text="🚫 BLOQUEADO" if is_bl else "✅ OK", width=110,
                         text_color="#ff4444" if is_bl else "#44ff88",
                         font=ctk.CTkFont(size=10)).pack(side="left")
            if is_bl:
                ctk.CTkButton(row, text="🔓 Desbloquear", width=110, height=26,
                              fg_color="#003300", hover_color="#005500", font=ctk.CTkFont(size=10),
                              command=lambda n=name: self._unblock(n)).pack(side="left",padx=4)
            else:
                ctk.CTkButton(row, text="🚫 Bloquear", width=110, height=26,
                              fg_color="#330000", hover_color="#550000", font=ctk.CTkFont(size=10),
                              command=lambda n=name: self._block(n,"Manual")).pack(side="left",padx=4)

    def _block(self, name, reason):
        spam = load_spam(); spam.setdefault("blocked",[])
        if name not in [b["name"] for b in spam["blocked"]]:
            spam["blocked"].append({"name":name,"reason":reason,"blocked_at":now_str()})
            save_spam(spam); log_activity("BLOQUEOU",name)
        self._navigate("usuarios")

    def _unblock(self, name):
        spam = load_spam()
        spam["blocked"] = [b for b in spam.get("blocked",[]) if b["name"]!=name]
        save_spam(spam); log_activity("DESBLOQUEOU",name); self._navigate("usuarios")


    # ── ANTI-SPAM ────────────────────────────────────────────────────────
    def _build_spam(self):
        self._panel_header("🛡  Anti-Spam")
        spam = load_spam(); blocked = spam.get("blocked",[])
        body = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=16, pady=10)
        ctk.CTkLabel(body, text=f"🚫  Usuários Bloqueados ({len(blocked)})",
                     font=ctk.CTkFont(size=12,weight="bold"), text_color="#ff4444").pack(anchor="w",pady=(0,6))
        if not blocked:
            ctk.CTkLabel(body, text="Nenhum bloqueado.", font=ctk.CTkFont(size=11), text_color="#444").pack(anchor="w")
        for b in blocked:
            row = ctk.CTkFrame(body, fg_color="#1a0000", corner_radius=8); row.pack(fill="x",pady=2)
            ctk.CTkLabel(row, text=f"🚫 {b['name']}", font=ctk.CTkFont(size=11,weight="bold"),
                         text_color="#ff4444", width=160).pack(side="left",padx=10,pady=8)
            ctk.CTkLabel(row, text=f"Motivo: {b.get('reason','')}", font=ctk.CTkFont(size=10),
                         text_color="#888", width=180).pack(side="left")
            ctk.CTkLabel(row, text=b.get("blocked_at",""), font=ctk.CTkFont(size=10),
                         text_color="#555", width=120).pack(side="left")
            ctk.CTkButton(row, text="🔓 Desbloquear", width=110, height=28,
                          fg_color="#003300", hover_color="#005500", font=ctk.CTkFont(size=10),
                          command=lambda n=b["name"]: self._unblock(n)).pack(side="right",padx=10)
        ctk.CTkFrame(body, height=1, fg_color="#222").pack(fill="x",pady=12)
        ctk.CTkLabel(body, text="➕  Bloquear manualmente:", font=ctk.CTkFont(size=11,weight="bold"),
                     text_color="#888").pack(anchor="w")
        ar = ctk.CTkFrame(body, fg_color="transparent"); ar.pack(fill="x",pady=6)
        be = ctk.CTkEntry(ar, placeholder_text="Nome do usuário", height=36, font=ctk.CTkFont(size=12))
        be.pack(side="left",fill="x",expand=True,padx=(0,8))
        ctk.CTkButton(ar, text="🚫 Bloquear", width=100, height=36,
                      fg_color="#330000", hover_color="#550000", font=ctk.CTkFont(size=12),
                      command=lambda: self._block(be.get().strip().lower(),"Manual")).pack(side="left")
        ctk.CTkFrame(body, height=1, fg_color="#222").pack(fill="x",pady=12)
        log = spam.get("log",[])
        ctk.CTkLabel(body, text=f"📋  Log ({len(log)})", font=ctk.CTkFont(size=12,weight="bold"),
                     text_color="#888").pack(anchor="w",pady=(0,6))
        for entry in reversed(log[-20:]):
            row = ctk.CTkFrame(body, fg_color="#111", corner_radius=6, height=28)
            row.pack(fill="x",pady=1); row.pack_propagate(False)
            ctk.CTkLabel(row, text=entry.get("time",""), font=ctk.CTkFont(size=9),
                         text_color="#444", width=120).pack(side="left",padx=6)
            ctk.CTkLabel(row, text=entry.get("name",""), font=ctk.CTkFont(size=10),
                         text_color="#ff8844", width=140).pack(side="left")
        ctk.CTkButton(body, text="🗑 Limpar Log", height=36,
                      fg_color="#1a1a00", hover_color="#2a2a00", font=ctk.CTkFont(size=11),
                      command=lambda: (spam.update({"log":[]}),save_spam(spam),self._navigate("spam"))
                      ).pack(fill="x",pady=8)

    # ── ANÚNCIOS ─────────────────────────────────────────────────────────
    def _build_announcements(self):
        self._panel_header("📢  Anúncios")
        body = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=16, pady=10)
        ctk.CTkLabel(body, text="✍️  Criar novo anúncio:",
                     font=ctk.CTkFont(size=12,weight="bold"), text_color="#44aaff").pack(anchor="w",pady=(0,6))
        tr = ctk.CTkFrame(body, fg_color="transparent"); tr.pack(fill="x",pady=4)
        ctk.CTkLabel(tr, text="Título:", width=70, font=ctk.CTkFont(size=11), text_color="#888").pack(side="left")
        ann_title = ctk.CTkEntry(tr, placeholder_text="Ex: Nova atualização!", height=36, font=ctk.CTkFont(size=12))
        ann_title.pack(side="left",fill="x",expand=True)
        type_var = ctk.StringVar(value="info")
        tyrow = ctk.CTkFrame(body, fg_color="transparent"); tyrow.pack(fill="x",pady=4)
        ctk.CTkLabel(tyrow, text="Tipo:", width=70, font=ctk.CTkFont(size=11), text_color="#888").pack(side="left")
        for tv,tl in [("info","ℹ️ Info"),("aviso","⚠️ Aviso"),("update","🆕 Update")]:
            ctk.CTkRadioButton(tyrow, text=tl, variable=type_var, value=tv,
                               font=ctk.CTkFont(size=11)).pack(side="left",padx=10)
        ctk.CTkLabel(body, text="Mensagem:", font=ctk.CTkFont(size=11), text_color="#888").pack(anchor="w")
        ann_msg = ctk.CTkTextbox(body, height=90, fg_color="#111", corner_radius=8, font=ctk.CTkFont(size=12))
        ann_msg.pack(fill="x",pady=(4,8))
        self._ann_st = ctk.CTkLabel(body, text="", font=ctk.CTkFont(size=11), text_color="#888")
        self._ann_st.pack(anchor="w")
        def _create():
            title = ann_title.get().strip(); msg = ann_msg.get("1.0","end").strip()
            if not title or not msg:
                messagebox.showwarning("Atenção","Preencha título e mensagem."); return
            ann = {"id":str(uuid.uuid4())[:8],"date":now_str(),
                   "title":title,"type":type_var.get(),"message":msg}
            if post_ann(ann):
                log_activity("CRIOU ANÚNCIO",title)
                self._ann_st.configure(text="✅ Anúncio publicado no Supabase!",text_color="#44ff88")
                ann_title.delete(0,"end"); ann_msg.delete("1.0","end")
                self.after(1500, lambda: self._navigate("announcements"))
            else:
                self._ann_st.configure(text="❌ Erro ao publicar.",text_color="#ff4444")
        ctk.CTkButton(body, text="📢  Publicar", height=42,
                      fg_color="#003a7a", hover_color="#0055bb",
                      font=ctk.CTkFont(size=13,weight="bold"), command=_create).pack(fill="x",pady=6)
        ctk.CTkFrame(body, height=1, fg_color="#333").pack(fill="x",pady=12)
        anns = load_announcements()
        ctk.CTkLabel(body, text=f"📋  Publicados ({len(anns)})",
                     font=ctk.CTkFont(size=12,weight="bold"), text_color="#888").pack(anchor="w",pady=(0,6))
        tclr = {"info":"#003a7a","aviso":"#3a2a00","update":"#003300"}
        ticn = {"info":"ℹ️","aviso":"⚠️","update":"🆕"}
        for ann in anns:
            row = ctk.CTkFrame(body, fg_color=tclr.get(ann.get("type","info"),"#111"), corner_radius=10)
            row.pack(fill="x",pady=3)
            top = ctk.CTkFrame(row, fg_color="transparent"); top.pack(fill="x",padx=12,pady=(8,2))
            ctk.CTkLabel(top, text=f"{ticn.get(ann.get('type',''),'📢')} {ann.get('title','')}",
                         font=ctk.CTkFont(size=12,weight="bold")).pack(side="left")
            ctk.CTkLabel(top, text=ann.get("date",""), font=ctk.CTkFont(size=10),
                         text_color="#555").pack(side="right")
            ctk.CTkLabel(row, text=ann.get("message","")[:80],
                         font=ctk.CTkFont(size=11), text_color="#aaa").pack(anchor="w",padx=12,pady=(0,4))
            btm = ctk.CTkFrame(row, fg_color="transparent"); btm.pack(fill="x",padx=12,pady=(0,8))
            ctk.CTkButton(btm, text="🗑 Deletar", width=80, height=26,
                          fg_color="#2a0000", hover_color="#440000", font=ctk.CTkFont(size=10),
                          command=lambda aid=ann.get("id",""): (delete_ann(aid),self._navigate("announcements"))
                          ).pack(side="right")


    # ── VERSÃO ───────────────────────────────────────────────────────────
    def _build_version(self):
        self._panel_header("🔖  Gerenciador de Versão")
        ver = load_version()
        body = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=16, pady=10)
        fields = {}
        for key, label, val in [
            ("version","Versão (ex: 1.0.1)",ver.get("version","1.0.0")),
            ("build","Build (número)",str(ver.get("build",1))),
            ("notes","Notas de atualização",ver.get("notes","")),
            ("download_pc","Link download PC",ver.get("download_pc","")),
            ("download_apk","Link download APK",ver.get("download_apk","")),
        ]:
            ctk.CTkLabel(body, text=label, font=ctk.CTkFont(size=11), text_color="#888").pack(anchor="w")
            if key == "notes":
                ent = ctk.CTkTextbox(body, height=80, fg_color="#111", corner_radius=8, font=ctk.CTkFont(size=12))
                ent.insert("end",val)
            else:
                ent = ctk.CTkEntry(body, height=38, font=ctk.CTkFont(size=12), fg_color="#111", corner_radius=8)
                ent.insert(0,val)
            ent.pack(fill="x",pady=(2,10)); fields[key] = ent
        def _save():
            nv = {"version":fields["version"].get().strip(),
                  "build":int(fields["build"].get().strip() or "1"),
                  "notes":fields["notes"].get("1.0","end").strip(),
                  "download_pc":fields["download_pc"].get().strip(),
                  "download_apk":fields["download_apk"].get().strip()}
            save_version(nv); log_activity("ATUALIZOU VERSÃO",nv["version"])
            messagebox.showinfo("✅",f"Versão {nv['version']} salva!"); self._navigate("version")
        ctk.CTkButton(body, text="💾  Salvar Versão", height=44,
                      fg_color="#0a001a", hover_color="#1a0a2a", text_color="#aa88ff",
                      font=ctk.CTkFont(size=13,weight="bold"), command=_save).pack(fill="x",pady=8)

    # ── LOGS ─────────────────────────────────────────────────────────────
    def _build_logs(self):
        self._panel_header("📋  Logs de Atividade")
        logs = list(reversed(load_activity()))
        body = ctk.CTkFrame(self.content, fg_color="transparent"); body.pack(fill="both",expand=True,padx=16,pady=10)
        ctk.CTkButton(body, text="🗑 Limpar logs", height=32, fg_color="#1a0000",
                      hover_color="#2a0000", font=ctk.CTkFont(size=11),
                      command=lambda: (save_activity([]),self._navigate("logs"))).pack(anchor="e",pady=(0,8))
        scroll = ctk.CTkScrollableFrame(body, fg_color="transparent"); scroll.pack(fill="both",expand=True)
        if not logs:
            ctk.CTkLabel(scroll, text="Nenhuma atividade.", font=ctk.CTkFont(size=12), text_color="#444").pack(pady=20)
        aclrs = {"LOGIN":"#44ff88","RESPOSTA":"#44aaff","DELETOU":"#ff4444","BLOQUEOU":"#ffaa44","CRIOU":"#aa88ff"}
        for entry in logs:
            row = ctk.CTkFrame(scroll, fg_color="#111", corner_radius=6, height=30)
            row.pack(fill="x",pady=1); row.pack_propagate(False)
            ctk.CTkLabel(row, text=entry.get("time",""), font=ctk.CTkFont(size=10),
                         text_color="#444", width=140).pack(side="left",padx=6)
            ac = entry.get("action","")
            acolor = next((v for k,v in aclrs.items() if k in ac),"#888")
            ctk.CTkLabel(row, text=ac, font=ctk.CTkFont(size=10,weight="bold"),
                         text_color=acolor, width=200).pack(side="left")
            ctk.CTkLabel(row, text=entry.get("detail","")[:80],
                         font=ctk.CTkFont(size=10), text_color="#666").pack(side="left",padx=4)

    # ── CONFIG ───────────────────────────────────────────────────────────
    def _build_config(self):
        self._panel_header("⚙️  Configurações")
        cfg = load_dev_config()
        body = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=16, pady=10)

        # Info Supabase
        sb_sec = ctk.CTkFrame(body, fg_color="#001a33", corner_radius=12); sb_sec.pack(fill="x",pady=(0,14))
        ctk.CTkLabel(sb_sec, text="☁️  Supabase — Banco Online",
                     font=ctk.CTkFont(size=12,weight="bold"), text_color="#44aaff").pack(anchor="w",padx=14,pady=(10,4))
        ctk.CTkLabel(sb_sec, text=f"URL: {SB_URL}",
                     font=ctk.CTkFont(size=10), text_color="#44ff88").pack(anchor="w",padx=14)
        ctk.CTkLabel(sb_sec, text="✅ Configurado automaticamente — sem necessidade de configuração manual.",
                     font=ctk.CTkFont(size=10), text_color="#555",wraplength=560).pack(anchor="w",padx=14,pady=(0,12))

        # Senha (protegida) — Heitor@cris
        sec = ctk.CTkFrame(body, fg_color="#111", corner_radius=12); sec.pack(fill="x",pady=(0,14))
        ctk.CTkLabel(sec, text="🔑  Segurança — Senha de Acesso",
                     font=ctk.CTkFont(size=12,weight="bold"), text_color="#ff8844").pack(anchor="w",padx=14,pady=(10,4))
        ctk.CTkLabel(sec, text="⚠️  Esta senha protege o Modo Desenvolvedor e arquivos sensíveis.",
                     font=ctk.CTkFont(size=10), text_color="#555",wraplength=560).pack(anchor="w",padx=14)
        pr = ctk.CTkFrame(sec, fg_color="transparent"); pr.pack(fill="x",padx=14,pady=(6,10))
        np = ctk.CTkEntry(pr, show="●", height=36, font=ctk.CTkFont(size=12),
                          placeholder_text="Nova senha...")
        np.pack(side="left",fill="x",expand=True,padx=(0,8))
        ctk.CTkButton(pr, text="💾 Salvar", width=90, height=36,
                      fg_color="#1a3a00", hover_color="#2a5a00", font=ctk.CTkFont(size=11),
                      command=lambda: self._save_pwd(np.get())).pack(side="left")

        # Zona de perigo
        dz = ctk.CTkFrame(body, fg_color="#1a0000", corner_radius=12); dz.pack(fill="x",pady=(0,14))
        ctk.CTkLabel(dz, text="⚠️  Zona de Perigo",
                     font=ctk.CTkFont(size=12,weight="bold"), text_color="#ff4444").pack(anchor="w",padx=14,pady=(10,4))
        for lbl, table in [("🗑 Limpar todos os tickets","tickets"),
                            ("🗑 Limpar todos os bugs","bugs"),
                            ("🗑 Limpar anúncios","announcements"),
                            ("🗑 Resetar spam local","spam")]:
            ctk.CTkButton(dz, text=lbl, height=34, fg_color="#220000", hover_color="#440000",
                          text_color="#ff6666", font=ctk.CTkFont(size=11),
                          command=lambda t=table: self._danger_clear(t)).pack(fill="x",padx=14,pady=2)
        ctk.CTkLabel(dz, text="").pack(pady=6)

    def _save_pwd(self, p):
        if len(p.strip()) < 4:
            messagebox.showwarning("Atenção","Senha precisa ter 4+ caracteres."); return
        cfg = load_dev_config()
        cfg["password_hash"] = _hash_pwd(p)
        save_dev_config(cfg)
        log_activity("ALTEROU SENHA","")
        messagebox.showinfo("✅","Senha atualizada com segurança! (hash SHA-256)")

    def _danger_clear(self, what):
        if not messagebox.askyesno("⚠️ CONFIRMAR",f"Deletar TODOS os dados de '{what}'?"):
            return
        if what == "spam":
            save_spam({"blocked":[],"log":[]})
        else:
            items = sb_get(what,"?select=id")
            for item in items: sb_delete(what, item["id"])
        log_activity(f"LIMPOU {what.upper()}","")
        messagebox.showinfo("Feito","Dados deletados.")
        self._navigate("config")


# ── Entry point ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = DevMode()
    app.mainloop()
