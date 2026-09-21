#!/usr/bin/env python3
"""Vibes Only V11 - consolidated local-first learning assistant.

Keeps the important capabilities of the supplied V10/V9 code while removing the
repeated class stacks that made the original file unmaintainable and un-compilable.
"""
from __future__ import annotations
import argparse, ast, difflib, hashlib, ipaddress, json, math, os, random, re, secrets, socket
import statistics, threading, urllib.parse, urllib.request, sys
from collections import Counter, deque
from copy import deepcopy
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Optional

# Optional dependencies
try:
    import requests; REQUESTS_OK = True
except Exception:
    requests = None; REQUESTS_OK = False
try:
    from bs4 import BeautifulSoup; BS4_OK = True
except Exception:
    BeautifulSoup = None; BS4_OK = False
try:
    from duckduckgo_search import DDGS; DDGS_OK = True
except Exception:
    DDGS = None; DDGS_OK = False
try:
    import wikipedia; WIKI_OK = True
except Exception:
    wikipedia = None; WIKI_OK = False
try:
    import PyPDF2; PDF_OK = True
except Exception:
    PyPDF2 = None; PDF_OK = False
try:
    from youtube_transcript_api import YouTubeTranscriptApi; YT_OK = True
except Exception:
    YouTubeTranscriptApi = None; YT_OK = False
try:
    import pytesseract
    from PIL import Image as PILImage
    OCR_OK = True
except Exception:
    pytesseract = None; PILImage = None; OCR_OK = False
try:
    import pyttsx3; TTS_OK = True
except Exception:
    pyttsx3 = None; TTS_OK = False

try:
    from kivy.app import App
    from kivy.clock import Clock
    from kivy.core.clipboard import Clipboard
    from kivy.core.window import Window
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.button import Button
    from kivy.uix.floatlayout import FloatLayout
    from kivy.uix.gridlayout import GridLayout
    from kivy.uix.label import Label
    from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
    from kivy.uix.scrollview import ScrollView
    from kivy.uix.textinput import TextInput
    from kivy.graphics import Color, RoundedRectangle
    from kivy.utils import platform as KIVY_PLATFORM
    KIVY_OK = True
except Exception:
    App = object; Clock = Clipboard = Window = None
    BoxLayout = Button = FloatLayout = GridLayout = Label = object
    ScreenManager = Screen = NoTransition = ScrollView = TextInput = object
    Color = RoundedRectangle = None; KIVY_PLATFORM = "unknown"; KIVY_OK = False

APP_NAME = "Vibes Only"
VERSION = "11.0"
SCHEMA_VERSION = 11
APP_TITLE = f"{APP_NAME} V{VERSION} Unified AI"

MAX_DEFAULT = {
    "max_conversations": 700, "max_short_term_memory": 80,
    "max_facts_per_source": 160, "max_search_results": 8,
    "max_response_chars": 16000, "max_memory_items": 80000,
    "max_users": 500, "max_notifications": 700, "max_safety_events": 1000,
    "max_usage_events": 2000, "max_training_jobs": 100, "max_projects": 150,
    "max_sources": 5000, "max_feedback": 2000, "http_timeout": 15,
    "http_max_bytes": 3_000_000,
}
SETTINGS_DEFAULTS = {
    **MAX_DEFAULT,
    "memory_mode": "hybrid", "auto_web_search": True, "auto_learn_from_web": True,
    "auto_learn_from_text": True, "auto_learn_from_notes": True,
    "allow_memory_answer": True, "allow_internet_answer": True,
    "minimum_answer_chars": 100, "long_response_mode": True,
    "long_response_keywords": ["explain", "essay", "report", "research", "teach me", "in detail",
                                "compare", "why", "how", "discuss", "evaluate", "analyse", "analyze",
                                "who is", "who was", "what is", "what are", "where is", "when was"],
    "simple_query_patterns": [
        r"^(hi|hello|hey|yo|good morning|good afternoon|good evening)[!. ]*$",
        r"^(thanks|thank you|thx)[!. ]*$", r"^(ok|okay|sure|cool|nice|great)[!. ]*$",
        r"^(bye|goodbye|see you)[!. ]*$", r"^(yes|no|yeah|nah)[!. ]*$",
    ],
    "block_offensive_words": True, "protect_user_data": True,
    "never_disclose_exact_location": True, "notifications_enabled": True,
    "notify_new_user": True, "notify_learning": True, "notify_network_error": True,
    "auto_health_scan": True, "duplicate_detection": True,
    "theme_admin": "dark", "theme_user": "white", "hacker_theme_enabled": True,
    "quick_toolbar": True, "multi_user": True, "audit_hash_chain": True,
    "decoy_detection": True, "tts_enabled": False, "tts_rate": 175,
    "request_user_agent": "VibesOnly/11.0",
    "web_sources": ["duckduckgo", "wikipedia", "direct_url"],
}
KNOWLEDGE_CATEGORIES = {
    "facts":"facts.json", "definitions":"definitions.json", "explanations":"explanations.json",
    "language":"language.json", "history":"history.json", "grammar_punctuation":"grammar_punctuation.json",
    "science":"science.json", "mathematics":"mathematics.json", "geography":"geography.json",
    "technology":"technology.json", "health_education":"health_education.json", "literature":"literature.json",
    "business":"business.json", "civics":"civics.json", "ideas":"ideas.json", "notes":"notes.json",
    "web":"web.json", "general":"general.json",
}
THEMES = {
    "white": {"bg":(0.96,0.97,0.99,1),"card":(1,1,1,1),"text":(0.05,0.07,0.10,1),"muted":(0.30,0.34,0.40,1),"user":(0.02,0.30,0.75,1),"ai":(0.12,0.45,0.18,1),"accent":(0.10,0.35,0.80,1)},
    "dark": {"bg":(0.04,0.05,0.08,1),"card":(0.09,0.10,0.14,1),"text":(0.92,0.95,1,1),"muted":(0.58,0.62,0.70,1),"user":(0.10,0.75,1,1),"ai":(1,0.78,0.15,1),"accent":(0.38,0.24,0.95,1)},
    "hacker": {"bg":(0.01,0.03,0.02,1),"card":(0.02,0.07,0.03,1),"text":(0.65,1,0.68,1),"muted":(0.30,0.60,0.35,1),"user":(0.25,1,0.35,1),"ai":(0.10,0.90,0.50,1),"accent":(0,0.80,0.25,1)},
}
OFFENSIVE_TERMS = {"fuck","fucking","motherfucker","bitch","cunt","nigger","nigga","retard","faggot"}
LOCATION_PATTERNS = [r"\bmy location\b",r"\bwhere am i\b",r"\bwhere do i live\b",r"\bmy address\b",r"\bstreet address\b",r"\bgps\b",r"\bcoordinates\b",r"\bexact location\b",r"\bcurrent location\b"]
SUSPICIOUS_CYBER = [r"\bsteal (?:credentials?|passwords?|tokens?)\b",r"\bpassword dump\b",r"\bcredential stuffing\b",r"\bkeylogger\b",r"\bmalware\b",r"\bransomware\b",r"\bbackdoor\b",r"\bdisable (?:antivirus|defender|security)\b",r"\bdelete logs\b",r"\bexfiltrat(?:e|ion)\b",r"\bdata dump\b"]
PROMPT_GUIDANCE = {
    "who":"Answer identity/role first, then key facts, background and significance.",
    "what":"Give the direct definition first, then characteristics, examples and related ideas.",
    "where":"Give the place first, then relevant geographic or contextual information.",
    "when":"Give the date/period first, then surrounding historical or practical context.",
    "why":"State the main cause(s), then contributing factors, effects and uncertainty.",
    "how":"Give a clear process, steps, prerequisites and a simple example.",
    "did":"Answer the action/event directly and identify the supporting context or source when known.",
    "must":"Explain the requirement, its context, exceptions and practical consequences.",
}
COMMANDS_LIST = f"""[b]{APP_TITLE}[/b]

[b]LEARNING[/b]
teach: question | answer | category
t: question | answer
bulk: q1|a1 ## q2|a2
study: text
feed: note
siphon: text
learned
search: keyword
forget: question
review
flashcard
test: category
grade: answer1\\nanswer2...
explain: topic
example: topic
prompts
autolearn:on / autolearn:off

[b]WEB / DIGEST[/b]
web: query
source: URL
sources
digest: web|URL
digest: pdf|FILE
digest: youtube|URL
digest: image|FILE
digest: txt|FILE

[b]PROJECTS[/b]
project: Name
project_view
ideas: topic
fill: Stage 2
siphon: project text

[b]ADMIN / ENGINEERING[/b]
settings
setting: key=value
settings: reset
health
skills
duplicates
users
user:add username [role]
user:switch: username
user:delete: username
notifications
audit
safety
usage
analytics
evals
dataset
train: start
train: status
backup
export: all
reload
selftest

[b]CHAT[/b]
help / menu / about / time / summarize / clear
/name Your Name
/project Project Name
/voice
/streak
/theme white|dark|hacker
/export"""

def choose_base_dir() -> Path:
    env = os.environ.get("VIBES_DATA_DIR", "").strip()
    if env: return Path(env).expanduser().resolve()
    if KIVY_PLATFORM == "android":
        try:
            from android.storage import app_storage_path
            return Path(app_storage_path())
        except Exception: pass
    return Path.cwd().resolve()
BASE_DIR = choose_base_dir()
DATA_DIR = BASE_DIR / "vibes_v11_data"
KNOWLEDGE_DIR = DATA_DIR / "knowledge"
PERSONAL_DIR = DATA_DIR / "personal_memory"
BACKUP_DIR = DATA_DIR / "backups"
EXPORT_DIR = DATA_DIR / "exports"
LOG_DIR = DATA_DIR / "logs"
CACHE_DIR = DATA_DIR / "cache"
for d in (DATA_DIR, KNOWLEDGE_DIR, PERSONAL_DIR, BACKUP_DIR, EXPORT_DIR, LOG_DIR, CACHE_DIR): d.mkdir(parents=True, exist_ok=True)
SETTINGS_FILE=DATA_DIR/"settings.json"; USERS_FILE=DATA_DIR/"users.json"; CHAT_FILE=DATA_DIR/"chat_history.json"
CONFIG_FILE=DATA_DIR/"config.json"; PROJECTS_FILE=DATA_DIR/"projects.json"; SOURCES_FILE=DATA_DIR/"sources.json"
FEEDBACK_FILE=DATA_DIR/"feedback.json"; TRAINING_FILE=DATA_DIR/"training_jobs.json"
NOTIFICATIONS_FILE=DATA_DIR/"notifications.json"; USAGE_FILE=LOG_DIR/"usage.json"; SAFETY_FILE=LOG_DIR/"safety.json"; AUDIT_FILE=LOG_DIR/"audit_chain.json"
LEGACY = {
    "memory":[BASE_DIR/"memory.json",BASE_DIR/"vibes_only_memory.json"],
    "qanda":[BASE_DIR/"qanda.json",BASE_DIR/"VIBES_Q&A.json"],
    "chat":[BASE_DIR/"vibes_admin_chat.json",BASE_DIR/"VIBES_CHAT.json"],
}

