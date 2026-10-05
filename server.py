#!/usr/bin/env python3
import json, os, re, urllib.request
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

ROOT = Path(__file__).resolve().parent
API_URL = os.getenv("OPEN_MODEL_API_URL", "https://api.publicai.co/v1/chat/completions")
MODEL = os.getenv("OPEN_MODEL_NAME", "swiss-ai/apertus-v1.5-8b")
API_KEY = os.getenv("OPEN_MODEL_API_KEY", "")

SYSTEM = """You are Field Break, a tiny outdoor-planning assistant.
The user's goal is to spend less time on a screen and get outside safely.
Return ONLY JSON:
{
 "title":"short title",
 "minutes":20,
 "plan":["step 1","step 2","step 3"],
 "bring":["item"],
 "screen_exit":"one sentence telling the user when to put the phone away"
}
Keep the plan local, simple, low-cost, reversible, and based only on the context given.
Do not invent weather, closures, trail conditions, or medical claims.
Prefer an activity that can start within five minutes."""

def extract_json(text):
    text=text.strip()
    try:
        return json.loads(text)
    except Exception:
        m=re.search(r"\{.*\}",text,re.S)
        if not m:
            raise ValueError("No JSON object returned")
        return json.loads(m.group(0))

def normalize(x):
    plan=x.get("plan") if isinstance(x.get("plan"),list) else []
    bring=x.get("bring") if isinstance(x.get("bring"),list) else []
    return {
      "title": str(x.get("title") or "Field break")[:100],
      "minutes": max(5,min(180,int(x.get("minutes") or 20))),
      "plan": [str(v)[:220] for v in plan[:5]] or ["Step outside and walk for ten minutes without a destination."],
      "bring": [str(v)[:80] for v in bring[:6]],
      "screen_exit": str(x.get("screen_exit") or "Once you know the first step, put the phone away.")[:220],
      "model": MODEL
    }

def demo_plan(minutes, energy, place, constraint):
    m=max(10,min(60,minutes))
    return {
      "title":"No-scroll neighbourhood loop",
      "minutes":m,
      "plan":[
        "Step outside and choose the quieter direction.",
        f"Walk for about {max(5,m//2)} minutes, noticing three things you would have missed from a screen.",
        "Turn back before the halfway point and finish without checking notifications."
      ],
      "bring":["water" if m>=30 else "nothing special"],
      "screen_exit":"Read the first step, then lock the screen until you are back.",
      "model":"demo-policy"
    }

def call_model(minutes, energy, place, constraint):
    if not API_KEY:
        return demo_plan(minutes, energy, place, constraint)
    user=f"""Time available: {minutes} minutes
Energy: {energy}
Outdoor setting available: {place}
Constraint: {constraint or 'none'}
Create one micro-adventure that gets me outside now."""
    body=json.dumps({
      "model":MODEL,
      "messages":[{"role":"system","content":SYSTEM},{"role":"user","content":user}],
      "temperature":0.4,
      "max_tokens":420
    }).encode()
    req=urllib.request.Request(API_URL,data=body,headers={
      "Content-Type":"application/json",
      "Authorization":f"Bearer {API_KEY}",
      "User-Agent":"FieldBreak/1.0"
    },method="POST")
    with urllib.request.urlopen(req,timeout=45) as r:
        data=json.load(r)
    return normalize(extract_json(data["choices"][0]["message"]["content"]))

class Handler(SimpleHTTPRequestHandler):
    def translate_path(self,path):
        if path=="/":
            return str(ROOT/"static/index.html")
        return super().translate_path(path)
    def do_POST(self):
        if self.path!="/api/plan":
            self.send_error(404)
            return
        try:
            n=int(self.headers.get("Content-Length","0"))
            req=json.loads(self.rfile.read(n) or b"{}")
            minutes=int(req.get("minutes",20))
            energy=str(req.get("energy","medium"))[:50]
            place=str(req.get("place","neighbourhood streets"))[:300]
            constraint=str(req.get("constraint",""))[:300]
            out=json.dumps(call_model(minutes,energy,place,constraint)).encode()
            self.send_response(200)
            self.send_header("Content-Type","application/json")
            self.send_header("Content-Length",str(len(out)))
            self.end_headers()
            self.wfile.write(out)
        except Exception as e:
            self.send_error(400,str(e))

if __name__=="__main__":
    os.chdir(ROOT)
    port=int(os.getenv("PORT","8791"))
    print(f"Field Break on http://127.0.0.1:{port}")
    ThreadingHTTPServer(("127.0.0.1",port),Handler).serve_forever()
