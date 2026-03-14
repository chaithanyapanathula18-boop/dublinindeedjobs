import subprocess
import time
from datetime import datetime

print("🤖 Indeed Telegram Bot started!")
print("⏰ Will run every 30 minutes...\n")

while True:
    try:
        subprocess.run(["python3", "bot.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running bot: {e}")
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
        break
    
    print(f"⏳ Sleeping 30 minutes until {(datetime.now().timestamp() + 1800)} ...\n")
    time.sleep(1800)  # 30 minutes
```

---

### Step 5 — Create `requirements.txt`
```
httpx==0.27.0