def now_iso(): return datetime.now().isoformat(timespec="seconds")
def normalize_text(x): return re.sub(r"\s+"," ",str(x or "").replace("\x00"," ")).strip().lower()
def clean_text(x): return re.sub(r"\s+"," ",str(x or "")).strip()
def safe_text(x): return str(x or "").replace("[","[lb]").replace("]","[rb]")
def strip_markup(x): return re.sub(r"\[/?[^\]]+\]","",str(x or ""))
def stable_key(x): return hashlib.sha256(normalize_text(x).encode()).hexdigest()[:20]
def similarity(a,b): return difflib.SequenceMatcher(None,normalize_text(a),normalize_text(b)).ratio()
def cap_list(items,n): return list(items)[-max(1,int(n)):]
def safe_read_json(path, default):
    try:
        if not Path(path).exists(): return deepcopy(default)
        with Path(path).open("r",encoding="utf-8") as f: return json.load(f)
    except Exception: return deepcopy(default)
def atomic_json_write(path,data):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True); tmp=path.with_suffix(path.suffix+".tmp")
    with tmp.open("w",encoding="utf-8") as f: json.dump(data,f,indent=2,ensure_ascii=False); f.flush(); os.fsync(f.fileno())
    os.replace(tmp,path)
def is_simple_query(text,settings):
    low=normalize_text(text)
    return any(re.match(p,low) for p in settings.get("simple_query_patterns",[]))
def human_bytes(n):
    v=float(n)
    for u in ("B","KB","MB","GB"):
        if v<1024 or u=="GB": return f"{v:.1f} {u}"
        v/=1024

def safe_url(url):
    try:
        p=urllib.parse.urlparse(url.strip())
        if p.scheme.lower() not in {"http","https"} or not p.hostname: return False,"Only valid HTTP/HTTPS URLs are supported."
        host=p.hostname.lower().rstrip(".")
        if host in {"localhost","localhost.localdomain"}: return False,"Local targets are blocked."
        try:
            infos=socket.getaddrinfo(host,None)
            for info in infos:
                ip=ipaddress.ip_address(info[4][0])
                if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_reserved: return False,"Private/local targets are blocked."
        except OSError: pass
        return True,""
    except Exception: return False,"Invalid URL."

