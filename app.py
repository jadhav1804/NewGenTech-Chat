#!/usr/bin/env python3
# realtime_chat_single_file.py - Modern attractive chat with multiple media types (no extra packages)
import http.server, socketserver, threading, time, json, os, sys, urllib.parse, socket, subprocess, re, mimetypes, base64
from collections import deque

HOST = "0.0.0.0"
PORT = 8080
MAX_MESSAGES = 500
UPLOAD_DIR = "uploads"
EMOJI_DIR = "emojis"
STICKER_DIR = "stickers"

for dir in [UPLOAD_DIR, EMOJI_DIR, STICKER_DIR]:
    os.makedirs(dir, exist_ok=True)

# Pre-populate with some default emojis and stickers
def init_default_assets():
    # Common emojis as text - using Unicode escape sequences for Windows compatibility
    common_emojis = {
        "smile": "\U0001f60a",
        "heart": "\u2764\ufe0f",
        "thumbsup": "\U0001f44d",
        "laugh": "\U0001f602",
        "fire": "\U0001f525",
        "clap": "\U0001f44f",
        "star": "\u2b50",
        "rocket": "\U0001f680",
        "ok": "\U0001f44c",
        "eyes": "\U0001f440",
        "cool": "\U0001f60e",
        "wink": "\U0001f609",
        "kiss": "\U0001f618",
        "sunglasses": "\U0001f60e",
        "thinking": "\U0001f914",
        "party": "\U0001f389",
        "balloon": "\U0001f388",
        "gift": "\U0001f381",
        "cake": "\U0001f370",
        "coffee": "\u2615",
        "beer": "\U0001f37a",
        "music": "\U0001f3b5",
        "camera": "\U0001f4f7",
        "phone": "\U0001f4f1",
        "computer": "\U0001f4bb",
        "book": "\U0001f4d6",
        "lightbulb": "\U0001f4a1",
        "money": "\U0001f4b0",
        "shopping": "\U0001f6cd",
        "car": "\U0001f697",
        "plane": "\u2708\ufe0f",
        "ship": "\U0001f6a2",
        "train": "\U0001f686",
        "bike": "\U0001f6b2",
        "moon": "\U0001f319",
        "sun": "\u2600\ufe0f",
        "cloud": "\u2601\ufe0f",
        "rain": "\U0001f327",
        "snow": "\u2744\ufe0f",
        "tree": "\U0001f332",
        "flower": "\U0001f339",
        "cat": "\U0001f431",
        "dog": "\U0001f436",
        "panda": "\U0001f43c",
        "lion": "\U0001f981",
        "tiger": "\U0001f42f",
        "bear": "\U0001f43b",
        "rabbit": "\U0001f430",
        "fox": "\U0001f98a",
        "owl": "\U0001f989",
        "eagle": "\U0001f985",
        "duck": "\U0001f986",
        "fish": "\U0001f41f",
        "butterfly": "\U0001f98b",
        "bee": "\U0001f41d",
        "snail": "\U0001f40c",
        "turtle": "\U0001f422",
        "snake": "\U0001f40d",
        "dinosaur": "\U0001f996",
        "ghost": "\U0001f47b",
        "alien": "\U0001f47d",
        "robot": "\U0001f916",
        "unicorn": "\U0001f984",
        "dragon": "\U0001f409",
        "skull": "\U0001f480",
        "angel": "\U0001f47c",
        "santa": "\U0001f385",
        "prince": "\U0001f934",
        "princess": "\U0001f478",
        "superhero": "\U0001f9b8",
        "wizard": "\U0001f9d9",
        "vampire": "\U0001f9db",
        "zombie": "\U0001f9df",
        "mage": "\U0001f9d9",
        "fairy": "\U0001f9da",
        "genie": "\U0001f9de",
        "merperson": "\U0001f9dc",
        "elf": "\U0001f9dd",
        "handshake": "\U0001f91d",
        "wave": "\U0001f44b",
        "point": "\U0001f449",
        "fist": "\u270a",
        "peace": "\u270c\ufe0f",
        "call": "\U0001f919",
        "muscle": "\U0001f4aa",
        "leg": "\U0001f9b5",
        "foot": "\U0001f9b6",
        "ear": "\U0001f442",
        "nose": "\U0001f443",
        "brain": "\U0001f9e0",
        "bone": "\U0001f9b4",
        "tooth": "\U0001f9b7"
    }
    
    for name, emoji in common_emojis.items():
        try:
            with open(os.path.join(EMOJI_DIR, f"{name}.txt"), "w", encoding="utf-8") as f:
                f.write(emoji)
        except Exception as e:
            print(f"Warning: Could not save emoji {name}: {e}")

    # Create some sample stickers (text-based for now)
    sticker_data = {
        "happy": "🎉 Party Time! 🎉",
        "love": "❤️ Love You! ❤️",
        "congrats": "🎊 Congratulations! 🎊",
        "sorry": "😔 I'm Sorry",
        "thankyou": "🙏 Thank You!",
        "welcome": "👋 Welcome!",
        "goodmorning": "☀️ Good Morning!",
        "goodnight": "🌙 Good Night!",
        "birthday": "🎂 Happy Birthday!",
        "celebration": "🥳 Celebration Time!",
        "winning": "🏆 We're Winning!",
        "goals": "⚽ Goal!",
        "vacation": "🏖️ Vacation Mode!",
        "work": "💼 Time to Work!",
        "study": "📚 Study Time!",
        "game": "🎮 Game On!",
        "movie": "🎬 Movie Night!",
        "music": "🎵 Music Time!",
        "food": "🍕 Food Time!",
        "coffee": "☕ Coffee Break!",
        "shopping": "🛍️ Shopping Time!",
        "travel": "✈️ Let's Travel!",
        "nature": "🌲 Nature Love!",
        "animal": "🐾 Animal Lover!",
        "tech": "💻 Tech Geek!",
        "science": "🔬 Science Rules!",
        "art": "🎨 Be Creative!",
        "sports": "⚽ Sports Fan!",
        "fitness": "💪 Fitness Time!",
        "yoga": "🧘 Yoga Time!",
        "meditate": "😌 Peace & Calm"
    }
    
    for name, text in sticker_data.items():
        try:
            with open(os.path.join(STICKER_DIR, f"{name}.txt"), "w", encoding="utf-8") as f:
                f.write(text)
        except Exception as e:
            print(f"Warning: Could not save sticker {name}: {e}")

