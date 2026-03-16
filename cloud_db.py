# ═══════════════════════════════════════════════════════════════════════════
#   cloud_db.py — FloppaAI Firebase Realtime Database Integration
#   Funciona de QUALQUER PC, em QUALQUER lugar do mundo.
#   Usa apenas requests (sem SDK extra). 100% gratuito no plano Spark.
# ═══════════════════════════════════════════════════════════════════════════
import requests, json, os, datetime

BASE_DIR          = os.path.dirname(os.path.abspath(__file__))
FIREBASE_URL_FILE = os.path.join(BASE_DIR, "firebase_url.txt")
LOCAL_SUPPORT     = os.path.join(BASE_DIR, "support.json")
LOCAL_BUGS        = os.path.join(BASE_DIR, "bugs.json")
LOCAL_SPAM        = os.path.join(BASE_DIR, "spam_log.json")
LOCAL_ANNOUNCE    = os.path.join(BASE_DIR, "announcements.json")

def _load_local(path, default):
    try:
        with open(path,"r",encoding="utf-8") as f: return json.load(f)
    except: return default

def _save_local(path, data):
    try:
        with open(path,"w",encoding="utf-8") as f: json.dump(data,f,ensure_ascii=False,indent=2)
    except: pass

class CloudDB:
    """
    Wrapper Firebase REST API.
    Se firebase_url.txt não existir, cai em modo LOCAL (retrocompatível).
    """

    def __init__(self, url: str = None):
        if url:
            self._base = url.rstrip("/")
        else:
            try:
                with open(FIREBASE_URL_FILE,"r") as f:
                    self._base = f.read().strip().rstrip("/")
            except:
                self._base = None

    @property
    def online(self): return bool(self._base)

    def _url(self, path): return f"{self._base}/{path}.json"

    # ── GET ──────────────────────────────────────────────────────────────────
    def _get(self, path):
        if not self.online: return None
        try:
            r = requests.get(self._url(path), timeout=8)
            if r.status_code == 200: return r.json()
        except: pass
        return None

    # ── PUT (substitui nó inteiro) ────────────────────────────────────────
    def _put(self, path, data):
        if not self.online: return False
        try:
            r = requests.put(self._url(path), json=data, timeout=8)
            return r.status_code == 200
        except: return False

    # ── POST (cria item novo com key auto) ────────────────────────────────
    def _post(self, path, data):
        if not self.online: return False
        try:
            r = requests.post(self._url(path), json=data, timeout=8)
            return r.status_code == 200
        except: return False

    # ── PATCH (atualiza campos) ───────────────────────────────────────────
    def _patch(self, path, data):
        if not self.online: return False
        try:
            r = requests.patch(self._url(path), json=data, timeout=8)
            return r.status_code == 200
        except: return False

    # ── DELETE ────────────────────────────────────────────────────────────
    def _delete(self, path):
        if not self.online: return False
        try:
            r = requests.delete(self._url(path), timeout=8)
            return r.status_code == 200
        except: return False

    # ── TEST ─────────────────────────────────────────────────────────────
    def test_connection(self):
        if not self.online: return False
        try:
            r = requests.get(self._url("_ping"), timeout=6)
            return r.status_code in (200, 404)  # 404 = nó vazio, mas Firebase respondeu
        except: return False

    # ══════════════════════════════════════════════════════════════════
    #   TICKETS DE SUPORTE
    # ══════════════════════════════════════════════════════════════════
    def get_tickets(self):
        """Retorna lista de tickets. Nuvem > local como fallback."""
        if self.online:
            raw = self._get("tickets")
            if isinstance(raw, dict):
                tickets = list(raw.values())
                _save_local(LOCAL_SUPPORT, tickets)   # cache local
                return tickets
            elif raw is None:
                return _load_local(LOCAL_SUPPORT, []) # fallback offline
        return _load_local(LOCAL_SUPPORT, [])

    def push_ticket(self, ticket: dict):
        """Envia ticket para nuvem E salva localmente."""
        # Salva local
        local = _load_local(LOCAL_SUPPORT, [])
        local.append(ticket)
        _save_local(LOCAL_SUPPORT, local)
        # Envia para nuvem
        if self.online:
            return self._put(f"tickets/{ticket['id']}", ticket)
        return False  # sem nuvem, apenas local

    def update_ticket(self, ticket_id: str, data: dict):
        """Atualiza campos de um ticket (ex: adicionar resposta)."""
        # Atualiza local
        local = _load_local(LOCAL_SUPPORT, [])
        for t in local:
            if t["id"] == ticket_id: t.update(data)
        _save_local(LOCAL_SUPPORT, local)
        # Atualiza nuvem
        if self.online:
            return self._patch(f"tickets/{ticket_id}", data)
        return False

    def delete_ticket(self, ticket_id: str):
        local = [t for t in _load_local(LOCAL_SUPPORT,[]) if t["id"]!=ticket_id]
        _save_local(LOCAL_SUPPORT, local)
        if self.online: return self._delete(f"tickets/{ticket_id}")
        return False

    # ══════════════════════════════════════════════════════════════════
    #   BUG REPORTS
    # ══════════════════════════════════════════════════════════════════
    def get_bugs(self):
        if self.online:
            raw = self._get("bugs")
            if isinstance(raw, dict):
                bugs = list(raw.values())
                _save_local(LOCAL_BUGS, bugs)
                return bugs
            elif raw is None:
                return _load_local(LOCAL_BUGS, [])
        return _load_local(LOCAL_BUGS, [])

    def push_bug(self, bug: dict):
        local = _load_local(LOCAL_BUGS, [])
        local.append(bug)
        _save_local(LOCAL_BUGS, local)
        if self.online: return self._put(f"bugs/{bug['id']}", bug)
        return False

    def update_bug(self, bug_id: str, data: dict):
        local = _load_local(LOCAL_BUGS, [])
        for b in local:
            if b["id"] == bug_id: b.update(data)
        _save_local(LOCAL_BUGS, local)
        if self.online: return self._patch(f"bugs/{bug_id}", data)
        return False

    def delete_bug(self, bug_id: str):
        local = [b for b in _load_local(LOCAL_BUGS,[]) if b["id"]!=bug_id]
        _save_local(LOCAL_BUGS, local)
        if self.online: return self._delete(f"bugs/{bug_id}")
        return False

    # ══════════════════════════════════════════════════════════════════
    #   SPAM / USUÁRIOS BLOQUEADOS
    # ══════════════════════════════════════════════════════════════════
    def get_spam(self):
        if self.online:
            raw = self._get("spam")
            if isinstance(raw, dict) and ("blocked" in raw or "log" in raw):
                _save_local(LOCAL_SPAM, raw); return raw
        return _load_local(LOCAL_SPAM, {"blocked":[],"log":[]})

    def save_spam(self, data: dict):
        _save_local(LOCAL_SPAM, data)
        if self.online: return self._put("spam", data)
        return False

    def is_user_blocked(self, name: str):
        spam = self.get_spam()
        return name.lower() in [b["name"] for b in spam.get("blocked",[])]

    def log_spam_attempt(self, name: str, action: str):
        spam = self.get_spam()
        spam.setdefault("log",[]).append({
            "name": name, "time": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"), "action": action})
        if len(spam["log"]) > 500: spam["log"] = spam["log"][-500:]
        self.save_spam(spam)

    # ══════════════════════════════════════════════════════════════════
    #   ANÚNCIOS
    # ══════════════════════════════════════════════════════════════════
    def get_announcements(self):
        if self.online:
            raw = self._get("announcements")
            if isinstance(raw, dict):
                anns = list(raw.values())
                _save_local(LOCAL_ANNOUNCE, anns); return anns
            elif raw is None: return _load_local(LOCAL_ANNOUNCE, [])
        return _load_local(LOCAL_ANNOUNCE, [])

    def push_announcement(self, ann: dict):
        local = _load_local(LOCAL_ANNOUNCE, [])
        local.append(ann); _save_local(LOCAL_ANNOUNCE, local)
        if self.online: return self._put(f"announcements/{ann['id']}", ann)
        return False

    def delete_announcement(self, ann_id: str):
        local = [a for a in _load_local(LOCAL_ANNOUNCE,[]) if a.get("id")!=ann_id]
        _save_local(LOCAL_ANNOUNCE, local)
        if self.online: return self._delete(f"announcements/{ann_id}")
        return False

    # ══════════════════════════════════════════════════════════════════
    #   ANTI-SPAM — contagem de tickets por usuário
    # ══════════════════════════════════════════════════════════════════
    def check_spam_limit(self, name: str, config: dict) -> tuple:
        """
        Retorna (bloqueado: bool, motivo: str).
        Verifica: usuário bloqueado, tamanho mínimo, limite de tickets na janela.
        """
        name_l = name.strip().lower()
        spam = self.get_spam()

        # 1) Usuário na lista de bloqueados
        if name_l in [b["name"] for b in spam.get("blocked",[])]:
            return True, "Usuário bloqueado"

        # 2) Conta tickets recentes do usuário
        limit  = int(config.get("spam_limit", 3))
        window = int(config.get("spam_window_min", 10))
        cutoff = datetime.datetime.now() - datetime.timedelta(minutes=window)

        tickets = self.get_tickets()
        recent  = 0
        for t in tickets:
            if t.get("name","").lower() != name_l: continue
            try:
                dt = datetime.datetime.strptime(t["date"], "%d/%m/%Y %H:%M")
                if dt >= cutoff: recent += 1
            except: pass

        if recent >= limit:
            # Auto-block se ultrapassou threshold
            auto_block = int(config.get("auto_block_after", 5))
            all_from_user = sum(1 for t in tickets if t.get("name","").lower()==name_l)
            if all_from_user >= auto_block:
                spam.setdefault("blocked",[]).append({
                    "name": name_l, "reason": "Auto-bloqueado por spam",
                    "blocked_at": datetime.datetime.now().strftime("%d/%m/%Y %H:%M")})
                self.save_spam(spam)
            return True, f"Limite de {limit} tickets em {window} minutos atingido"

        return False, ""