class SafeMath:
    BIN={ast.Add:lambda a,b:a+b,ast.Sub:lambda a,b:a-b,ast.Mult:lambda a,b:a*b,ast.Div:lambda a,b:a/b,ast.FloorDiv:lambda a,b:a//b,ast.Mod:lambda a,b:a%b,ast.Pow:lambda a,b:a**b}
    UN={ast.UAdd:lambda x:+x,ast.USub:lambda x:-x}
    N={"pi":math.pi,"e":math.e,"sqrt":math.sqrt,"sin":math.sin,"cos":math.cos,"tan":math.tan,"log":math.log,"log10":math.log10,"abs":abs,"round":round}
    @classmethod
    def eval(cls,s):
        s=str(s).strip().replace("×","*").replace("÷","/").replace("^","**")
        if len(s)>120: raise ValueError("expression too long")
        return cls._node(ast.parse(s,mode="eval").body)
    @classmethod
    def _node(cls,n):
        if isinstance(n,ast.Constant) and isinstance(n.value,(int,float)): return n.value
        if isinstance(n,ast.Name) and n.id in cls.N: return cls.N[n.id]
        if isinstance(n,ast.UnaryOp) and type(n.op) in cls.UN: return cls.UN[type(n.op)](cls._node(n.operand))
        if isinstance(n,ast.BinOp) and type(n.op) in cls.BIN:
            r=cls._node(n.right); l=cls._node(n.left)
            if isinstance(n.op,ast.Pow) and abs(float(r))>20: raise ValueError("exponent too large")
            return cls.BIN[type(n.op)](l,r)
        if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id in cls.N:
            return cls.N[n.func.id](*[cls._node(x) for x in n.args])
        raise ValueError("unsupported expression")
    @classmethod
    def evaluate(cls,s):
        try:
            value=cls.eval(s)
            if isinstance(value,float) and value.is_integer(): value=int(value)
            return str(value)
        except Exception as e:
            return f"Calculation error: {e}"
    @classmethod
    def looks(cls,s):
        s=str(s).strip().replace("×","*").replace("÷","/")
        return len(s)<=120 and any(c.isdigit() for c in s) and bool(re.fullmatch(r"[0-9A-Za-z_\s+\-*/^().,%]+",s))

class Settings:
    def __init__(self):
        d=safe_read_json(SETTINGS_FILE,{})
        self.data=deepcopy(SETTINGS_DEFAULTS)
        if isinstance(d,dict): self.data.update(d)
        self.data["schema_version"]=SCHEMA_VERSION; self.save()
    def save(self): atomic_json_write(SETTINGS_FILE,self.data)
    def reset(self): self.data=deepcopy(SETTINGS_DEFAULTS); self.data["schema_version"]=SCHEMA_VERSION; self.save(); return "Settings reset to V11 defaults."
    def set(self,key,val):
        if key not in self.data: return f"Unknown setting: {key}"
        old=self.data[key]; raw=str(val).strip()
        if isinstance(old,bool):
            if raw.lower() not in {"1","0","true","false","yes","no","on","off"}: return "Invalid boolean."
            v=raw.lower() in {"1","true","yes","on"}
        elif isinstance(old,int) and not isinstance(old,bool):
            try:v=max(1,int(raw))
            except Exception:return "Invalid integer."
        elif isinstance(old,list):v=[x.strip() for x in raw.split(",") if x.strip()]
        else:v=raw
        self.data[key]=v; self.save(); return f"Setting updated: {key} = {v}"
    def get(self,key,default=None): return self.data.get(key,default)
    def __getitem__(self,key): return self.data[key]
    def set_value_text(self,text):
        raw=str(text).strip()
        if "=" not in raw: return "Format: setting: key=value"
        key,val=[x.strip() for x in raw.split("=",1)]
        return self.set(key,val)
    def render(self):
        keys=["memory_mode","auto_web_search","auto_learn_from_web","auto_learn_from_text","auto_learn_from_notes","allow_memory_answer","allow_internet_answer","minimum_answer_chars","long_response_mode","protect_user_data","never_disclose_exact_location","theme_admin","theme_user","multi_user","audit_hash_chain","tts_enabled"]
        return "[b]V11 SETTINGS[/b]\n"+"\n".join(f"{k}: {self.data.get(k)}" for k in keys)

class Notifications:
    def __init__(self,settings): self.settings=settings; self.items=safe_read_json(NOTIFICATIONS_FILE,[]); self._lock=threading.RLock()
    def push(self,kind,msg):
        if not self.settings.get("notifications_enabled",True): return
        with self._lock:
            self.items.append({"id":secrets.token_hex(8),"time":now_iso(),"kind":kind,"message":clean_text(msg)[:1000],"read":False})
            self.items=cap_list(self.items,self.settings["max_notifications"]); atomic_json_write(NOTIFICATIONS_FILE,self.items)
    def render(self):
        if not self.items:return "Notifications: none."
        return "[b]NOTIFICATIONS[/b]\n"+"\n".join(f"{'✓' if x.get('read') else '•'} {x.get('time')} | {x.get('kind')} | {safe_text(x.get('message'))}" for x in reversed(self.items[-25:]))

class Security:
    def __init__(self,settings,notifier):
        self.settings=settings; self.notifier=notifier; self.safety=safe_read_json(SAFETY_FILE,[]); self.audit=safe_read_json(AUDIT_FILE,[]); self._lock=threading.RLock()
    def sanitize(self,text):
        if not self.settings.get("block_offensive_words",True): return str(text or "")
        if not OFFENSIVE_TERMS:return str(text or "")
        pat=re.compile(r"(?i)\b("+"|".join(re.escape(x) for x in OFFENSIVE_TERMS)+r")\b")
        return pat.sub(lambda m:"*"*len(m.group(0)),str(text or ""))
    def is_location_request(self,text): return any(re.search(p,normalize_text(text)) for p in LOCATION_PATTERNS)
    def detect_suspicious(self,text): return self.suspicious(text)
    def suspicious(self,text):
        low=normalize_text(text); hit=any(re.search(p,low) for p in SUSPICIOUS_CYBER)
        if hit:self.log_safety("suspicious_request",low[:800])
        return hit
    def privacy(self,user_text,response):
        if self.settings.get("never_disclose_exact_location",True) and any(re.search(p,normalize_text(user_text)) for p in LOCATION_PATTERNS):
            return "I can't provide exact location, address, GPS or coordinate information. I can help with general geographic information instead."
        r=str(response)
        if self.settings.get("protect_user_data",True):
            for p in [r"(?i)\b(password|passcode|private key|secret token|api[_ -]?key)\s*[:=]\s*\S+",r"(?i)\bbearer\s+[A-Za-z0-9._-]+"]:
                r=re.sub(p,lambda m:re.sub(r"\S+$","[REDACTED]",m.group(0)),r)
        return self.sanitize(r)
    def guard(self,user_text,response): return self.privacy(user_text,response)
    def log_safety(self,typ,content):
        with self._lock:
            self.safety.append({"time":now_iso(),"type":typ,"content":str(content)[:1000]}); self.safety=cap_list(self.safety,self.settings["max_safety_events"]); atomic_json_write(SAFETY_FILE,self.safety)
    def _hash(self,e,prev):
        stable={"time":e.get("time",""),"action":e.get("action",""),"actor":e.get("actor",""),"details":e.get("details","")}
        return hashlib.sha256(json.dumps({"event":stable,"previous_hash":prev},sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    def audit_event(self,action,actor,details):
        if not self.settings.get("audit_hash_chain",True):return
        with self._lock:
            e={"time":now_iso(),"action":str(action),"actor":str(actor),"details":str(details)[:1500]}; prev=self.audit[-1].get("hash","GENESIS") if self.audit else "GENESIS"; e["previous_hash"]=prev; e["hash"]=self._hash(e,prev); self.audit.append(e); self.audit=cap_list(self.audit,self.settings["max_usage_events"]); atomic_json_write(AUDIT_FILE,self.audit)
    def verify(self):
        prev="GENESIS"; bad=[]
        for i,e in enumerate(self.audit):
            if e.get("previous_hash")!=prev or e.get("hash")!=self._hash(e,prev):bad.append(i)
            prev=e.get("hash","")
        return {"valid":not bad,"checked":len(self.audit),"bad_indexes":bad}
    def show_audit(self):
        r=self.verify(); return f"[b]AUDIT CHAIN[/b]\nEntries: {r['checked']}\nIntegrity: {'VALID' if r['valid'] else 'BROKEN'}\nBad indexes: {r['bad_indexes'][:20]}"
    def show_safety(self):
        if not self.safety:return "Safety Center: no events."
        return "[b]SAFETY CENTER[/b]\n"+"\n".join(f"{x.get('time')} | {x.get('type')} | {safe_text(x.get('content'))}" for x in self.safety[-30:])

class Users:
    def __init__(self,settings,notifications,security):
        self.settings=settings; self.notifications=notifications; self.security=security; self.data=safe_read_json(USERS_FILE,{}); self.data=self.data if isinstance(self.data,dict) else {}
        self.data.setdefault("admin",{"role":"admin","created":now_iso(),"last_seen":now_iso(),"theme":settings.get("theme_admin","dark"),"current_project":"Current Project"}); self.current="admin"; self.save()
    @property
    def role(self):return self.data.get(self.current,{}).get("role","user")
    def save(self):
        atomic_json_write(USERS_FILE,self.data)
    def add(self,name,role="user"):
        name=re.sub(r"[^A-Za-z0-9_.-]","_",str(name).strip())[:48]
        if not name:return "Username cannot be empty."
        if name in self.data:self.current=name; self.data[name]["last_seen"]=now_iso(); self.save(); return f"User already exists. Switched to {name}."
        role=role if role in {"user","engineer","admin"} else "user"; self.data[name]={"role":role,"created":now_iso(),"last_seen":now_iso(),"theme":self.settings.get("theme_user","white"),"current_project":"Current Project"}; self.current=name; self.save(); self.notifications.push("new_user",f"New user created: {name}"); self.security.audit_event("user_create",name,role); return f"Created and signed in user: {name}"
    def switch(self,name):
        if name not in self.data:return f"Unknown user: {name}"
        self.current=name; self.data[name]["last_seen"]=now_iso(); self.save(); self.security.audit_event("user_switch",name,"active namespace changed"); return f"Switched to user: {name}"
    def delete(self,name):
        if name=="admin":return "Admin cannot be deleted."
        if name not in self.data:return "User not found."
        del self.data[name]; self.current="admin" if self.current==name else self.current; self.save(); self.security.audit_event("user_delete","admin",name); return f"Deleted user: {name}"
    def render(self):
        return "[b]USERS[/b]\n"+"\n".join(f"{n} | role={x.get('role')} | theme={x.get('theme')} | project={x.get('current_project','Current Project')} {'← current' if n==self.current else ''}" for n,x in self.data.items())

class Store:
    RULES=[
        ("grammar_punctuation",["grammar","punctuation","sentence","verb","noun","adjective","comma","full stop"]),
        ("definitions",["definition","define","meaning of","what is","what are","what does"]),
        ("explanations",["explain","explanation","why","how does","how do","reason"]),
        ("language",["synonym","antonym","vocabulary","english","word","translation"]),
        ("history",["history","war","empire","independence","ancient","colonial","revolution"]),
        ("science",["science","physics","chemistry","biology","atom","energy","cell","plant","animal"]),
        ("mathematics",["math","mathematics","equation","algebra","geometry","fraction","calculate","percent"]),
        ("geography",["geography","country","capital","river","mountain","climate","continent","population"]),
        ("technology",["computer","software","ai","artificial intelligence","technology","python","programming","internet","code"]),
        ("health_education",["health","nutrition","hygiene","disease","exercise","medicine","body"]),
        ("literature",["story","poem","novel","character","metaphor","simile","literature","proverb","folktale"]),
        ("business",["business","marketing","profit","company","finance","money","economy","entrepreneur"]),
        ("civics",["government","citizen","law","rights","civics","election","constitution"]),
        ("ideas",["idea","project","upgrade","plan","concept","solution"]),
        ("notes",["note","notes","journal"]),
    ]
    def __init__(self,settings,security,notifications,users):
        self.settings=settings; self.security=security; self.notifications=notifications; self.users=users; self._lock=threading.RLock()
        self.categories={c:(safe_read_json(KNOWLEDGE_DIR/f,{}) if isinstance(safe_read_json(KNOWLEDGE_DIR/f,{}),dict) else {}) for c,f in KNOWLEDGE_CATEGORIES.items()}
        self.global_memory=safe_read_json(DATA_DIR/"global_memory.json",{}); self.global_memory=self.global_memory if isinstance(self.global_memory,dict) else {}
        self.global_qanda=safe_read_json(DATA_DIR/"global_qanda.json",{"cards":{},"categories":{}}); self.global_qanda=self.global_qanda if isinstance(self.global_qanda,dict) else {"cards":{},"categories":{}}
        self.global_qanda.setdefault("cards",{}); self.global_qanda.setdefault("categories",{})
        self.notes=safe_read_json(DATA_DIR/"notes.json",[]); self.notes=self.notes if isinstance(self.notes,list) else []
        self.conversations=safe_read_json(CHAT_FILE,[]); self.conversations=self.conversations if isinstance(self.conversations,list) else []
        self.active_user="admin"; self.personal_memory={}; self.personal_qanda={}; self.personal_notes=[]; self.tests=[]; self.short_term=deque(maxlen=settings["max_short_term_memory"])
        self.set_active_user("admin"); self.migrate_legacy(); self.save_all()
    @property
    def memory(self): return self.global_memory
    @property
    def qanda(self): return self.global_qanda
    def user_file(self,user=None): return PERSONAL_DIR/f"{stable_key(user or self.active_user)}.json"
    def set_active_user(self,user):
        self.active_user=user or "admin"; d=safe_read_json(self.user_file(),{"memory":{},"qanda":{},"notes":[]}); d=d if isinstance(d,dict) else {}
        self.personal_memory=d.get("memory",{}) if isinstance(d.get("memory"),dict) else {}; self.personal_qanda=d.get("qanda",{}) if isinstance(d.get("qanda"),dict) else {}; self.personal_notes=d.get("notes",[]) if isinstance(d.get("notes"),list) else []
    def save_personal(self): atomic_json_write(self.user_file(),{"schema_version":SCHEMA_VERSION,"user":self.active_user,"memory":self.personal_memory,"qanda":self.personal_qanda,"notes":cap_list(self.personal_notes,self.settings["max_memory_items"]),"updated":now_iso()})
    def _cap(self):
        n=self.settings["max_memory_items"]; self.global_memory=dict(list(self.global_memory.items())[-n:]); self.global_qanda["cards"]=dict(list(self.global_qanda["cards"].items())[-n:]); self.categories={k:dict(list(v.items())[-n:]) for k,v in self.categories.items()}; self.personal_memory=dict(list(self.personal_memory.items())[-n:]); self.personal_qanda=dict(list(self.personal_qanda.items())[-n:]); self.notes=cap_list(self.notes,n); self.personal_notes=cap_list(self.personal_notes,n); self.conversations=cap_list(self.conversations,self.settings["max_conversations"])
    def save_all(self):
        with self._lock:
            self._cap()
            for c,f in KNOWLEDGE_CATEGORIES.items(): atomic_json_write(KNOWLEDGE_DIR/f,self.categories[c])
            atomic_json_write(DATA_DIR/"global_memory.json",self.global_memory); atomic_json_write(DATA_DIR/"global_qanda.json",self.global_qanda); atomic_json_write(DATA_DIR/"notes.json",self.notes); atomic_json_write(CHAT_FILE,self.conversations); self.save_personal()
    def migrate_legacy(self):
        imported=0
        for p in LEGACY["memory"]:
            if p.exists():
                d=safe_read_json(p,{}); d=d if isinstance(d,dict) else {}; bucket=d.get("memory",d.get("teachings",d))
                if isinstance(bucket,dict):
                    for k,v in bucket.items():
                        a=v.get("answer",v.get("text","")) if isinstance(v,dict) else str(v)
                        if a:self.teach_memory(k,a,private=True,notify=False,source=f"legacy:{p.name}"); imported+=1
                break
        for p in LEGACY["qanda"]:
            if p.exists():
                d=safe_read_json(p,{}); d=d if isinstance(d,dict) else {}; bucket=d.get("cards",d.get("memory",d))
                if isinstance(bucket,dict):
                    for k,v in bucket.items():
                        a=v.get("answer",v.get("text","")) if isinstance(v,dict) else str(v)
                        if a:self.teach_qa(k,a,private=True,notify=False,source=f"legacy:{p.name}"); imported+=1
                break
        for p in LEGACY["chat"]:
            if p.exists():
                d=safe_read_json(p,[])
                if isinstance(d,list): self.conversations.extend(d[-self.settings["max_conversations"]:])
                break
        if imported:self.notifications.push("learning",f"Imported {imported} legacy items into V11.")
    def classify(self,text,hint=None):
        if hint:
            h=normalize_text(hint).replace(" ","_")
            if h in self.categories:return h
        low=normalize_text(text); scores=Counter()
        for cat,words in self.RULES:
            for w in words:
                if w in low:scores[cat]+=2 if " " in w else 1
        return scores.most_common(1)[0][0] if scores else "facts"
    def extract_pairs(self,text,forced=None):
        raw=str(text or ""); out=[]; seen=set()
        def add(q,a,c=None):
            q=clean_text(q); a=clean_text(a); sig=(normalize_text(q),normalize_text(a))
            if q and a and sig not in seen: out.append((q,a,c)); seen.add(sig)
        for pat in [r"(?ims)^\s*Q(?:uestion)?\s*[:\-]\s*(.*?)\s*A(?:nswer)?\s*[:\-]\s*(.*?)(?=^\s*Q(?:uestion)?\s*[:\-]|\Z)"]:
            for m in re.finditer(pat,raw): add(m.group(1),m.group(2),forced)
        for line in raw.splitlines():
            s=line.strip()
            if not s or s.startswith(("http://","https://")):continue
            if ":" in s:
                q,a=[clean_text(x) for x in s.split(":",1)]
                if 2<=len(q)<=160 and 2<=len(a)<=1500: add(q,a,forced or self.classify(q+" "+a))
            if "|" in s:
                cells=[clean_text(x) for x in s.strip("|").split("|")]
                if len(cells)==2 and all(cells) and 2<=len(cells[0])<=160: add(cells[0],cells[1],forced or self.classify(s))
        # Markdown table blocks
        table_lines=[x.strip() for x in raw.splitlines() if "|" in x]
        has_table_separator=any(re.search(r"\|\s*:?-{2,}",line) for line in table_lines)
        if has_table_separator:
            seen_pipe=set((normalize_text(a),normalize_text(b)) for a,b,_ in out)
            for i,line in enumerate(table_lines):
                cells=[clean_text(x) for x in line.strip("|").split("|")]
                if i==0 or len(cells)<2 or not all(cells): continue
                if all(set(c.replace(":","")) <= set("-") for c in cells): continue
                qv=cells[0]; av=" — ".join(cells[1:]); sig=(normalize_text(qv),normalize_text(av))
                if sig not in seen_pipe: add(qv,av,forced or self.classify(line)); seen_pipe.add(sig)
        lines=[clean_text(x) for x in raw.splitlines() if clean_text(x)]
        for i,line in enumerate(lines[:-1]):
            if re.match(r"(?i)^what (?:is|are)\s+.+\??$",line): add(line,lines[i+1],forced or "definitions")
        for m in re.finditer(r"(?im)^\s*(?:def(?:inition)?|meaning)\s*[:\-]\s*(.+?)(?:\s*\|\s*|\n\s+)(.+)$",raw): add(m.group(1),m.group(2),forced or "definitions")
        return out
    def extract_sentences(self,text,category=None,source="text"):
        clean=re.sub(r"```.*?```"," ",str(text or ""),flags=re.S); clean=re.sub(r"\s+"," ",clean).strip(); out=[]; seen=set()
        for s in re.split(r"(?<=[.!?])\s+",clean):
            s=clean_text(s)
            if len(s)<35:continue
            k=stable_key(s[:1800])
            if k in seen:continue
            seen.add(k); out.append({"id":k,"text":s[:1800],"category":self.classify(s,category),"source":source,"created":now_iso()})
            if len(out)>=self.settings["max_facts_per_source"]:break
        return out
    def _save_item(self,item,source):
        text=clean_text(item.get("text",""));
        if not text:return
        cat=self.classify(text,item.get("category")); k=item.get("id") or stable_key(text); payload={"text":text,"category":cat,"source":source,"created":item.get("created",now_iso()),"updated":now_iso()}; self.categories[cat][k]=payload; self.global_memory["fact:"+k]={"answer":text,"category":cat,"source":source,"created":payload["created"],"updated":payload["updated"],"confidence":55,"times_asked":0}
    def ingest(self,text,source="text",category=None,private=False):
        safe=self.security.sanitize(text); pairs=self.extract_pairs(safe,category); qa=0; seen=set()
        for q,a,c in pairs:
            sig=(normalize_text(q),normalize_text(a))
            if sig in seen:continue
            seen.add(sig); self.teach_qa(q,a,c,private=private,notify=False,source=source); qa+=1
        facts=self.extract_sentences(safe,category,source); [self._save_item(x,source) for x in facts]; self.save_all(); n=len(facts)
        if qa or n:self.notifications.push("learning",f"Learned {qa} Q&A + {n} knowledge items.")
        return {"qa":qa,"knowledge":n}
    def teach_text(self,raw):
        text=str(raw or "")
        if ":" not in text: return "Format: teach: question | answer | category"
        data=text.split(":",1)[1].strip()
        parts=[x.strip() for x in data.split("|",2)]
        if len(parts)<2:return "Format: teach: question | answer | category"
        return self.teach_qa(parts[0],parts[1],parts[2] if len(parts)>2 else None)
    def bulk_text(self,raw):
        if ":" not in raw:return "Format: bulk: q1|a1 ## q2|a2"
        count=0
        for pair in raw.split(":",1)[1].split("##"):
            if "|" not in pair: continue
            q,a=pair.split("|",1)
            if clean_text(q) and clean_text(a): self.teach_qa(q,a,notify=False); count+=1
        if count:self.notifications.push("learning",f"Bulk learning added {count} Q&A cards.")
        return f"Bulk added {count} Q&A cards."
    def siphon(self,text,category=None,source="text"):
        r=self.ingest(text,source,category); return f"Siphoned {r['qa']} Q&A + {r['knowledge']} categorized knowledge items."
    def teach_memory(self,key,value,category=None,private=True,notify=True,source="manual"):
        k=normalize_text(key); v=clean_text(value)
        if not k or not v:return "Question/key and answer cannot be empty."
        item={"answer":v,"category":self.classify(k+" "+v,category),"source":source,"created":now_iso(),"updated":now_iso(),"confidence":60,"times_asked":0}
        (self.personal_memory if private else self.global_memory)[k]=item; self.save_all()
        if notify:self.notifications.push("learning",f"Learned memory in {item['category']}: {k[:80]}")
        return f"Learned memory: {k} [{item['category']}]"
    def teach_qa(self,key,value,category=None,private=True,notify=True,source="manual"):
        k=normalize_text(key); v=clean_text(value)
        if not k or not v:return "Question and answer cannot be empty."
        card={"answer":v,"category":self.classify(k+" "+v,category),"confidence":60,"times_asked":0,"wrong":0,"source":source,"created":now_iso(),"updated":now_iso()}
        if private:self.personal_qanda[k]=card
        else:self.global_qanda["cards"][k]=card
        self.save_all()
        if notify:self.notifications.push("learning",f"Learned Q&A in {card['category']}: {k[:80]}")
        return f"Learned Q&A: {k} [{card['category']}]"
    def all_items(self):
        out=[]
        for scope,bucket in [("private_qanda",self.personal_qanda),("private_memory",self.personal_memory),("global_qanda",self.global_qanda["cards"]),("global_memory",self.global_memory)]:
            for k,v in bucket.items():
                if isinstance(v,dict):out.append((k,scope,v,str(v.get("answer",v.get("text","")))))
        for cat,bucket in self.categories.items():
            for k,v in bucket.items():
                if isinstance(v,dict):out.append((k,cat,v,str(v.get("text",""))))
        return out
    def search_all(self,query,limit=8):
        q=normalize_text(query); ranked=[]
        for k,scope,item,ans in self.all_items():
            kn=normalize_text(k); an=normalize_text(ans); score=max(1.0 if q==kn else 0,0.9 if q in kn else 0,0.6 if q in an else 0,similarity(q,kn)*.75,similarity(q,an[:1000])*.45)
            if scope.startswith("private"):score+=.05
            if item.get("category")=="definitions":score+=.03
            if score>=.44:ranked.append((score,int(item.get("confidence",50)),{"key":k,"scope":scope,"item":item,"answer":ans,"score":round(score,4)}))
        ranked.sort(key=lambda x:(x[0],x[1]),reverse=True); out=[]; seen=set()
        for _,_,x in ranked:
            sig=normalize_text(x["answer"])
            if sig in seen or not sig:continue
            seen.add(sig); out.append(x)
            if len(out)>=limit:break
        return out
    def recall(self,query):
        m=self.search_all(query,5)
        if not m:return None
        x=m[0]; x["item"]["times_asked"]=int(x["item"].get("times_asked",0))+1; self.save_all(); return x
    def search_memory(self,query):
        m=self.search_all(query,15)
        if not m:return "No memory matches."
        return "[b]MEMORY SEARCH — ALL BUCKETS[/b]\n"+"\n".join(f"• {x['key'][:90]} | {x['scope']} | {x['score']} | {clean_text(x['answer'])[:220]}" for x in m)
    def forget(self,key):
        q=normalize_text(key); removed=0
        for bucket in (self.personal_memory,self.personal_qanda,self.global_memory,self.global_qanda["cards"]):
            for k in list(bucket):
                if k==q or q in k or k in q: del bucket[k]; removed+=1
        self.save_all(); return f"Removed {removed} matching memory item(s)." if removed else "No matching memory item found."
    def stats(self):
        cats=sum(len(v) for v in self.categories.values()); cards=[v for v in list(self.personal_qanda.values())+list(self.global_qanda["cards"].values()) if isinstance(v,dict)]; conf=[int(x.get("confidence",60)) for x in cards]
        avg=round(statistics.mean(conf),1) if conf else 0
        return f"[b]V11 MEMORY STATS[/b]\nKnowledge items: {cats}\nGlobal memory: {len(self.global_memory)}\nPrivate memory: {len(self.personal_memory)}\nGlobal Q&A: {len(self.global_qanda['cards'])}\nPrivate Q&A: {len(self.personal_qanda)}\nNotes: {len(self.personal_notes)}\nConversations: {len(self.conversations)}\nAverage confidence: {avg}%"
    def brain_scan(self):
        populated=", ".join(f"{k}={len(v)}" for k,v in self.categories.items() if v) or "empty"
        return f"[b]V11 KNOWLEDGE BRAIN[/b]\nMemory={len(self.global_memory)} | Q&A={len(self.global_qanda['cards'])} | Private={len(self.personal_memory)+len(self.personal_qanda)}\nCategories: {populated}"
    def feed_note(self,note):
        v=clean_text(note)
        if not v:return "Note cannot be empty."
        e={"time":now_iso(),"note":v,"user":self.active_user}; self.personal_notes.append(e); self.notes.append(e); self.teach_memory("note:"+stable_key(v),v,"notes",True,False,"note"); self.ingest(v,"note","notes",private=True); return "Note saved and learned into notes/knowledge."
    def render_notes(self):
        if not self.personal_notes:return "No notes yet."
        return f"[b]YOUR NOTES — {safe_text(self.active_user)}[/b]\n"+"\n".join(f"{i+1}. {x.get('time')} — {safe_text(x.get('note'))}" for i,x in enumerate(reversed(self.personal_notes[-25:])))
    def clear_conversations(self):self.conversations=[]; atomic_json_write(CHAT_FILE,self.conversations); return "Chat history cleared."
    def summarize(self):
        if not self.conversations:return "No conversations yet."
        return "[b]RECENT EXCHANGES[/b]\n\n"+"\n\n".join(f"You: {safe_text(str(x.get('user',''))[:250])}\nAI: {strip_markup(str(x.get('ai','')))[:450]}" for x in self.conversations[-6:])
    def import_pack(self,filename):
        path=Path(str(filename).strip()).expanduser()
        if not path.exists():return f"File not found: {path}"
        pack=safe_read_json(path,None)
        if pack is None:return "Invalid JSON pack."
        count=0
        if isinstance(pack,dict):
            mem=pack.get("memory",pack.get("global_memory",pack.get("teachings",{})))
            if isinstance(mem,dict):
                for k,v in mem.items():
                    a=v.get("answer",v.get("text","")) if isinstance(v,dict) else str(v)
                    if a:self.teach_memory(k,a,v.get("category") if isinstance(v,dict) else None,private=True,notify=False,source=f"import:{path.name}");count+=1
            cards=pack.get("qanda",pack.get("cards",pack.get("global_qanda",{})))
            if isinstance(cards,dict) and "cards" in cards:cards=cards.get("cards",{})
            if isinstance(cards,dict):
                for k,v in cards.items():
                    a=v.get("answer",v.get("text","")) if isinstance(v,dict) else str(v)
                    if a:self.teach_qa(k,a,v.get("category") if isinstance(v,dict) else None,private=True,notify=False,source=f"import:{path.name}");count+=1
        elif isinstance(pack,list):
            for item in pack:
                if not isinstance(item,dict):continue
                q=item.get("question",item.get("q",""));a=item.get("answer",item.get("a",""))
                if q and a:self.teach_qa(q,a,item.get("category"),private=True,notify=False,source=f"import:{path.name}");count+=1
        self.save_all();self.notifications.push("learning",f"Imported {count} items from {path.name}.");return f"Imported {count} items from {path.name}."
    def clear_notes(self):
        removed=len(self.personal_notes);self.personal_notes=[];self.notes=[x for x in self.notes if x.get("user")!=self.active_user];self.save_all();return f"Cleared {removed} note(s)."
    def export_all(self):
        p=EXPORT_DIR/f"vibes_v11_{self.active_user}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"; atomic_json_write(p,{"schema_version":SCHEMA_VERSION,"version":VERSION,"user":self.active_user,"global_memory":self.global_memory,"global_qanda":self.global_qanda,"private_memory":self.personal_memory,"private_qanda":self.personal_qanda,"categories":self.categories,"notes":self.personal_notes}); return p
    def spaced_review(self):
        cards={**self.global_qanda["cards"],**self.personal_qanda}
        if not cards:return "No Q&A cards."
        rows=[]
        for q,c in cards.items():rows.append(((100-int(c.get("confidence",60)))+int(c.get("wrong",0))*6,q))
        rows.sort(reverse=True); return "[b]REVIEW QUEUE[/b]\n"+"\n".join(f"• {q}" for _,q in rows[:15])
    def flashcard(self):
        cards=list(dict.fromkeys(list(self.personal_qanda)+list(self.global_qanda["cards"])))
        if not cards:return "No flashcards yet."
        q=random.choice(cards); c=self.personal_qanda.get(q) or self.global_qanda["cards"].get(q,{}); return f"[b]FLASHCARD[/b]\n\nQ: {q}\nA: {c.get('answer','')}"
    def test(self,category=None):
        cards=[]
        for q,c in list(self.personal_qanda.items())+list(self.global_qanda["cards"].items()):
            if category is None or category=="general" or c.get("category")==normalize_text(category):cards.append(q)
        cards=list(dict.fromkeys(cards))
        if len(cards)<3:return "Need at least 3 Q&A cards first."
        self.tests=random.sample(cards,min(5,len(cards))); return "[b]REVISION TEST[/b]\n"+"\n".join(f"{i+1}. {q}" for i,q in enumerate(self.tests))+"\n\nUse: grade: answer1\\nanswer2..."
    def grade(self,raw):
        if not self.tests:return "No test is active. Use test first."
        ans=[clean_text(x) for x in str(raw).splitlines() if clean_text(x)]; score=0; lines=["[b]REPORT CARD[/b]"]
        for i,q in enumerate(self.tests):
            c=self.personal_qanda.get(q) or self.global_qanda["cards"].get(q,{}) ; correct=str(c.get("answer","")); student=ans[i] if i<len(ans) else ""; ratio=similarity(correct,student); ok=ratio>=.62
            if ok:score+=1;c["confidence"]=min(100,int(c.get("confidence",60))+8); res="Correct ✅"
            else:c["wrong"]=int(c.get("wrong",0))+1;c["confidence"]=max(10,int(c.get("confidence",60))-6);res="Review ❌"
            c["times_asked"]=int(c.get("times_asked",0))+1; lines.append(f"{i+1}. {res}\nQ: {q}\nKey: {correct}\nYou: {student}")
        total=len(self.tests); self.tests=[]; self.save_all(); lines.append(f"\nScore: {score}/{total}"); return "\n".join(lines)
    def find_duplicates(self):
        arr=[]
        for scope,b in [("private_qanda",self.personal_qanda),("private_memory",self.personal_memory),("global_qanda",self.global_qanda["cards"]),("global_memory",self.global_memory)]:
            for k,v in list(b.items())[-2500:]:
                if isinstance(v,dict):arr.append((scope,k,str(v.get("answer",v.get("text","")))))
        dup=[]
        for i in range(len(arr)):
            for j in range(i+1,len(arr)):
                if arr[i][1]==arr[j][1] or similarity(arr[i][2],arr[j][2])>=.97:dup.append((arr[i],arr[j]))
                if len(dup)>=50:break
            if len(dup)>=50:break
        if not dup:return "Duplicate finder: no high-confidence duplicates found."
        return "[b]DUPLICATES[/b]\n"+"\n".join(f"• {a[0]}:{a[1][:60]} ↔ {b[0]}:{b[1][:60]}" for a,b in dup)

class Web:
    def __init__(self,settings,store,security,notifications):
        self.settings=settings; self.store=store; self.security=security; self.notifications=notifications; self.cache=safe_read_json(DATA_DIR/"search_cache.json",{}); self.sources=safe_read_json(SOURCES_FILE,[])
    def save(self):self.cache=dict(list(self.cache.items())[-1000:]);self.sources=cap_list(self.sources,self.settings["max_sources"]);atomic_json_write(DATA_DIR/"search_cache.json",self.cache);atomic_json_write(SOURCES_FILE,self.sources)
    def _ddg(self,q):
        if not DDGS_OK:return []
        try:
            with DDGS() as d: raw=d.text(q,max_results=self.settings["max_search_results"]); return [{"title":str(x.get("title","")),"href":str(x.get("href",x.get("url",""))),"body":str(x.get("body",x.get("snippet","")))} for x in raw if isinstance(x,dict)]
        except Exception as e:self.notifications.push("network_error",f"Search failed: {type(e).__name__}");return []
    def _wiki(self,q):
        if not WIKI_OK:return []
        try:
            p=wikipedia.page(q,auto_suggest=True,redirect=True);return [{"title":p.title,"href":p.url,"body":p.summary[:3000]}]
        except Exception:return []
    def fetch(self,url):
        ok,msg=safe_url(url)
        if not ok:raise ValueError(msg)
        timeout=int(self.settings["http_timeout"]);limit=int(self.settings["http_max_bytes"]);headers={"User-Agent":self.settings["request_user_agent"]}
        if REQUESTS_OK:
            current=url
            for _ in range(4):
                ok,msg=safe_url(current)
                if not ok:raise ValueError(msg)
                r=requests.get(current,headers=headers,timeout=timeout,stream=True,allow_redirects=False)
                if 300 <= r.status_code < 400 and r.headers.get("Location"):
                    current=urllib.parse.urljoin(current,r.headers["Location"]); continue
                r.raise_for_status();data=bytearray()
                for c in r.iter_content(65536):
                    if c:data.extend(c)
                    if len(data)>=limit:break
                return bytes(data[:limit]).decode(r.encoding or "utf-8",errors="ignore")
            raise ValueError("Too many redirects")
        req=urllib.request.Request(url,headers=headers)
        with urllib.request.urlopen(req,timeout=timeout) as r:return r.read(limit).decode(r.headers.get_content_charset() or "utf-8",errors="ignore")
    def direct(self,url):
        html=self.fetch(url)
        if BS4_OK:
            soup=BeautifulSoup(html,"html.parser")
            for x in soup(["script","style","noscript","svg"]):x.decompose()
            title=clean_text(soup.title.get_text(" ",strip=True) if soup.title else domain_of(url));body=clean_text(soup.get_text(" ",strip=True))
        else:title=domain_of(url);body=clean_text(re.sub(r"<[^>]+>"," ",html))
        return [{"title":title,"href":url,"body":body[:9000]}]
    def search_data(self,q,learn=True):
        q=clean_text(q); key=stable_key(q)
        if not q:return []
        cached=self.cache.get(key)
        if isinstance(cached,dict) and isinstance(cached.get("results"),list):
            results=cached["results"]
        else:
            results=[];src=self.settings.get("web_sources",[])
            if "duckduckgo" in src:results+=self._ddg(q)
            if not results and "wikipedia" in src:results+=self._wiki(q)
            if looks_like_url(q) and "direct_url" in src:
                try:results+=self.direct(q)
                except Exception as e:self.notifications.push("network_error",f"URL fetch failed: {type(e).__name__}")
            results=results[:int(self.settings["max_search_results"])]
            self.cache[key]={"query":q,"time":now_iso(),"results":results};self.save()
        if learn and results:self.collect(results,q)
        return results
    def render_results(self,q,results=None):
        if results is None:results=self.search_data(q,learn=True)
        if not results:return f"No web results were available for: {safe_text(q)}"
        out=[f"[b]WEB RESULTS: {safe_text(q)}[/b]"]
        for i,x in enumerate(results,1):
            out.append(f"{i}. [b]{safe_text(clean_text(x.get('title') or 'Result')[:180])}[/b]\n   {safe_text(clean_text(x.get('body'))[:700])}\n   Source: {safe_text(str(x.get('href',''))[:300])}")
        return "\n\n".join(out)
    def search(self,q,learn=True):
        return self.render_results(q,self.search_data(q,learn=learn))
    def source(self,url):
        ok,msg=safe_url(url)
        if not ok:return msg
        try:
            results=self.direct(url);self.collect(results,url);return self.render_results(url,results)
        except Exception as e:return f"Source fetch failed: {e}"
    def digest(self,kind,target):
        k=normalize_text(kind)
        if k in {"web","url","page"}:return self.digest_web(target)
        if k=="pdf":return self.digest_pdf(target)
        if k in {"youtube","yt"}:return self.digest_youtube(target)
        if k in {"image","img","ocr"}:return self.digest_image(target)
        if k in {"txt","text","file"}:return self.digest_txt(target)
        return "Digest types: web, pdf, youtube, image, txt."
    def collect(self,results,q):
        for x in results:
            body=clean_text(x.get("body",""));url=x.get("href","")
            if body:self.store.ingest(body,url or f"web:{q}","web");self.sources.append({"time":now_iso(),"type":"web","url":url,"title":clean_text(x.get("title")),"query":q})
        self.save()
    def digest_web(self,url):
        try:r=self.direct(url)[0]
        except Exception as e:return f"Web digest failed: {e}"
        x=self.store.ingest(r.get("body",""),url,"web");self.sources.append({"time":now_iso(),"type":"web","url":url,"title":r.get("title")});self.save();return f"Web page digested: {x['qa']} Q&A + {x['knowledge']} knowledge items learned."
    def digest_pdf(self,path):
        p=Path(path).expanduser()
        if not p.exists():return f"PDF not found: {p}"
        if not PDF_OK:return "PDF support unavailable. Install PyPDF2."
        try:
            with p.open("rb") as f:r=PyPDF2.PdfReader(f);text="\n".join(page.extract_text() or "" for page in r.pages)
            x=self.store.ingest(text,str(p));return f"PDF digested: {x['qa']} Q&A + {x['knowledge']} knowledge items learned."
        except Exception as e:return f"PDF digest failed: {e}"
    @staticmethod
    def yt_id(url):
        m=re.search(r"(?:v=|youtu\.be/|youtube\.com/(?:shorts|embed)/)([A-Za-z0-9_-]{6,})",url);return m.group(1) if m else None
    def digest_youtube(self,url):
        if not YT_OK:return "YouTube transcript support unavailable. Install youtube-transcript-api."
        vid=self.yt_id(url)
        if not vid:return "Could not identify a YouTube video ID."
        try:
            if hasattr(YouTubeTranscriptApi,"get_transcript"):tr=YouTubeTranscriptApi.get_transcript(vid)
            elif hasattr(YouTubeTranscriptApi,"list"):tr=next(iter(YouTubeTranscriptApi.list(vid))).fetch()
            else:tr=YouTubeTranscriptApi.fetch(vid)
            text=" ".join(x.get("text","") if isinstance(x,dict) else str(getattr(x,"text",x)) for x in tr);x=self.store.ingest(text,url);return f"YouTube transcript digested: {x['qa']} Q&A + {x['knowledge']} knowledge items learned."
        except Exception as e:return f"YouTube digest failed: {e}"
    def digest_image(self,path):
        p=Path(path).expanduser()
        if not p.exists():return f"Image not found: {p}"
        if not OCR_OK:return "OCR unavailable. Install pillow and pytesseract."
        try:text=pytesseract.image_to_string(PILImage.open(p));x=self.store.ingest(text,str(p));return f"Image OCR digested: {x['qa']} Q&A + {x['knowledge']} knowledge items learned."
        except Exception as e:return f"Image digest failed: {e}"
    def digest_txt(self,path):
        p=Path(path).expanduser()
        if not p.exists():return f"Text file not found: {p}"
        try:x=self.store.ingest(p.read_text(encoding="utf-8",errors="ignore"),str(p));return f"Text file digested: {x['qa']} Q&A + {x['knowledge']} knowledge items learned."
        except Exception as e:return f"Text digest failed: {e}"
    def sources_list(self):return "No sources yet." if not self.sources else "[b]SOURCES[/b]\n"+"\n".join(f"• {x.get('time')} | {x.get('type')} | {safe_text(x.get('title'))}\n  {safe_text(x.get('url'))}" for x in reversed(self.sources[-25:]))

class Projects:
    STAGES={"Stage 1":["Statement of Problem","Intent","Research"],"Stage 2":["Solution 1","Solution 2","Solution 3","Solution 4"],"Stage 3":["Adopt Solution","Modify Solution","Innovate Solution"],"Stage 4":["Materials","Process","Why Chosen"],"Stage 5":["Implementation","Testing","Results"],"Stage 6":["Evaluation","Recommendations"]}
    def __init__(self,settings,store,web):
        self.settings=settings;self.store=store;self.web=web;self.data=safe_read_json(PROJECTS_FILE,{});self.data=self.data if isinstance(self.data,dict) else {};self.current="Current Project";self.data.setdefault(self.current,{"raw":"","stages":{},"updated":now_iso()});self.save()
    def save(self):atomic_json_write(PROJECTS_FILE,dict(list(self.data.items())[-self.settings["max_projects"]:]))
    def set_current(self,name,user=None):
        name=clean_text(name)[:120] or "Current Project";self.current=name;self.data.setdefault(name,{"raw":"","stages":{},"updated":now_iso()});self.data[name]["updated"]=now_iso();self.save()
        if user in self.store.users.data:self.store.users.data[user]["current_project"]=name;self.store.users.save()
        return f"Switched to project: {name}"
    def siphon(self,text,project=None):
        name=project or self.current;p=self.data.setdefault(name,{"raw":"","stages":{},"updated":now_iso()});p["raw"]=(p.get("raw","")+"\n"+str(text)).strip()[:100000];lines=[clean_text(x) for x in str(text).splitlines() if clean_text(x)];stage=None;count=0;i=0
        while i<len(lines):
            line=lines[i];m=re.match(r"(?i)^[#*\- ]*stage\s*(\d+)\s*:?[ ]*(.*)$",line)
            if m:stage=f"Stage {m.group(1)}";p["stages"].setdefault(stage,{});rest=clean_text(m.group(2));
            else:rest=None
            if m:
                if rest:p["stages"][stage]["Description"]=rest;count+=1
                i+=1;continue
            if stage:
                if ":" in line:
                    k,v=[clean_text(x) for x in line.split(":",1)]
                    aliases={"problem":"Statement of Problem","statement of problem":"Statement of Problem","aim":"Intent","purpose":"Intent","design":"Solution 1","solution":"Solution 1","testing":"Testing","result":"Results","evaluation":"Evaluation","recommendation":"Recommendations"}
                    label=aliases.get(normalize_text(k),k)
                    if 2<=len(label)<=140 and len(v)>=2:p["stages"][stage][label]=v[:2000];count+=1;i+=1;continue
                if line.startswith(("#","*")) and i+1<len(lines):
                    k=clean_text(line.lstrip("#*- "));v=clean_text(lines[i+1])
                    if k and v:p["stages"][stage][k]=v[:2000];count+=1;i+=2;continue
            i+=1
        self.store.ingest(text,f"project:{name}","ideas");self.autofill(name);p["updated"]=now_iso();self.save();return f"Siphoned {count} project sections into '{name}'."
    def autofill(self,name=None):
        name=name or self.current;p=self.data.setdefault(name,{"raw":"","stages":{},"updated":now_iso()});filled=0
        for stage,labels in self.STAGES.items():
            b=p["stages"].setdefault(stage,{})
            for label in labels:
                if not clean_text(b.get(label,"")):b[label]=f"Develop a source-supported section for {label.lower()} in {name}.";filled+=1
        self.save();return f"Auto-filled {filled} missing project fields."
    def fill(self,stage):
        m=re.search(r"(?i)stage\s*(\d+)",stage)
        if not m:return "Format: fill: Stage 2"
        stage=f"Stage {m.group(1)}"
        if stage not in self.STAGES:return f"Unknown stage: {stage}"
        p=self.data.setdefault(self.current,{"raw":"","stages":{},"updated":now_iso()});b=p["stages"].setdefault(stage,{});out=[f"[b]{stage} — {self.current}[/b]"]
        for label in self.STAGES[stage]:
            b.setdefault(label,f"Research and write a clear section for {label.lower()}.");out.append(f"• {label}: {b[label]}")
        self.save();return "\n".join(out)
    def view(self,name=None):
        name=name or self.current;p=self.data.get(name)
        if not p:return f"Project not found: {name}"
        out=[f"[b]PROJECT: {safe_text(name)}[/b]"]
        for stage,labels in self.STAGES.items():
            out.append(f"\n[b]{stage}[/b]");b=p.get("stages",{}).get(stage,{})
            out += [f"• {label}: {safe_text(clean_text(b.get(label,"[missing]"))[:1000])}" for label in labels]
        return "\n".join(out)
    def ideas(self,topic):
        topic=clean_text(topic) or self.current;ideas=[x["answer"] for x in self.store.search_all(topic,6) if x.get("answer")]
        if len(ideas)<3 and self.settings.get("auto_web_search",True):
            try:ideas += [clean_text(x.get("body")) for x in self.web._ddg(f"{topic} project ideas") if x.get("body")]
            except Exception:pass
        ideas += [f"Investigate a practical solution related to {topic}.",f"Compare different approaches to {topic}.",f"Design, test and evaluate an intervention for {topic}."]
        seen=set();unique=[]
        for x in ideas:
            s=normalize_text(x)
            if s and s not in seen:seen.add(s);unique.append(x)
        return f"[b]PROJECT IDEAS: {safe_text(topic)}[/b]\n"+"\n".join(f"{i+1}. {x[:700]}" for i,x in enumerate(unique[:3]))

class Training:
    def __init__(self,settings,store,security):self.settings=settings;self.store=store;self.security=security;self.jobs=safe_read_json(TRAINING_FILE,[]);self.jobs=self.jobs if isinstance(self.jobs,list) else []
    def start(self):
        job={"id":secrets.token_hex(8),"time":now_iso(),"status":"completed","items":len(self.store.personal_memory)+len(self.store.personal_qanda)};self.jobs.append(job);self.jobs=cap_list(self.jobs,self.settings["max_training_jobs"]);atomic_json_write(TRAINING_FILE,self.jobs);self.security.audit_event("training_start",self.store.active_user,job);return f"Training refresh completed. Job {job['id']} processed {job['items']} items."
    def status(self):return "No training jobs yet." if not self.jobs else "[b]TRAINING JOBS[/b]\n"+"\n".join(f"• {x.get('id')} | {x.get('time')} | {x.get('status')} | {x.get('items',0)} items" for x in self.jobs[-10:])
    def evals(self):
        cards=[x for x in list(self.store.personal_qanda.values())+list(self.store.global_qanda["cards"].values()) if isinstance(x,dict)]
        if not cards:return "No Q&A data available for evaluation."
        c=[int(x.get("confidence",60)) for x in cards];w=sum(int(x.get("wrong",0)) for x in cards);a=sum(int(x.get("times_asked",0)) for x in cards)
        return f"[b]EVALS[/b]\nCards: {len(cards)}\nAverage confidence: {round(statistics.mean(c),1)}%\nWrong-answer events: {w}\nRecall events: {a}"
    def analytics(self):
        msgs=[len(str(x.get("user",""))) for x in self.store.conversations];return f"[b]ANALYTICS[/b]\nConversations: {len(msgs)}\nAverage user message length: {round(statistics.mean(msgs),1) if msgs else 0}\nActive user: {self.store.active_user}"

class Health:
    def __init__(self,settings,store,security):self.settings=settings;self.store=store;self.security=security
    def scan(self):
        a=self.security.verify();return "[b]V11 HEALTH[/b]\n"+"\n".join([
            f"Python: {sys.version.split()[0]}",f"Kivy: {'available' if KIVY_OK else 'not installed'}",f"Web search: {'available' if DDGS_OK else 'not installed'}",f"Requests: {'available' if REQUESTS_OK else 'not installed'}",f"PDF: {'available' if PDF_OK else 'not installed'}",f"YouTube: {'available' if YT_OK else 'not installed'}",f"OCR: {'available' if OCR_OK else 'not installed'}",f"Knowledge items: {sum(len(v) for v in self.store.categories.values())}",f"Audit: {'VALID' if a['valid'] else 'BROKEN'}"])
    def skills(self):return "[b]V11 SKILLS[/b]\n"+"\n".join("• "+x for x in ["Flexible definition/Q&A parser","All-memory fuzzy recall","Categorized JSON routing","Web/PDF/YouTube/OCR digestion","Project siphoning","Safe AST math","Private user memory","Audit chain","Revision/feedback/analytics","Kivy + CLI fallback"])

class Brain:
    def __init__(self, settings, store, web, projects, training, health, users, security, notifications):
        self.settings, self.store, self.web = settings, store, web
        self.projects, self.training, self.health = projects, training, health
        self.users, self.security, self.notifications = users, security, notifications
        self.last_response = ""
        self.request_count = 0
        self.voice_enabled = bool(settings.get("tts_enabled", False))

    def is_staff(self):
        role = self.users.data.get(self.users.current, {}).get("role", "user")
        return role in {"admin", "engineer"}

    def is_admin(self):
        return self.users.data.get(self.users.current, {}).get("role") == "admin"

    def _staff_guard(self):
        return None if self.is_staff() else "This command is restricted to admin/engineer users."

    def _admin_guard(self):
        return None if self.is_admin() else "This command is restricted to the admin user."

    def _record_usage(self, command, chars=0, error=False):
        data = safe_read_json(USAGE_FILE, [])
        if not isinstance(data, list): data = []
        data.append({"time": now_iso(), "user": self.users.current, "command": command[:120], "response_chars": int(chars), "error": bool(error)})
        atomic_json_write(USAGE_FILE, cap_list(data, self.settings["max_usage_events"]))

    def _long_mode(self, q):
        if not self.settings.get("long_response_mode", True): return False
        low = normalize_text(q)
        return any(k in low for k in self.settings.get("long_response_keywords", []))

    def _intent(self, q):
        low = normalize_text(q)
        for key in ("who", "what", "where", "when", "why", "how", "did", "must"):
            if re.match(rf"^{key}\b", low): return key
        if re.match(r"^(this|that)\s+is\b", low): return "what"
        return "general"

    def _topic(self, q):
        s = clean_text(q)
        s = re.sub(r"(?i)^(who|what|where|when|why|how|did|must)\s+(is|are|was|were|did|does|do|is|must|can|could|should)?\s*", "", s)
        s = re.sub(r"(?i)^(this|that)\s+is\s+", "", s)
        return s.rstrip(" ?.!:") or s

    def _compose(self, query, recalled=None, web_results=None, extra=""):
        intent = self._intent(query)
        topic = self._topic(query)
        parts = []
        if extra: parts.append(extra.strip())
        if recalled:
            answer = clean_text(recalled.get("answer", ""))
            source = recalled.get("scope", "memory")
            label = "Private memory" if source.startswith("private") else "Stored knowledge"
            if answer: parts.append(f"{label}: {answer}")
        if web_results:
            useful = [x for x in web_results if x.get("body")]
            if useful:
                parts.append("Web findings:")
                for x in useful[:3]:
                    title = clean_text(x.get("title") or "Result")
                    body = clean_text(x.get("body"))
                    href = clean_text(x.get("url"))
                    parts.append(f"• {title}\n  {body[:900]}" + (f"\n  Source: {href}" if href else ""))
        if not parts:
            return None
        answer = "\n\n".join(parts)
        if self._long_mode(query) and len(strip_markup(answer)) < self.settings["minimum_answer_chars"]:
            guide = PROMPT_GUIDANCE.get(intent, "Answer directly, then give useful context and an example.")
            answer += f"\n\nApproach: {guide}"
            if topic:
                answer += f"\nRelated idea: consider the main characteristics, examples, practical uses and limitations of {topic}."
        return answer

    def answer(self, user_text):
        q = str(user_text or "").replace("\x00", " ").strip()
        if not q: return "Type a question or command."
        low = normalize_text(q)
        self.request_count += 1
        if self.security.is_location_request(q) and self.settings.get("never_disclose_exact_location", True):
            r = "I can help with general location information, but I won't provide an exact address, GPS coordinates, or hidden device location."
            self._record_usage(q, len(r)); return r
        if self.security.detect_suspicious(q):
            r = "I can help with defensive cybersecurity, secure coding, malware analysis in a safe lab, and account protection, but not credential theft, destructive malware, log deletion, or data exfiltration."
            self._record_usage(q, len(r)); return r
        if re.match(r"(?i)^calc(?:ulate)?\s*:", q):
            expr = q.split(":",1)[1].strip()
            r = SafeMath.evaluate(expr)
            self._record_usage(q, len(r)); return r
        if self._looks_like_math(q):
            r = SafeMath.evaluate(q)
            if not r.startswith("Calculation error"):
                self._record_usage(q, len(r)); return r
        try:
            r = self._route(q)
            r = r or self._fallback(q)
            r = self.security.guard(q, r)
            command_like=low.startswith(("teach:","t:","bulk:","study:","feed:","note:","search:","forget:","web:","breathe:","source:","digest:","settings","setting:","user:","project:","fill:","siphon:","test","quiz:","grade:","export:","import:","calc:","calculate:"))
            if not command_like and not is_simple_query(q,self.settings) and len(strip_markup(r)) < int(self.settings["minimum_answer_chars"]):
                r += "\n\nFor a fuller study answer, add the key definition, main explanation, a practical example, and one or two related ideas."
            r = r[: int(self.settings["max_response_chars"])]
            self.last_response = r
            self._record_usage(q, len(r))
            return r
        except Exception as e:
            self.security.audit_event("engine_error", self.users.current, str(e))
            self._record_usage(q, 0, True)
            return "I hit an internal error while processing that request. Run `health` for diagnostics."

    def _looks_like_math(self, q):
        s = q.strip()
        return bool(re.fullmatch(r"[0-9+\-*/%^().\s]+", s)) and any(ch.isdigit() for ch in s)

    def _fallback(self, q):
        recalled = self.store.recall(q) if self.settings.get("allow_memory_answer", True) and self.settings.get("memory_mode") != "internet_only" else None
        if recalled:
            return self._compose(q, recalled=recalled)
        if self.settings.get("auto_web_search", True) and self.settings.get("allow_internet_answer", True) and self.settings.get("memory_mode") != "memory_only":
            results = self.web.search(q, learn=bool(self.settings.get("auto_learn_from_web", True)))
            composed = self._compose(q, web_results=results)
            if composed: return composed
        # Explicitly search every memory bucket one more time before admitting no answer.
        all_matches = self.store.search_all(q, limit=8)
        if all_matches:
            return self._compose(q, recalled=all_matches[0])
        topic = self._topic(q)
        return f"I don't have enough stored knowledge for {safe_text(topic or q)!r} yet. Try `teach: question | answer | category`, `study: text`, or `web: {topic or q}`."

    def _route(self, q):
        low = normalize_text(q)
        if is_simple_query(q, self.settings):
            if low.startswith("hi") or low.startswith("hello") or low.startswith("hey") or low == "yo": return "Hey! Vibes Only V11 is ready."
            if low.startswith("thank"): return "You're welcome."
            if low in {"bye", "goodbye", "see you"}: return "See you next time."
            return "Got it."
        if low in {"help","menu"}: return COMMANDS_LIST
        if low == "about": return f"[b]{APP_TITLE}[/b]\nLocal-first learning assistant with memory, categorized ingestion, web digestion, projects, revision, privacy controls and CLI/Kivy interfaces."
        if low == "time": return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if low == "settings": return self.settings.render()
        if low in {"vertex: connect","vertex: search"} or low.startswith("playground:"):
            return "External model connector/playground is not configured in this standalone build. Use web:, study:, teach: and digest: for the available local-first workflow."
        if low == "settings: reset":
            g=self._admin_guard()
            return g or self._settings_reset()
        if low.startswith("setting:"):
            g=self._staff_guard(); return g or self.settings.set_value_text(q.split(":",1)[1])
        if low == "health": return self.health.scan()
        if low == "skills": return self.health.skills()
        if low == "duplicates": return self.store.find_duplicates()
        if low in {"users", "user:list"}: return self.users.render()
        if low.startswith("user:add"):
            g=self._admin_guard();
            if g:return g
            data=q.split(":",1)[1].strip() if ":" in q else q[len("user:add"):].strip()
            data=re.sub(r"(?i)^add\b", "", data, count=1).strip()
            bits=data.split()
            r=self.users.add(bits[0] if bits else "", bits[1] if len(bits)>1 else "user")
            if self.users.current in self.users.data:self.store.set_active_user(self.users.current)
            return r
        if low.startswith("user:switch"):
            data=q.split(":",1)[1].strip() if ":" in q else q[len("user:switch"):].strip()
            data=re.sub(r"(?i)^switch\b", "", data, count=1).strip()
            name=clean_text(data)
            r=self.users.switch(name)
            if r.startswith("Switched"):
                self.store.set_active_user(name)
            return r
        if low.startswith("user:delete"):
            g=self._admin_guard();
            if g:return g
            data=q.split(":",1)[1].strip() if ":" in q else q[len("user:delete"):].strip()
            data=re.sub(r"(?i)^delete\b", "", data, count=1).strip()
            return self.users.delete(clean_text(data))
        if low == "notifications": return self.notifications.render()
        if low == "audit": return self.security.show_audit()
        if low == "safety": return self.security.show_safety()
        if low == "usage": return self._usage_render()
        if low == "analytics": return self.training.analytics()
        if low == "evals": return self.training.evals()
        if low == "dataset": return self.store.stats()
        if low == "brain": return self.store.brain_scan()
        if low == "train: start":
            g=self._staff_guard(); return g or self.training.start()
        if low == "train: status": return self.training.status()
        if low == "backup":
            g=self._staff_guard(); return g or self._backup()
        if low in {"export: all", "/export"}: return self._export()
        if low == "reload":
            g=self._staff_guard(); return g or self._reload()
        if low == "selftest": return self.selftest()
        if low == "learned": return self.store.stats()
        if low in {"stats","mem","memory: management","qa"}: return self.store.stats() if low!="brain" else self.store.brain_scan()
        if low == "done": return self.store.clear_notes()
        if low == "random upgrades": return self.random_upgrades()
        if low in {"review", "spaced review"}: return self.store.spaced_review()
        if low == "flashcard": return self.store.flashcard()
        if low == "prompts": return self.prompts()
        if low == "summarize": return self.store.summarize()
        if low == "clear": return self.store.clear_conversations()
        if low == "/voice": return self.toggle_voice()
        if low == "/streak": return self.streak()
        if low.startswith("/name "): return self.set_name(q[6:].strip())
        if low.startswith("/project "): return self.projects.set_current(q[9:].strip(), self.users.current)
        if low.startswith("/theme "): return self.set_theme(q[7:].strip())
        if low.startswith("teach:") or low.startswith("t:"): return self.store.teach_text(q)
        if low.startswith("bulk:"): return self.store.bulk_text(q)
        if low.startswith("study:"): return self.store.siphon(q.split(":",1)[1],source="study") if self.settings.get("auto_learn_from_text",True) else "Text learning is disabled."
        if low.startswith("feed:") or low.startswith("note:"): return self.store.feed_note(q.split(":",1)[1])
        if low.startswith("siphon:") and not low.startswith("siphon: project"):
            return self.store.siphon(q.split(":",1)[1],source="siphon")
        if low.startswith("search:"): return self.store.search_memory(q.split(":",1)[1])
        if low.startswith("forget:"): return self.store.forget(q.split(":",1)[1])
        if low.startswith("explain:"):
            topic=q.split(":",1)[1].strip(); r=self.store.recall(topic)
            return self._compose(q, recalled=r) if r else self._fallback("explain " + topic)
        if low.startswith("example:"):
            topic=q.split(":",1)[1].strip(); r=self.store.recall(topic)
            if r:return f"[b]Examples for {safe_text(topic)}[/b]\n\n1. {r['answer']}\n2. Apply {safe_text(topic)} to a practical situation.\n3. Compare it with a related concept."
            return self._fallback("example " + topic)
        if low.startswith("test") or low.startswith("quiz"):
            cat=q.split(":",1)[1].strip() if ":" in q else None; return self.store.test(cat)
        if low.startswith("grade:"): return self.store.grade(q.split(":",1)[1])
        if low == "ideas" or low.startswith("ideas:"):
            topic=q.split(":",1)[1].strip() if ":" in q else self.projects.current; return self.projects.ideas(topic)
        if low == "project_view": return self.projects.view()
        if low.startswith("project:"):
            return self.projects.set_current(q.split(":",1)[1].strip(), self.users.current)
        if low.startswith("fill:"): return self.projects.fill(q.split(":",1)[1].strip())
        if low.startswith("siphon: project"):
            data=q.split(":",1)[1].strip()
            data=re.sub(r"(?i)^project\s*(?:\|)?\s*", "", data, count=1)
            return self.projects.siphon(data)
        if low.startswith("breathe:"):
            query=q.split(":",1)[1].strip(); return self.web.render_results(query,self.web.search_data(query,learn=bool(self.settings.get("auto_learn_from_web",True))))
        if low.startswith("web:"):
            query=q.split(":",1)[1].strip(); return self.web.render_results(query, self.web.search(query, learn=bool(self.settings.get("auto_learn_from_web",True))))
        if low.startswith("source:"):
            url=q.split(":",1)[1].strip(); return self.web.source(url)
        if low == "sources": return self.web.sources_list()
        if low.startswith("import:"):
            g=self._staff_guard(); return g or self.store.import_pack(q.split(":",1)[1].strip())
        if low.startswith("export:") and low != "export: all": return self._export()
        if low.startswith("digest:"):
            spec=q.split(":",1)[1].strip()
            if "|" in spec: kind,target=[x.strip() for x in spec.split("|",1)]
            else: kind,target="web",spec
            return self.web.digest(kind,target)
        if low.startswith("autolearn:"):
            val=low.split(":",1)[1].strip() in {"on","1","true","yes"}; self.settings.data["auto_learn_from_text"]=val; self.settings.data["auto_learn_from_web"]=val; self.settings.save(); return f"Autolearn {'enabled' if val else 'disabled'}."
        if low.startswith("def:") or low.startswith("definition:"):
            r=self.store.recall(q.split(":",1)[1].strip()); return self._compose(q,recalled=r) if r else self._fallback(q)
        if low.startswith("this is ") or low.startswith("that is "):
            topic=self._topic(q); r=self.store.recall(topic); return self._compose(q,recalled=r) if r else f"Understood. `{clean_text(q)}` can be saved with `teach: {topic} | explanation | definitions`."
        return None

    def random_upgrades(self):
        upgrades=["semantic embeddings","confidence decay","source trust scoring","contradiction detection","offline document index","conversation pinning","memory version history","project templates","teacher mode","flashcard difficulty levels","daily revision planner","source deduplication","incremental backups","encrypted export option","role-based admin permissions","search result reranking","multi-language category routing","structured note extraction","citation-aware web memory","question clustering","memory TTL controls","import format validator","health telemetry dashboard","plugin adapter layer","unit-test command suite"]
        random.shuffle(upgrades);return "[b]RANDOM V11 UPGRADES[/b]\n"+"\n".join(f"{i+1}. {x}" for i,x in enumerate(upgrades[:12]))
    def _settings_reset(self): self.settings.reset(); return "Settings reset to V11 defaults."
    def _usage_render(self):
        data=safe_read_json(USAGE_FILE,[]); data=data if isinstance(data,list) else []
        return "No usage data." if not data else "[b]USAGE[/b]\n"+"\n".join(f"• {x.get('time')} | {x.get('user')} | {x.get('command')} | {x.get('response_chars')} chars" for x in data[-20:])
    def _backup(self):
        dest=BACKUP_DIR/f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        payload={"schema_version":SCHEMA_VERSION,"version":VERSION,"time":now_iso(),"settings":self.settings.data,"users":self.users.data,"global_memory":self.store.global_memory,"global_qanda":self.store.global_qanda,"categories":self.store.categories,"notes":self.store.notes,"conversations":self.store.conversations}
        atomic_json_write(dest,payload); self.security.audit_event("backup",self.users.current,str(dest)); return f"Backup created: {dest}"
    def _export(self):
        p=self.store.export_all(); self.security.audit_event("export",self.users.current,str(p)); return f"Exported data to: {p}"
    def _reload(self):
        fresh=Settings(); self.settings.data=fresh.data; return "Settings reloaded for the current session."
    def set_name(self,name):
        if not name:return "Format: /name Your Name"
        self.users.data[self.users.current]["display_name"]=name[:80];self.users.save();return f"Display name set to {safe_text(name[:80])}."
    def set_theme(self,name):
        name=normalize_text(name)
        if name not in THEMES:return "Theme options: white, dark, hacker."
        self.users.data[self.users.current]["theme"]=name;self.users.save();return f"Theme set to {name}."
    def toggle_voice(self):
        self.voice_enabled=not self.voice_enabled;self.settings.data["tts_enabled"]=self.voice_enabled;self.settings.save();return f"Voice {'enabled' if self.voice_enabled else 'disabled'}."
    def streak(self):
        days=[]; seen=set()
        for x in self.store.conversations:
            try: d=str(x.get("time",""))[:10]; seen.add(d)
            except Exception: pass
        current=date.today(); streak=0
        while current.isoformat() in seen: streak+=1; current-=timedelta(days=1)
        return f"Learning streak: {streak} day(s)."
    def prompts(self):
        return "[b]PROMPT IDEAS[/b]\n\n• Explain a topic with definition, causes, examples and related ideas.\n• Compare two concepts with similarities, differences and examples.\n• Turn notes into Q&A, categorized knowledge and revision cards.\n• Use `web:` for fresh research and `digest:` for source ingestion."
    def selftest(self):
        results=[]
        probe_key="__v11_selftest_cell__"
        probe_answer="A cell is the basic structural and functional unit of life."
        had=probe_key in self.store.personal_qanda
        if not had:self.store.teach_qa(probe_key,probe_answer,"science",private=True,notify=False,source="selftest")
        checks=[("safe math", SafeMath.evaluate("(12+8)*3") in {"60","60.0"}),
                ("definition recall", bool(self.store.search_all(probe_key,1))),
                ("category routing", self.store.classify("Explain photosynthesis") in {"explanations","science"}),
                ("private memory", self.store.active_user==self.users.current),
                ("audit chain", self.security.verify().get("valid",False))]
        if not had:self.store.personal_qanda.pop(probe_key,None);self.store.save_all()
        for n,ok in checks: results.append(f"• {n}: {'PASS' if ok else 'FAIL'}")
        return "[b]V11 SELFTEST[/b]\n"+"\n".join(results)


class ChatController:
    def __init__(self):
        self.settings=Settings(); self.notifications=Notifications(self.settings); self.security=Security(self.settings,self.notifications)
        self.users=Users(self.settings,self.notifications,self.security); self.store=Store(self.settings,self.security,self.notifications,self.users)
        self.web=Web(self.settings,self.store,self.security,self.notifications); self.projects=Projects(self.settings,self.store,self.web)
        self.training=Training(self.settings,self.store,self.security); self.health=Health(self.settings,self.store,self.security)
        self.brain=Brain(self.settings,self.store,self.web,self.projects,self.training,self.health,self.users,self.security,self.notifications)
        self.store.set_active_user(self.users.current)
        self.startup_audit()
    def startup_audit(self):
        try:self.security.audit_event("startup",self.users.current,f"V11 {VERSION}")
        except Exception:pass
    def send(self,text):
        response=self.brain.answer(text)
        self.store.conversations.append({"time":now_iso(),"user":str(text)[:5000],"ai":strip_markup(response)[:16000],"user_id":self.users.current})
        self.store.save_all()
        return response


if KIVY_OK:
    class RoundedCard(BoxLayout):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            with self.canvas.before:
                self._bg=Color(0.08,0.10,0.14,1)
                self._rr=RoundedRectangle(pos=self.pos,size=self.size,radius=[16,])
            self.bind(pos=self._sync,size=self._sync)
        def _sync(self,*_): self._rr.pos=self.pos; self._rr.size=self.size

    class ChatUI(Screen):
        def __init__(self, controller, **kwargs):
            super().__init__(**kwargs); self.controller=controller
            root=BoxLayout(orientation="vertical",padding=8,spacing=8)
            header=BoxLayout(size_hint_y=None,height=48,spacing=6)
            self.title=Label(text=APP_TITLE,markup=True,font_size=20,bold=True)
            header.add_widget(self.title)
            for label,cmd in (("HELP","help"),("THEME","/theme dark"),("HEALTH","health"),("CLEAR","clear")):
                b=Button(text=label,size_hint_x=None,width=78); b.bind(on_release=lambda _,c=cmd:self.do_command(c)); header.add_widget(b)
            root.add_widget(header)
            self.scroll=ScrollView(); self.chat=Label(text="",markup=True,halign="left",valign="top",size_hint_y=None,text_size=(None,None))
            self.chat.bind(texture_size=self._fit_chat); self.scroll.add_widget(self.chat); root.add_widget(self.scroll)
            bar=BoxLayout(size_hint_y=None,height=52,spacing=6)
            self.entry=TextInput(multiline=False,write_tab=False,hint_text="Ask Vibes Only…")
            self.entry.bind(on_text_validate=lambda *_: self.send())
            send=Button(text="SEND",size_hint_x=None,width=90); send.bind(on_release=lambda *_:self.send())
            bar.add_widget(self.entry);bar.add_widget(send);root.add_widget(bar)
            self.add_widget(root);self._history=[]
        def _fit_chat(self,*_):
            self.chat.text_size=(self.scroll.width-20,None); self.chat.height=max(self.scroll.height,self.chat.texture_size[1]); Clock.schedule_once(lambda *_: setattr(self.scroll,"scroll_y",0),0)
        def do_command(self,text):self.entry.text=text;self.send()
        def send(self):
            text=self.entry.text.strip()
            if not text:return
            response=self.controller.send(text);self._history.append((text,response));
            self.chat.text += ("\n\n" if self.chat.text else "") + f"[b]You:[/b] {safe_text(text)}\n[b]Vibes:[/b] {safe_text(response)}";self.entry.text="";self._fit_chat()

    class VibesApp(App):
        def __init__(self, **kwargs): super().__init__(**kwargs); self.controller=ChatController()
        def build(self):
            Window.minimum_width=360; Window.minimum_height=520
            sm=ScreenManager(transition=NoTransition());sm.add_widget(ChatUI(self.controller,name="chat"));return sm
else:
    ChatUI=None
    VibesApp=None


def run_cli(controller):
    print(f"{APP_TITLE}\nType 'help' for commands. Type 'exit' to quit.\n")
    while True:
        try: text=input("You > ").strip()
        except (EOFError,KeyboardInterrupt): print(); break
        if text.lower() in {"exit","quit"}: break
        print("Vibes > " + controller.send(text) + "\n")


def build_controller(): return ChatController()


def main(argv=None):
    parser=argparse.ArgumentParser(description=APP_TITLE)
    parser.add_argument("--cli",action="store_true",help="run terminal chat even when Kivy is installed")
    parser.add_argument("--command",type=str,help="run one command and exit")
    parser.add_argument("--selftest",action="store_true",help="run built-in diagnostics")
    args=parser.parse_args(argv)
    if args.selftest:
        c=build_controller(); print(c.brain.selftest()); return 0
    if args.command is not None:
        c=build_controller(); print(c.send(args.command)); return 0
    if args.cli or not KIVY_OK:
        c=build_controller(); run_cli(c); return 0
    VibesApp().run(); return 0

if __name__ == "__main__":
    raise SystemExit(main())
