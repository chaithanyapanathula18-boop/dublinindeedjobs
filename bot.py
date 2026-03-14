import os
import json
import httpx
import time
from datetime import datetime

# ── Telegram config ─────────────────────────────────────────────
TELEGRAM_TOKEN   = os.environ.get("TELEGRAM_TOKEN", "8459295642:AAGsLR_uwzETJkCG-Lf999f7lfNUwaTSLTsi")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "7205019596")
SEEN_JOBS_FILE   = "seen_jobs.json"

# ── Indeed API (free endpoint) ──────────────────────────────────
INDEED_API = "https://api.indeed.com/ads/apisearch"
PUBLISHER_ID = os.environ.get("INDEED_PUBLISHER_ID", "")  # Optional, if you have one

# ── Tech job searches across Ireland/Dublin ─────────────────────
SEARCHES = [
    {"q": "software engineer", "l": "Dublin, Ireland"},
    {"q": "frontend developer", "l": "Dublin, Ireland"},
    {"q": "backend developer", "l": "Dublin, Ireland"},
    {"q": "fullstack developer", "l": "Dublin, Ireland"},
    {"q": "devops engineer", "l": "Dublin, Ireland"},
    {"q": "cloud engineer AWS Azure GCP", "l": "Dublin, Ireland"},
    {"q": "data engineer", "l": "Dublin, Ireland"},
    {"q": "data scientist", "l": "Dublin, Ireland"},
    {"q": "machine learning engineer AI", "l": "Dublin, Ireland"},
    {"q": "mobile developer iOS Android", "l": "Dublin, Ireland"},
    {"q": "QA automation test engineer", "l": "Dublin, Ireland"},
    {"q": "systems engineer infrastructure", "l": "Dublin, Ireland"},
    {"q": "cybersecurity engineer", "l": "Dublin, Ireland"},
    {"q": "product manager tech", "l": "Dublin, Ireland"},
    {"q": "engineering manager tech lead", "l": "Dublin, Ireland"},
    # Wider Ireland
    {"q": "software engineer", "l": "Ireland"},
    {"q": "developer remote", "l": "Ireland"},
]

# ── Load previously seen job IDs ────────────────────────────────
def load_seen():
    if os.path.exists(SEEN_JOBS_FILE):
        try:
            with open(SEEN_JOBS_FILE) as f:
                return set(json.load(f))
        except:
            return set()
    return set()

# ── Save job IDs to prevent duplicates ──────────────────────────
def save_seen(ids: set):
    with open(SEEN_JOBS_FILE, "w") as f:
        json.dump(list(ids), f)

# ── Search Indeed (free API) ────────────────────────────────────
def search_indeed(query: str, location: str) -> list:
    params = {
        "q": query,
        "l": location,
        "format": "json",
        "v": "2",
        "fromage": 1,  # last 24 hours
        "limit": 25,
        "highlight": 1,
    }
    
    # Add publisher ID if you have one
    if PUBLISHER_ID:
        params["publisher"] = PUBLISHER_ID
    
    try:
        r = httpx.get(INDEED_API, params=params, timeout=10)
        r.raise_for_status()
        return r.json().get("results", [])
    except Exception as e:
        print(f"Error searching [{query} in {location}]: {e}")
        return []