messages = deque(maxlen=MAX_MESSAGES)
msg_cond = threading.Condition()
active_calls = {}

def now_ms(): return int(time.time() * 1000)

def local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]; s.close(); return ip
    except: return socket.gethostbyname(socket.gethostname())

def start_tunnel(port):
    try:
        cmd = ["ssh","-o","StrictHostKeyChecking=accept-new","-o","ServerAliveInterval=60","-R",f"80:localhost:{port}","nokey@localhost.run","-N"]
        proc = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1)
        def reader():
            for line in proc.stdout:
                m = re.search(r"https://[a-zA-Z0-9\-\.]+", line.strip())
                if m: print(f"[Public URL] {m.group(0)}")
        threading.Thread(target=reader,daemon=True).start()
        return proc
    except: return None

def get_file_icon(filename):
    ext = os.path.splitext(filename)[1].lower()
    icons = {
        '.pdf': '📕', '.doc': '📘', '.docx': '📘', '.txt': '📄',
        '.zip': '📦', '.rar': '📦', '.7z': '📦',
        '.mp3': '🎵', '.wav': '🎵', '.ogg': '🎵',
        '.mp4': '🎬', '.avi': '🎬', '.mov': '🎬', '.mkv': '🎬',
        '.xls': '📊', '.xlsx': '📊', '.csv': '📊',
        '.ppt': '📊', '.pptx': '📊'
    }
    return icons.get(ext, '📎')

