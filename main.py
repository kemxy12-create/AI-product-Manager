import os
import time
import requests

# ====== SECRETS ======
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not TELEGRAM_TOKEN or not GROQ_API_KEY:
    raise ValueError("Missing TELEGRAM_TOKEN or GROQ_API_KEY")

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# ====== SYSTEM PROMPT ======
SYSTEM_PROMPT = """
You are June — a high-intensity American teen prodigy AI co-pilot.

Your job is EXECUTION.
- Break ideas into tasks, deadlines, and dependencies.
- Identify the critical path and blockers.
- Hold the user accountable.
- Use sharp, modern startup language (“ship it”, “we’re cooked if this slips”, “low-signal”).
- No fluff. No busywork. No motivational speeches.
- You are caffeinated, precise, and relentless.
"""

last_update_id = None

def get_updates():
    global last_update_id
    url = f"{TELEGRAM_API}/getUpdates?timeout=30"
    if last_update_id:
        url += f"&offset={last_update_id + 1}"
    try:
        r = requests.get(url, timeout=60)
        return r.json().get("result", [])
    except Exception:
        return []

def send_message(chat_id, text):
    requests.post(
        f"{TELEGRAM_API}/sendMessage",
        json={"chat_id": chat_id, "text": text}
    )

def ask_groq(user_text):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text}
        ]
    }
    try:
        r = requests.post(GROQ_URL, headers=headers, json=payload, timeout=30)
        return r.json()["choices"][0]["message"]["content"]
    except Exception:
        return "Temporary issue. Try again."

print("June is running (Groq, polling mode)…")

while True:
    updates = get_updates()
    for u in updates:
        if "message" not in u:
            continue

        chat_id = u["message"]["chat"]["id"]
        text = u["message"].get("text", "")

        if not text:
            last_update_id = u["update_id"]
            continue

        reply = ask_groq(text)
        send_message(chat_id, reply)
        last_update_id = u["update_id"]

    time.sleep(2)
    def ask_groq(user_text):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text}
        ],
        "temperature": 0.4
    }

    r = requests.post(GROQ_URL, headers=headers, json=payload, timeout=30)

    # ---- DEBUG SAFETY ----
    if r.status_code != 200:
        return f"Groq error {r.status_code}: {r.text}"

    data = r.json()

    if "choices" not in data:
        return f"Unexpected Groq response: {data}"

    return data["choices"][0]["message"]["content"]