# ── Classify job by title ───────────────────────────────────────
def classify_job(title: str) -> str:
    t = title.lower()
    
    if any(k in t for k in ["frontend", "front-end", "react", "vue", "angular", "typescript", "javascript ui", "web ui"]):
        return "🎨 Frontend"
    elif any(k in t for k in ["backend", "back-end", "api", "server", "node", "python", "java", "golang", "ruby", ".net", "c#"]):
        return "⚙️ Backend"
    elif any(k in t for k in ["full stack", "fullstack", "mern", "mean"]):
        return "🔄 Full Stack"
    elif any(k in t for k in ["devops", "sre", "infrastructure", "cloud", "aws", "azure", "gcp", "kubernetes", "docker"]):
        return "☁️ DevOps/Cloud"
    elif any(k in t for k in ["data engineer", "data warehouse", "etl", "spark", "hadoop"]):
        return "📊 Data Engineer"
    elif any(k in t for k in ["data scientist", "analytics", "bi ", "machine learning", "ai "]):
        return "🤖 AI/ML"
    elif any(k in t for k in ["mobile", "ios", "android", "flutter", "react native"]):
        return "📱 Mobile"
    elif any(k in t for k in ["qa", "test automation", "quality assurance"]):
        return "🧪 QA/Testing"
    elif any(k in t for k in ["security", "cybersecurity", "infosec"]):
        return "🔒 Security"
    elif any(k in t for k in ["product manager", "product owner"]):
        return "📦 Product"
    elif any(k in t for k in ["engineering manager", "tech lead", "architect"]):
        return "👔 Leadership"
    else:
        return "💻 Tech"

# ── Format job for Telegram ─────────────────────────────────────
def format_job(job: dict) -> str:
    title    = job.get("jobtitle", "N/A")
    company  = job.get("company", "N/A")
    location = job.get("formattedLocation", "Ireland")
    url      = job.get("url", "")
    posted   = job.get("formattedRelativeTime", "Recently")
    
    return (
        f"💼 <b>{title}</b>\n"
        f"🏢 {company}\n"
        f"📍 {location}\n"
        f"⏰ {posted}\n"
        f"<a href='{url}'>🔗 Apply here</a>"
    )

# ── Send message to Telegram ────────────────────────────────────
def send_telegram(text: str):
    try:
        httpx.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": text,
                "parse_mode": "HTML",
                "disable_web_page_preview": True
            },
            timeout=10
        )
    except Exception as e:
        print(f"Telegram error: {e}")

# ── MAIN ────────────────────────────────────────────────────────
def main():
    print(f"\n{'='*60}")
    print(f"[{datetime.now().strftime('%d %b %Y, %H:%M:%S')}] Starting job search...")
    print(f"{'='*60}")
    
    seen     = load_seen()
    new_jobs = []
    
    # Search all job types
    for search in SEARCHES:
        query    = search["q"]
        location = search["l"]
        
        print(f"Searching: {query} in {location}...", end=" ", flush=True)
        jobs = search_indeed(query, location)
        
        for job in jobs:
            job_id = job.get("jobkey")
            
            if job_id and job_id not in seen:
                new_jobs.append(job)
                seen.add(job_id)
        
        print(f"Found {len(jobs)} jobs")
        time.sleep(0.5)  # Be nice to Indeed's servers
    
    if not new_jobs:
        print(f"\n✅ No new jobs found. Cache has {len(seen)} total jobs.")
        return
    
    # Group jobs by category
    by_category = {}
    for job in new_jobs:
        cat = classify_job(job.get("jobtitle", ""))
        by_category.setdefault(cat, []).append(job)
    
    # Send header
    timestamp = datetime.now().strftime('%d %b %Y, %H:%M')
    summary = "\n".join(f"  {cat}: {len(jobs)}" for cat, jobs in sorted(by_category.items()))
    
    send_telegram(
        f"🚀 <b>NEW TECH JOBS IN IRELAND!</b>\n"
        f"📊 {len(new_jobs)} new jobs found\n"
        f"🕐 {timestamp}\n\n"
        f"{summary}"
    )
    
    # Send each job grouped by category
    for category in sorted(by_category.keys()):
        jobs = by_category[category]
        send_telegram(f"\n{'━'*40}\n{category}\n{'━'*40}")
        
        for job in jobs:
            send_telegram(format_job(job))
            print(f"  ✓ Sent: {job.get('jobtitle')} @ {job.get('company')}")
    
    # Save seen jobs
    save_seen(seen)
    print(f"\n✅ Done! Sent {len(new_jobs)} new jobs. Total cached: {len(seen)}")

if __name__ == "__main__":
    main()
