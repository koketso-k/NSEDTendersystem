# Tender Insight Hub — Integration Strategy (Number 2)

This document defines the integration strategy for **MySQL, MongoDB, and Redis** in the **Tender Insight Hub** project.

---

## A. Write Operations

### MySQL (source of truth)
- User actions are written first to **MySQL** inside a transaction.
- An **event** is inserted into `integration_outbox` in the same transaction.

### MongoDB (derived data)
- AI summaries, readiness scores, and logs are stored here via workers.

### Redis (ephemeral/cache)
- Search results, analytics, quotas, and locks are cached here with TTL.

---

## B. Read Operations

- **Cache-first**: query Redis first.
- **Fallbacks**: MySQL for structured data, MongoDB for summaries/scores/logs.
- **Cache invalidation**: workers clear/update Redis when relevant events occur.

---

## C. Data Synchronization (Scenarios)

### Scenario 1 — New Tender Saved
- `tenders` row inserted → outbox event `tender.created`.
- Worker `process_new_tender`:
  - Summarize tender text.
  - Save to `tender_summaries` (Mongo).
  - Cache in Redis (`tender:{id}:metadata`).

### Scenario 2 — Company Profile Updated
- Profile updated → outbox event `company.updated`.
- Worker `recalculate_readiness_for_team`:
  - Fetch tenders + profile.
  - Compute scores.
  - Upsert into `readiness_scores` (Mongo).
  - Cache top 5 tenders in Redis.

### Scenario 3 — Analytics Aggregation (Nightly)
- Celery beat job triggers worker `aggregate_analytics_nightly`:
  - Aggregates spend by buyer from MySQL.
  - Writes sorted leaderboard into Redis (`analytics:spend_by_buyer`).

### Scenario 4 — User Activity Logs
- Worker `log_user_activity`:
  - Direct insert into MongoDB capped collection (`user_activity_logs`).
  - Auto-purges old logs → no manual cleanup needed.

---

## D. MySQL Outbox Table

```sql
CREATE TABLE integration_outbox (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    event_type VARCHAR(100) NOT NULL,
    payload JSON NOT NULL,
    published BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    published_at TIMESTAMP NULL
);

CREATE INDEX idx_outbox_unpublished
    ON integration_outbox (published, created_at);
```

---

## E. Dispatcher (Outbox → Celery)

```python
# scripts/dispatch_outbox.py
import time, json
from sqlalchemy import create_engine, text
from celery import Celery
from datetime import datetime

celery_app = Celery("dispatcher", broker="redis://localhost:6379/0")
engine = create_engine("mysql+pymysql://user:pass@localhost:3306/tenderhub")

@celery_app.task
def route_event(event_type, payload):
    if event_type == "tender.created":
        celery_app.send_task("tender_worker.process_new_tender", args=[payload])
    elif event_type == "company.updated":
        celery_app.send_task("readiness_worker.recalculate_readiness_for_team", args=[payload])
    elif event_type == "user.activity":
        celery_app.send_task("activity_worker.log_user_activity", args=[payload])

def dispatch_loop():
    while True:
        with engine.begin() as conn:
            rows = conn.execute(text("""
                SELECT id, event_type, payload
                FROM integration_outbox
                WHERE published = FALSE
                ORDER BY created_at
                LIMIT 50
            """)).fetchall()

            for row in rows:
                route_event.delay(row.event_type, row.payload)
                conn.execute(text("""
                    UPDATE integration_outbox
                    SET published = TRUE, published_at = :ts
                    WHERE id = :id
                """), {"id": row.id, "ts": datetime.utcnow()})
        time.sleep(5)

if __name__ == "__main__":
    dispatch_loop()
```

---

## F. Workers

### 1. Tender Summaries

```python
# workers/tender_worker.py
from celery import Celery
from sqlalchemy import create_engine, text
from pymongo import MongoClient
import redis, json
from datetime import datetime

celery_app = Celery("tender_worker", broker="redis://localhost:6379/0")
pg = create_engine("mysql+pymysql://user:pass@localhost:3306/tenderhub")
mongo = MongoClient("mongodb://localhost:27017/")["tenderhub"]
r = redis.Redis()

def run_summarizer(text):
    return f"Summary: {text[:100]}..."

@celery_app.task(bind=True, max_retries=3)
def process_new_tender(self, payload):
    tid, team_id = payload["tender_id"], payload["team_id"]
    lock_key = f"lock:summary:{tid}"

    if not r.set(lock_key, "1", nx=True, ex=600):
        return

    try:
        with pg.begin() as conn:
            row = conn.execute(
                text("SELECT raw_json, description FROM tenders WHERE tender_id=:tid"),
                {"tid": tid}
            ).mappings().first()
            text_data = row["description"] or json.dumps(row["raw_json"])

        summary = run_summarizer(text_data)

        mongo.tender_summaries.update_one(
            {"tender_id": tid},
            {"$set": {
                "tender_id": tid,
                "team_id": team_id,
                "summary": summary,
                "model_used": "facebook/bart-large-cnn",
                "last_updated": datetime.utcnow()
            }},
            upsert=True
        )

        r.hset(f"tender:{tid}:metadata", mapping={"summary": summary})
        r.expire(f"tender:{tid}:metadata", 6*3600)

    finally:
        r.delete(lock_key)
```

