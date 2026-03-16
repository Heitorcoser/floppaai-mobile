# ═══════════════════════════════════════════════════════════════════
#  FloppaAI — Servidor Local + Auto-config Mobile
#  Serve o FloppaAIMobile.html com a URL já injetada automaticamente.
#  Uso: python server.py
# ═══════════════════════════════════════════════════════════════════
import json, os, datetime, uuid, socket
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

BASE  = os.path.dirname(os.path.abspath(__file__))
FILES = {
    "tickets":       os.path.join(BASE, "support.json"),
    "bugs":          os.path.join(BASE, "bugs.json"),
    "spam":          os.path.join(BASE, "spam_log.json"),
    "announcements": os.path.join(BASE, "announcements.json"),
}
PORT         = 8080
MOBILE_HTML  = os.path.join(BASE, "FloppaAIMobile.html")

def load(key):
    try:
        with open(FILES[key], "r", encoding="utf-8") as f: return json.load(f)
    except: return [] if key != "spam" else {"blocked":[], "log":[]}

def save(key, data):
    with open(FILES[key], "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80)); ip = s.getsockname()[0]; s.close(); return ip
    except: return "127.0.0.1"

def serve_mobile(handler, injected_url=""):
    """Lê o HTML e injeta a URL do servidor automaticamente."""
    try:
        with open(MOBILE_HTML, "r", encoding="utf-8") as f:
            html = f.read()
        # Injeta script no <head> que configura a URL antes de qualquer coisa
        inject = f"""<script>
// Auto-configurado pelo servidor FloppaAI
(function(){{
  var url = "{injected_url}";
  if (url && url.startsWith("http")) {{
    localStorage.setItem("fai_srv", url);
    localStorage.setItem("fai_auto", "1");
  }}
}})();
</script>"""
        html = html.replace("</head>", inject + "\n</head>", 1)
        body = html.encode("utf-8")
        handler.send_response(200)
        handler.send_header("Content-Type", "text/html; charset=utf-8")
        handler.send_header("Content-Length", len(body))
        handler.end_headers()
        handler.wfile.write(body)
    except Exception as e:
        handler.send_response(500)
        handler.end_headers()
        handler.wfile.write(f"Erro: {e}".encode())

class Handler(BaseHTTPRequestHandler):

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PATCH, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, ngrok-skip-browser-warning")

    def do_OPTIONS(self):
        self.send_response(204); self._cors(); self.end_headers()

    def _ok(self, data):
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", len(body))
        self._cors(); self.end_headers(); self.wfile.write(body)

    def _err(self, code, msg):
        body = json.dumps({"error": msg}).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self._cors(); self.end_headers(); self.wfile.write(body)

    def _body(self):
        n = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(n)) if n else {}

    def log_message(self, fmt, *args):
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"  [{ts}] {self.address_string()} — {fmt % args}")

    def route(self):
        p = urlparse(self.path).path.rstrip("/")
        parts = [x for x in p.split("/") if x]
        if len(parts) >= 2 and parts[0] == "api":
            return parts[1], parts[2] if len(parts) >= 3 else None
        return None, None

    # ── GET ───────────────────────────────────────────────────────
    def do_GET(self):
        path = urlparse(self.path).path.rstrip("/")

        # Serve o HTML mobile na raiz — injeta a URL automaticamente
        if path in ("", "/", "/mobile", "/app"):
            host = self.headers.get("Host", "")
            # Detecta se veio pelo ngrok (https) ou local (http)
            scheme = "https" if "ngrok" in host or "lhr.life" in host else "http"
            injected_url = f"{scheme}://{host}"
            serve_mobile(self, injected_url)
            print(f"  📱 Celular conectou! URL injetada: {injected_url}")
            return

        resource, rid = self.route()
        if not resource: self._err(404, "Not found"); return

        if resource == "tickets":
            data = load("tickets")
            if rid:
                item = next((t for t in data if t.get("id")==rid), None)
                self._ok(item) if item else self._err(404, "Não encontrado")
            else: self._ok(data)
        elif resource == "bugs":          self._ok(load("bugs"))
        elif resource == "announcements": self._ok(load("announcements"))
        elif resource == "ping":          self._ok({"status":"online","server":"FloppaAI"})
        else: self._err(404, "Recurso não encontrado")

    # ── POST ──────────────────────────────────────────────────────
    def do_POST(self):
        resource, _ = self.route()
        body = self._body()

        if resource == "tickets":
            name    = body.get("name","").lower()
            tickets = load("tickets")
            spam    = load("spam")
            # Bloqueado?
            if any(b["name"]==name for b in spam.get("blocked",[])):
                self._err(403,"Usuário bloqueado"); return
            # Rate limit
            now    = datetime.datetime.now()
            window = datetime.timedelta(minutes=10)
            recent = sum(1 for t in tickets
                if t.get("name","").lower()==name
                and (now - datetime.datetime.strptime(t["date"],"%d/%m/%Y %H:%M")) < window
                if self._try_parse(t.get("date","")))
            if recent >= 3:
                self._err(429,"Limite atingido. Aguarde 10 minutos."); return
            if not body.get("message") or len(body["message"].strip()) < 5:
                self._err(400,"Mensagem muito curta"); return
            ticket = {
                "id":       body.get("id") or str(uuid.uuid4())[:8],
                "date":     now.strftime("%d/%m/%Y %H:%M"),
                "name":     body.get("name","Anônimo"),
                "subject":  body.get("subject","outro"),
                "message":  body.get("message","").strip(),
                "response": "",
                "platform": body.get("platform","mobile")
            }
            tickets.append(ticket); save("tickets", tickets)
            print(f"  📨 Novo ticket de '{ticket['name']}': {ticket['message'][:50]}")
            self._ok({"ok":True,"id":ticket["id"]})

        elif resource == "bugs":
            bug = {
                "id":       body.get("id") or str(uuid.uuid4())[:8],
                "date":     datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
                "summary":  body.get("summary",""),
                "response": "", "status":"pendente",
                "platform": body.get("platform","mobile")
            }
            bugs = load("bugs"); bugs.append(bug); save("bugs", bugs)
            print(f"  🐛 Novo bug: {bug['summary'][:60]}")
            self._ok({"ok":True,"id":bug["id"]})

        elif resource == "announcements":
            ann = {
                "id":      body.get("id") or str(uuid.uuid4())[:8],
                "date":    datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
                "title":   body.get("title",""), "type": body.get("type","info"),
                "message": body.get("message","")
            }
            anns = load("announcements"); anns.append(ann); save("announcements", anns)
            self._ok({"ok":True})
        else:
            self._err(404,"Recurso não encontrado")

    def _try_parse(self, date_str):
        try: datetime.datetime.strptime(date_str,"%d/%m/%Y %H:%M"); return True
        except: return False

    # ── PATCH ─────────────────────────────────────────────────────
    def do_PATCH(self):
        resource, rid = self.route(); body = self._body()
        if resource == "tickets" and rid:
            items = load("tickets")
            for t in items:
                if t["id"]==rid: t.update({k:v for k,v in body.items() if k!="id"}); break
            save("tickets",items); self._ok({"ok":True})
        elif resource == "bugs" and rid:
            items = load("bugs")
            for b in items:
                if b["id"]==rid: b.update({k:v for k,v in body.items() if k!="id"}); break
            save("bugs",items); self._ok({"ok":True})
        else: self._err(404,"Não encontrado")

    # ── DELETE ────────────────────────────────────────────────────
    def do_DELETE(self):
        resource, rid = self.route()
        if resource=="tickets" and rid:
            save("tickets",[t for t in load("tickets") if t["id"]!=rid]); self._ok({"ok":True})
        elif resource=="bugs" and rid:
            save("bugs",[b for b in load("bugs") if b["id"]!=rid]); self._ok({"ok":True})
        elif resource=="announcements" and rid:
            save("announcements",[a for a in load("announcements") if a.get("id")!=rid]); self._ok({"ok":True})
        else: self._err(404,"Não encontrado")


# ── MAIN ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    ip = get_local_ip()
    httpd = HTTPServer(("0.0.0.0", PORT), Handler)
    print()
    print("  ╔══════════════════════════════════════════════════════╗")
    print("  ║       FloppaAI — Servidor Ativo 🟢                  ║")
    print("  ╠══════════════════════════════════════════════════════╣")
    print(f"  ║  IP local:  http://{ip}:{PORT}".ljust(56)+"║")
    print(f"  ║  Porta:     {PORT}".ljust(56)+"║")
    print("  ╠══════════════════════════════════════════════════════╣")
    print("  ║  📱 Celular abre a URL do ngrok e já configura!      ║")
    print("  ║  Ex: https://xxxx.ngrok-free.app  →  abre o app      ║")
    print("  ╚══════════════════════════════════════════════════════╝")
    print()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n  🔴 Servidor encerrado.")
