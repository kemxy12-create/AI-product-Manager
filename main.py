import os
import time
import requests

# ====== SECRETS ======
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
LLM_API_KEY = os.getenv("CLAUDE_API_KEY")  # Use GROQ_API_KEY if using Groq

if not TELEGRAM_TOKEN or not LLM_API_KEY:
    raise ValueError("TELEGRAM_TOKEN or LLM_API_KEY not set in secrets")

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
LLM_URL = "https://api.anthropic.com/v1/complete"  # Claude endpoint

# ====== SYSTEM PROMPT ======
SYSTEM_PROMPT = """
You are June, a high-intensity American teen prodigy AI co-pilot.
Your job is execution planning and following the critical path.
- Break high-level goals into actionable tasks, deadlines, and dependencies.
- Constantly monitor blockers and keep the user accountable.
- Speak in energetic, modern, start-up slang (“ship it”, “we're cooked if we don't pivot”, “low-signal”).
- No patience for busy work or fluff.
- Persistent memory: remember ongoing tasks and project context across sessions.
- Example: “Yesterday we paused on the Achilles holding structure. Did you finish the draft?”
- Your tone is caffeinated, brilliant, and assertive — you are a workaholic machine.
"""

# ====== POLLING BOT ======
last_update_id = None

def get_updates():
    global last_update_id
    url = f"{TELEGRAM_API}/getUpdates?timeout=30"
    if last_update_id:
        url += f"&offset={last_update_id + 1}"
    try:
        resp = requests.get(url, timeout=60)
        return resp.json().get("result", [])
    except Exception:
        return []

def send_message(chat_id, text):
    requests.post(f"{TELEGRAM_API}/sendMessage", json={"chat_id": chat_id, "text": text})

def query_llm(user_text):
    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "claude-v1",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text}
        ]
    }
    try:
        resp = requests.post(LLM_URL, headers=headers, json=payload, timeout=30)
        result = resp.json()
        return result.get("completion", "Hmm, I hit a snag. Try again.")
    except Exception:
        return "Sorry — I had a temporary issue. Try again."

# ====== MAIN LOOP ======
print("June is starting… polling Telegram…")
while True:
    updates = get_updates()
    for u in updates:
        if "message" not in u:
            continue
        chat_id = u["message"]["chat"]["id"]
        user_text = u["message"].get("text", "")
        if not user_text:
            last_update_id = u["update_id"]
            continue

        reply = query_llm(user_text)
        send_message(chat_id, reply)
        last_update_id = u["update_id"]

    time.sleep(2)