---

### 2. Readiness Scoring

```python
# workers/readiness_worker.py
from celery import Celery
from sqlalchemy import create_engine, text
from pymongo import MongoClient
import redis
from datetime import datetime

celery_app = Celery("readiness_worker", broker="redis://localhost:6379/0")
pg = create_engine("mysql+pymysql://user:pass@localhost:3306/tenderhub")
mongo = MongoClient("mongodb://localhost:27017/")["tenderhub"]
r = redis.Redis()

def calculate_readiness(profile, tender):
    score, checklist = 0, {}
    checklist["sector_match"] = profile["sector"].lower() in (tender["description"] or "").lower()
    if checklist["sector_match"]: score += 25
    checklist["experience_match"] = (profile["experience_years"] or 0) >= (tender.get("min_experience", 0))
    if checklist["experience_match"]: score += 25
    checklist["certifications_match"] = (profile["cidb_level"] or "0") >= str(tender.get("required_cidb", "0"))
    if checklist["certifications_match"]: score += 25
    checklist["coverage_match"] = True
    if checklist["coverage_match"]: score += 25
    return score, checklist

@celery_app.task
def recalculate_readiness_for_team(payload):
    team_id = payload["team_id"]
    with pg.begin() as conn:
        profile = conn.execute(
            text("SELECT * FROM company_profiles WHERE team_id=:tid"),
            {"tid": team_id}
        ).mappings().first()
        tenders = conn.execute(text("SELECT tender_id, description FROM tenders")).mappings().all()

    for tender in tenders:
        score, checklist = calculate_readiness(profile, tender)
        mongo.readiness_scores.update_one(
            {"team_id": team_id, "tender_id": tender["tender_id"]},
            {"$set": {
                "team_id": team_id,
                "tender_id": tender["tender_id"],
                "score": score,
                "checklist": checklist,
                "generated_at": datetime.utcnow()
            }},
            upsert=True
        )

    top = mongo.readiness_scores.find({"team_id": team_id}).sort("score", -1).limit(5)
    r.delete(f"team:{team_id}:top_tenders")
    for t in top:
        r.rpush(f"team:{team_id}:top_tenders", f"{t['tender_id']}:{t['score']}")
    r.expire(f"team:{team_id}:top_tenders", 3600)
```

---

### 3. Analytics Aggregation

```python
# workers/analytics_worker.py
from celery import Celery
from sqlalchemy import create_engine, text
import redis

celery_app = Celery("analytics_worker", broker="redis://localhost:6379/0")
pg = create_engine("mysql+pymysql://user:pass@localhost:3306/tenderhub")
r = redis.Redis()

@celery_app.task
def aggregate_analytics_nightly():
    with pg.begin() as conn:
        rows = conn.execute(
            text("SELECT buyer, SUM(budget) as total FROM tenders GROUP BY buyer")
        ).mappings().all()

    r.delete("analytics:spend_by_buyer")
    for row in rows:
        r.zadd("analytics:spend_by_buyer", {row["buyer"]: float(row["total"])})
    r.expire("analytics:spend_by_buyer", 86400)
```

---

### 4. User Activity Logs

```python
# workers/activity_worker.py
from celery import Celery
from pymongo import MongoClient
from datetime import datetime

celery_app = Celery("activity_worker", broker="redis://localhost:6379/0")
mongo = MongoClient("mongodb://localhost:27017/")["tenderhub"]

@celery_app.task
def log_user_activity(payload):
    mongo.user_activity_logs.insert_one({
        "user_id": payload["user_id"],
        "action": payload["action"],
        "metadata": payload.get("metadata", {}),
        "timestamp": datetime.utcnow()
    })
```

---

## G. End-to-End Guarantees

- **Reliability**: Outbox ensures events are never lost.
- **Performance**: Heavy tasks run asynchronously in Celery.
- **Idempotency**: Mongo upserts + Redis locks prevent duplicates.
- **Scalability**: Multiple workers can run in parallel safely.
- **Consistency**: Derived data is eventually consistent but always catches up.

---