class ChatHandler(http.server.BaseHTTPRequestHandler):
    def _set_headers(self,status=200,extra=None,ctype="text/html; charset=utf-8"):
        self.send_response(status); self.send_header("Content-Type",ctype)
        self.send_header("Cache-Control","no-store, no-cache, must-revalidate")
        if extra: [self.send_header(k,v) for k,v in extra.items()]
        self.end_headers()
    def log_message(self,fmt,*a): sys.stdout.write("[%s] %s\n"%(self.address_string(),fmt%a))

    def do_GET(self):
        p = urllib.parse.urlparse(self.path)
        if p.path == "/": return self.page()
        if p.path == "/stream": return self.sse()
        if p.path == "/history":
            self._set_headers(200,ctype="application/json"); 
            with msg_cond: self.wfile.write(json.dumps(list(messages)).encode())
        elif p.path == "/emojis":
            emojis = {}
            for f in os.listdir(EMOJI_DIR):
                if f.endswith('.txt'):
                    try:
                        with open(os.path.join(EMOJI_DIR, f), 'r', encoding="utf-8") as ef:
                            emojis[f[:-4]] = ef.read().strip()
                    except:
                        continue
            self._set_headers(200,ctype="application/json")
            self.wfile.write(json.dumps(emojis).encode())
        elif p.path == "/stickers":
            stickers = {}
            for f in os.listdir(STICKER_DIR):
                if f.endswith('.txt'):
                    name = os.path.splitext(f)[0]
                    try:
                        with open(os.path.join(STICKER_DIR, f), 'r', encoding="utf-8") as sf:
                            stickers[name] = sf.read().strip()
                    except:
                        continue
            self._set_headers(200,ctype="application/json")
            self.wfile.write(json.dumps(stickers).encode())
        elif p.path.startswith("/uploads/"):
            return self.serve_file(p.path[1:])
        elif p.path.startswith("/" + STICKER_DIR + "/"):
            return self.serve_file(p.path[1:])
        elif p.path == "/call-status":
            return self.get_call_status()
        else:
            self._set_headers(404,ctype="text/plain"); self.wfile.write(b"Not found")

    def do_POST(self):
        if self.path == "/send": return self.handle_text()
        if self.path == "/upload": return self.handle_upload()
        if self.path == "/start-call": return self.start_call()
        if self.path == "/end-call": return self.end_call()
        if self.path == "/send-emoji": return self.handle_emoji()
        if self.path == "/send-sticker": return self.handle_sticker()
        self._set_headers(404,ctype="text/plain")

    def handle_text(self):
        ln = int(self.headers.get("Content-Length",0)); data = urllib.parse.parse_qs(self.rfile.read(ln).decode())
        user = (data.get("username",["Anon"])[0][:30]).strip() or "Anon"
        text = (data.get("text",[""])[0]).strip()
        if not text: self._set_headers(400,ctype="text/plain"); return
        msg = {"user":user,"text":text,"ts":now_ms(),"type":"text"}
        with msg_cond: messages.append(msg); msg_cond.notify_all()
        self._set_headers(204,ctype="text/plain")

    def handle_emoji(self):
        ln = int(self.headers.get("Content-Length",0)); data = json.loads(self.rfile.read(ln).decode())
        user = data.get("username", "Anon")[:30].strip() or "Anon"
        emoji = data.get("emoji", "")
        if not emoji: self._set_headers(400,ctype="text/plain"); return
        msg = {"user":user,"text":emoji,"ts":now_ms(),"type":"emoji"}
        with msg_cond: messages.append(msg); msg_cond.notify_all()
        self._set_headers(200,ctype="application/json")
        self.wfile.write(json.dumps({"status":"sent"}).encode())

    def handle_sticker(self):
        ln = int(self.headers.get("Content-Length",0)); data = json.loads(self.rfile.read(ln).decode())
        user = data.get("username", "Anon")[:30].strip() or "Anon"
        sticker = data.get("sticker", "")
        if not sticker: self._set_headers(400,ctype="text/plain"); return
        # Format sticker as a nice message
        sticker_msg = f"""
        <div style="background:linear-gradient(135deg,#667eea,#764ba2);padding:15px;border-radius:20px;text-align:center;color:white;font-weight:bold;font-size:18px;max-width:200px;margin:5px 0;">
            {sticker}
        </div>
        """
        msg = {"user":user,"text":sticker_msg,"ts":now_ms(),"type":"sticker"}
        with msg_cond: messages.append(msg); msg_cond.notify_all()
        self._set_headers(200,ctype="application/json")
        self.wfile.write(json.dumps({"status":"sent"}).encode())

    def handle_upload(self):
        ctype = self.headers.get("Content-Type","")
        if not ctype.startswith("multipart/form-data"):
            self._set_headers(400,ctype="text/plain"); return
        boundary = ctype.split("boundary=")[-1].encode()
        length = int(self.headers.get("Content-Length",0))
        body = self.rfile.read(length)

        parts = body.split(b"--"+boundary)
        for part in parts:
            if b"Content-Disposition" in part:
                header, filedata = part.split(b"\r\n\r\n",1) if b"\r\n\r\n" in part else (part, b"")
                filedata = filedata.rstrip(b"\r\n-")
                
                # Get filename
                filename_match = re.search(br'filename="([^"]+)"', header)
                if not filename_match: 
                    # Check for username
                    um = re.search(br'name="username"\r\n\r\n([^-\r\n]+)', part)
                    if um: user = um.group(1).decode().strip() or "Anon"
                    continue
                    
                fname = filename_match.group(1).decode().replace(" ","_")
                fpath = os.path.join(UPLOAD_DIR,f"{int(time.time())}_{fname}")
                with open(fpath,"wb") as f: f.write(filedata)
                url = "/"+fpath.replace("\\","/")
                
                # Determine file type and create appropriate message
                ext = os.path.splitext(fname)[1].lower()
                if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
                    content = f"<img src='{url}' style='max-width:200px;border-radius:8px;cursor:pointer' onclick='window.open(this.src)'/>"
                    msg_type = "image"
                elif ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm']:
                    content = f"""
                    <video controls style='max-width:200px;border-radius:8px;'>
                        <source src='{url}' type='video/mp4'>
                        Your browser does not support the video tag.
                    </video>
                    """
                    msg_type = "video"
                elif ext in ['.mp3', '.wav', '.ogg', '.m4a']:
                    content = f"""
                    <audio controls style='width:200px;'>
                        <source src='{url}' type='audio/mpeg'>
                        Your browser does not support the audio tag.
                    </audio>
                    <span style='font-size:12px;color:#888;'>🎵 Audio file</span>
                    """
                    msg_type = "audio"
                else:
                    icon = get_file_icon(fname)
                    content = f"{icon} <a href='{url}' download='{fname}' style='color:#00a884;text-decoration:none;'>Download {fname}</a>"
                    msg_type = "file"
                
                msg = {"user":user,"text":content,"ts":now_ms(),"type":msg_type}
                with msg_cond: messages.append(msg); msg_cond.notify_all()
        self._set_headers(204,ctype="text/plain")

    def start_call(self):
        length = int(self.headers.get("Content-Length",0))
        data = json.loads(self.rfile.read(length).decode())
        user = data.get("username", "Anon")
        call_id = data.get("callId", str(int(time.time())))
        
        active_calls[call_id] = {
            "users": [user],
            "start_time": now_ms(),
            "type": data.get("callType", "voice")
        }
        
        # Notify all users about the call
        msg = {
            "user": "system", 
            "text": f"📞 {user} started a {active_calls[call_id]['type']} call",
            "ts": now_ms(),
            "type": "system",
            "callId": call_id
        }
        with msg_cond: messages.append(msg); msg_cond.notify_all()
        
        self._set_headers(200,ctype="application/json")
        self.wfile.write(json.dumps({"callId": call_id, "status": "started"}).encode())

    def end_call(self):
        length = int(self.headers.get("Content-Length",0))
        data = json.loads(self.rfile.read(length).decode())
        call_id = data.get("callId")
        user = data.get("username", "Anon")
        
        if call_id in active_calls:
            duration = (now_ms() - active_calls[call_id]["start_time"]) // 1000
            del active_calls[call_id]
            
            # Notify all users about call end
            msg = {
                "user": "system", 
                "text": f"📞 Call ended (duration: {duration}s)",
                "ts": now_ms(),
                "type": "system"
            }
            with msg_cond: messages.append(msg); msg_cond.notify_all()
        
        self._set_headers(200,ctype="application/json")
        self.wfile.write(json.dumps({"status": "ended"}).encode())

    def get_call_status(self):
        self._set_headers(200,ctype="application/json")
        self.wfile.write(json.dumps(active_calls).encode())

    def serve_file(self, path):
        fpath = os.path.join(".", path)
        if not os.path.isfile(fpath): self._set_headers(404,ctype="text/plain"); self.wfile.write(b"Not found"); return
        ctype = mimetypes.guess_type(fpath)[0] or "application/octet-stream"
        self._set_headers(200,ctype=ctype)
        with open(fpath,"rb") as f: self.wfile.write(f.read())

    def page(self):
        self._set_headers()
        self.wfile.write(f"""<!doctype html>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>NewGen Tech Chat</title>
<style>
body{{margin:0;font-family:Segoe UI,Roboto,sans-serif;background:linear-gradient(135deg,#0f2027,#203a43,#2c5364);color:#fff;display:flex;flex-direction:column;height:100vh;}}
header{{background:rgba(0,0,0,0.4);padding:12px 16px;font-size:18px;font-weight:bold;color:#fff;text-align:center;backdrop-filter:blur(4px);position:sticky;top:0;z-index:1;display:flex;justify-content:space-between;align-items:center;}}
#log{{flex:1;overflow-y:auto;padding:10px;display:flex;flex-direction:column;gap:10px;}}
.msg-wrap{{display:flex;align-items:flex-end;gap:8px;animation:fadeIn 0.3s ease;}}
.me{{flex-direction:row-reverse;}}
.avatar{{width:32px;height:32px;border-radius:50%;background:#00a884;display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:bold;color:#fff;}}
.bubble{{max-width:70%;padding:10px 14px;border-radius:14px;line-height:1.4;word-wrap:break-word;box-shadow:0 2px 4px rgba(0,0,0,0.3);background:rgba(255,255,255,0.1);}}
.me .bubble{{background:#00a884;color:#fff;border-bottom-right-radius:4px;}}
.other .bubble{{border-bottom-left-radius:4px;}}
.meta{{font-size:11px;opacity:0.7;margin-top:4px;}}
.system-msg{{text-align:center;color:#aaa;font-style:italic;margin:5px 0;}}
.emoji-msg{{font-size:2em;text-align:center;padding:10px;}}
.sticker-msg{{text-align:center;padding:5px;}}
form{{display:flex;padding:10px;background:rgba(0,0,0,0.3);gap:8px;position:sticky;bottom:0;backdrop-filter:blur(4px);}}
input,button{{padding:10px;border:none;border-radius:8px;font-size:15px;}}
input[name=text]{{flex:1;}}
button{{background:#00a884;color:#fff;cursor:pointer;}}
.controls{{display:flex;gap:5px;}}
.icon-btn{{background:none;border:none;color:#fff;font-size:18px;cursor:pointer;padding:5px;}}
.picker{{position:absolute;bottom:60px;background:rgba(0,0,0,0.9);border-radius:10px;padding:10px;max-width:300px;max-height:200px;overflow-y:auto;display:none;flex-wrap:wrap;gap:5px;backdrop-filter:blur(10px);z-index:1000;}}
.emoji{{font-size:24px;cursor:pointer;padding:5px;transition:transform 0.2s;}}
.emoji:hover{{transform:scale(1.2);}}
.sticker{{padding:8px 12px;background:linear-gradient(135deg,#667eea,#764ba2);border-radius:15px;cursor:pointer;color:white;font-weight:bold;text-align:center;min-width:80px;transition:transform 0.2s;}}
.sticker:hover{{transform:scale(1.05);}}
.recorder{{display:none;position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);background:rgba(0,0,0,0.9);padding:20px;border-radius:10px;z-index:1000;}}
.call-ui{{position:fixed;top:10px;right:10px;background:rgba(0,0,0,0.8);padding:10px;border-radius:10px;z-index:999;}}
@keyframes fadeIn{{from{{opacity:0;transform:translateY(5px);}}to{{opacity:1;transform:translateY(0);}}}}
.typing{{font-style:italic;color:#aaa;font-size:12px;padding:5px 10px;}}
.recording-animation{{animation:pulse 1s infinite;}}
@keyframes pulse{{0%{{opacity:1;}}50%{{opacity:0.5;}}100%{{opacity:1;}}}}
</style>
<header>
    <span>💬 NewGen Tech Chat</span>
    <div class="controls">
        <button class="icon-btn" onclick="toggleEmojiPicker()">😀</button>
        <button class="icon-btn" onclick="toggleStickerPicker()">🖼️</button>
        <button class="icon-btn" onclick="toggleVoiceCall()">📞</button>
        <button class="icon-btn" onclick="toggleVideoCall()">🎥</button>
    </div>
</header>
<div id="log"></div>
<div id="typing"></div>
<form id="f" enctype="multipart/form-data">
<input name="username" placeholder="Name" required style="max-width:120px">
<input name="text" placeholder="Type a message..." autocomplete="off" id="textInput">
<input type="file" name="file" accept="*/*" id="fileInput" style="display:none">
<button type="button" onclick="document.getElementById('fileInput').click()">📎</button>
<button type="button" id="recordBtn" onclick="toggleRecording()">🎤</button>
<button type="submit">Send</button>
</form>

<div id="emojiPicker" class="picker"></div>
<div id="stickerPicker" class="picker"></div>
<div id="recorder" class="recorder">
    <h3>🎤 Recording...</h3>
    <div style="display:flex;align-items:center;gap:10px;margin:10px 0;">
        <div id="recordingIndicator" style="width:20px;height:20px;background:red;border-radius:50%;animation:pulse 1s infinite;"></div>
        <span>Recording in progress</span>
    </div>
    <button onclick="stopRecording()" style="background:#00a884;">Stop & Send</button>
    <button onclick="cancelRecording()" style="background:#666;">Cancel</button>
</div>

<div id="callUI" class="call-ui" style="display:none">
    <div id="callInfo"></div>
    <button onclick="endCall()">End Call</button>
</div>

<script>
let log=document.getElementById('log'),uname='',seenWelcome=false,emojis={{}},stickers={{}};
let mediaRecorder, audioChunks = [], isRecording = false, currentCall = null;
let typingTimer, isTyping = false;

function avatarLetter(name){{return name?name.trim()[0].toUpperCase():"?";}}
function escapeHtml(s){{return s.replace(/[&<>"']/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}})[c]);}}

function add(m){{
    if(m.user==="system" && seenWelcome && m.type==="system") return; 
    if(m.user==="system") seenWelcome=true;
    
    let mine=(m.user===uname);
    
    if(m.type === "system") {{
        let wrap=document.createElement('div');
        wrap.className='system-msg';
        wrap.textContent = m.text;
        log.appendChild(wrap);
    }} else if(m.type === "emoji") {{
        let wrap=document.createElement('div');
        wrap.className='msg-wrap '+(mine?'me':'other');
        let av=document.createElement('div');av.className='avatar';av.textContent=avatarLetter(m.user);
        let bubble=document.createElement('div');bubble.className='bubble emoji-msg';
        bubble.innerHTML='<b>'+escapeHtml(m.user)+'</b><div style="font-size:2em;">'+m.text+'</div><div class="meta">'+new Date(m.ts).toLocaleTimeString()+'</div>';
        wrap.appendChild(av);wrap.appendChild(bubble);log.appendChild(wrap);
    }} else if(m.type === "sticker") {{
        let wrap=document.createElement('div');
        wrap.className='msg-wrap '+(mine?'me':'other');
        let av=document.createElement('div');av.className='avatar';av.textContent=avatarLetter(m.user);
        let bubble=document.createElement('div');bubble.className='bubble sticker-msg';
        bubble.innerHTML='<b>'+escapeHtml(m.user)+'</b>'+m.text+'<div class="meta">'+new Date(m.ts).toLocaleTimeString()+'</div>';
        wrap.appendChild(av);wrap.appendChild(bubble);log.appendChild(wrap);
    }} else {{
        let wrap=document.createElement('div');
        wrap.className='msg-wrap '+(mine?'me':'other');
        let av=document.createElement('div');av.className='avatar';av.textContent=avatarLetter(m.user);
        let bubble=document.createElement('div');bubble.className='bubble';
        bubble.innerHTML='<b>'+escapeHtml(m.user)+'</b><br>'+m.text+'<div class="meta">'+new Date(m.ts).toLocaleTimeString()+'</div>';
        wrap.appendChild(av);wrap.appendChild(bubble);log.appendChild(wrap);
    }}
    log.scrollTop=log.scrollHeight;
}}

// Load history and setup SSE
fetch('/history').then(r=>r.json()).then(d=>d.forEach(add));
let es=new EventSource('/stream');
es.onmessage=e=>{{try{{add(JSON.parse(e.data));}}catch{{}}}};

// Load emojis and stickers
fetch('/emojis').then(r=>r.json()).then(data=>{{emojis=data; loadEmojis();}});
fetch('/stickers').then(r=>r.json()).then(data=>{{stickers=data; loadStickers();}});

function loadEmojis(){{
    let picker = document.getElementById('emojiPicker');
    picker.innerHTML = '';
    for(let [name, emoji] of Object.entries(emojis)){{
        let emojiEl = document.createElement('div');
        emojiEl.className = 'emoji';
        emojiEl.textContent = emoji;
        emojiEl.title = name;
        emojiEl.onclick = () => {{
            sendEmoji(emoji);
            picker.style.display = 'none';
        }};
        picker.appendChild(emojiEl);
    }}
}}

function loadStickers(){{
    let picker = document.getElementById('stickerPicker');
    picker.innerHTML = '';
    for(let [name, sticker] of Object.entries(stickers)){{
        let stickerEl = document.createElement('div');
        stickerEl.className = 'sticker';
        stickerEl.textContent = sticker;
        stickerEl.title = name;
        stickerEl.onclick = () => {{
            sendSticker(sticker);
            picker.style.display = 'none';
        }};
        picker.appendChild(stickerEl);
    }}
}}

function toggleEmojiPicker(){{
    let picker = document.getElementById('emojiPicker');
    let stickerPicker = document.getElementById('stickerPicker');
    picker.style.display = picker.style.display === 'flex' ? 'none' : 'flex';
    stickerPicker.style.display = 'none';
}}

function toggleStickerPicker(){{
    let picker = document.getElementById('stickerPicker');
    let emojiPicker = document.getElementById('emojiPicker');
    picker.style.display = picker.style.display === 'flex' ? 'none' : 'flex';
    emojiPicker.style.display = 'none';
}}

function sendEmoji(emoji){{
    fetch('/send-emoji', {{
        method: 'POST',
        headers: {{'Content-Type': 'application/json'}},
        body: JSON.stringify({{
            username: uname,
            emoji: emoji
        }})
    }});
}}

function sendSticker(sticker){{
    fetch('/send-sticker', {{
        method: 'POST',
        headers: {{'Content-Type': 'application/json'}},
        body: JSON.stringify({{
            username: uname,
            sticker: sticker
        }})
    }});
}}

// Voice recording - SIMPLIFIED VERSION
async function toggleRecording(){{
    if(!isRecording){{
        try{{
            let stream = await navigator.mediaDevices.getUserMedia({{audio:true}});
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];
            
            mediaRecorder.ondataavailable = e=>{{
                audioChunks.push(e.data);
            }};
            
            mediaRecorder.onstop = ()=>{{
                let audioBlob = new Blob(audioChunks, {{type:'audio/webm'}});
                // Create a simple audio file upload
                let formData = new FormData();
                formData.append('username', uname);
                formData.append('file', audioBlob, 'voice_message.webm');
                
                fetch('/upload', {{
                    method: 'POST',
                    body: formData
                }}).then(()=>{{
                    console.log('Voice message sent');
                }});
            }};
            
            mediaRecorder.start();
            isRecording = true;
            document.getElementById('recorder').style.display = 'block';
            document.getElementById('recordBtn').textContent = '⏹️';
            document.getElementById('recordBtn').style.background = '#ff4444';
        }}catch(e){{
            alert('Microphone access denied or not available');
            console.error('Recording error:', e);
        }}
    }}else{{
        stopRecording();
    }}
}}

function stopRecording(){{
    if(mediaRecorder && isRecording){{
        mediaRecorder.stop();
        mediaRecorder.stream.getTracks().forEach(track=>track.stop());
        isRecording = false;
        document.getElementById('recorder').style.display = 'none';
        document.getElementById('recordBtn').textContent = '🎤';
        document.getElementById('recordBtn').style.background = '';
    }}
}}

function cancelRecording(){{
    if(mediaRecorder && isRecording){{
        mediaRecorder.stop();
        mediaRecorder.stream.getTracks().forEach(track=>track.stop());
        isRecording = false;
        document.getElementById('recorder').style.display = 'none';
        document.getElementById('recordBtn').textContent = '🎤';
        document.getElementById('recordBtn').style.background = '';
        audioChunks = [];
    }}
}}

// Call functionality
function toggleVoiceCall(){{
    if(!currentCall){{
        startCall('voice');
    }}else{{
        endCall();
    }}
}}

function toggleVideoCall(){{
    if(!currentCall){{
        startCall('video');
    }}else{{
        endCall();
    }}
}}

function startCall(type){{
    let callId = 'call_' + Date.now();
    currentCall = callId;
    
    fetch('/start-call', {{
        method: 'POST',
        headers: {{'Content-Type': 'application/json'}},
        body: JSON.stringify({{
            username: uname,
            callId: callId,
            callType: type
        }})
    }});
    
    document.getElementById('callUI').style.display = 'block';
    document.getElementById('callInfo').innerHTML = `${{type==='voice'?'📞':'🎥'}} ${{uname}}'s ${{type}} call`;
}}

function endCall(){{
    if(currentCall){{
        fetch('/end-call', {{
            method: 'POST',
            headers: {{'Content-Type': 'application/json'}},
            body: JSON.stringify({{
                username: uname,
                callId: currentCall
            }})
        }});
        currentCall = null;
        document.getElementById('callUI').style.display = 'none';
    }}
}}

// Form submission
document.getElementById('f').onsubmit=async e=>{{
  e.preventDefault();uname=f.username.value;
  
  if(f.file.files.length>0){{
      let fd=new FormData(f);
      await fetch('/upload',{{method:'POST',body:fd}});
  }}
  else if(f.text.value.trim()!==''){{
      let fd=new URLSearchParams();
      fd.append('username', uname);
      fd.append('text', f.text.value);
      await fetch('/send',{{method:'POST',headers:{{'Content-Type':'application/x-www-form-urlencoded'}},body:fd}});
  }}
  f.text.value='';f.file.value='';
}};

// Close pickers when clicking outside
document.addEventListener('click', (e)=>{{
    if(!e.target.closest('.picker') && !e.target.closest('.icon-btn')){{
        document.getElementById('emojiPicker').style.display = 'none';
        document.getElementById('stickerPicker').style.display = 'none';
    }}
}});

// Initialize with default username if available
window.addEventListener('load', ()=>{{
    let savedName = localStorage.getItem('chatUsername');
    if(savedName){{
        document.querySelector('input[name="username"]').value = savedName;
    }}
}});

// Save username when typing
document.querySelector('input[name="username"]').addEventListener('input', (e)=>{{
    localStorage.setItem('chatUsername', e.target.value);
}});
</script>
""".encode())

    def sse(self):
        self._set_headers(200,ctype="text/event-stream",extra={"Cache-Control":"no-cache","Connection":"keep-alive"})
        last=0; self.wfile.write(b": hi\n\n"); self.wfile.flush()
        while True:
            try:
                with msg_cond:
                    if last>=len(messages): msg_cond.wait(timeout=20)
                    new=list(messages)[last:]
                for m in new:
                    self.wfile.write(b"data: "+json.dumps(m).encode()+b"\n\n"); self.wfile.flush(); last+=1
            except: break

def run():
    init_default_assets()
    with msg_cond: messages.append({"user":"NewGen Tech","text":"Welcome to NewGen Tech Group Chat 🚀","ts":now_ms(),"type":"system"})
    httpd = socketserver.ThreadingTCPServer((HOST, PORT), ChatHandler)
    ip = local_ip()
    print(f"Local:  http://{ip}:{PORT}/")
    print("Public (if tunnel works):"); start_tunnel(PORT)
    try: httpd.serve_forever()
    except KeyboardInterrupt: pass

if __name__=="__main__": run()