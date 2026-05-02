# PROJECT: SecureWealth Twin | v3.0-production — Deployment Guide

# SecureWealth Twin — Production Deployment

> **Goal:** Live, judge-accessible URL in under 30 minutes.
> Stack: **Supabase** (PostgreSQL) → **Render** (FastAPI) → **Vercel** (Frontend)

---

## STEP 1 — Supabase (PostgreSQL)

1. supabase.com → New Project → name `securewealth-twin`, region Singapore
2. Settings → Database → Connection string → **Transaction pooler** tab (port 6543)
   ```
   postgresql://postgres.xxxx:PASSWORD@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres
   ```
3. Change scheme to `postgresql+asyncpg://` for FastAPI:
   ```
   DATABASE_URL=postgresql+asyncpg://postgres.xxxx:PASSWORD@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres
   ```
   > Use port 6543 (Transaction pooler) — NOT port 5432.

---

## STEP 2 — Deploy FastAPI to Render

### 2.1 Push to GitHub
```bash
git init && git add . && git commit -m "v3.0 production"
git remote add origin https://github.com/YOUR_USERNAME/securewealth-api.git
git push -u origin main
```

### 2.2 Create Web Service on Render
- render.com → New → Web Service → connect repo
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Plan: Free

### 2.3 Environment Variables on Render
| Key | Value |
|-----|-------|
| `DATABASE_URL` | `postgresql+asyncpg://postgres.xxxx:PW@...pooler.supabase.com:6543/postgres` |
| `GROQ_API_KEY` | `gsk_xxxxxxxxxxxx` |
| `JWT_SECRET` | any 32+ char random string |
| `FRONTEND_URL` | (fill after Vercel deploy) |

### 2.4 Verify
```
GET https://securewealthtwin-api.onrender.com/health
→ {"status":"healthy","db":"connected","agents":7}
```

---

## STEP 3 — Deploy Frontend to Vercel

The frontend is a **single static HTML file** — no server needed.

### 3.1 Update API URL in index.html
```bash
cd frontend
sed -i '' "s|http://localhost:8000|https://securewealthtwin-api.onrender.com|g" index.html
```

### 3.2 Create vercel.json in frontend/
```json
{
  "version": 2,
  "builds": [{"src": "index.html","use": "@vercel/static"}],
  "routes": [{"src": "(.*)","dest": "/index.html"}]
}
```

### 3.3 Deploy
```bash
cd frontend
npx vercel --prod
```
Copy the URL: `https://securewealth-twin.vercel.app`

---

## STEP 4 — Update CORS

Render → Environment → add:
```
FRONTEND_URL=https://securewealth-twin.vercel.app
```
Render auto-redeploys (~2 min).

---

## STEP 5 — Seed Demo User

```bash
curl -X POST https://securewealthtwin-api.onrender.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Priya Sharma","email":"demo@securewealthtwin.com","password":"demo1234"}'
```

---

## STEP 6 — Verify Checklist

```
□ /health → {"db": "connected"}
□ Vercel URL opens login page
□ Sign up / log in works
□ Dashboard shows live balance from Supabase
□ ₹5,000 transfer → AI scan → APPROVED
□ ₹5,00,000 transfer → AI scan → BLOCKED
□ Supabase Table Editor → risk_audit_log → row visible
□ Works on mobile phone
```

---

## Architecture

```
BROWSER → VERCEL (index.html static)
               ↓ HTTPS + CORS
          RENDER (FastAPI + 7 AI Agents)
               ↓ asyncpg + pooling
          SUPABASE (PostgreSQL)
          Tables: users, accounts, transactions,
                  goals, risk_audit_log
```

---

## 30-Second Judge Demo Script

1. Open `[vercel-url]` on phone
2. **Sign up** → `demo@securewealthtwin.com` / `demo1234`
3. **Dashboard** → live balance ₹1,00,000 from Supabase
4. **Send Money** → ₹5,000 → 7-step AI scan → ✅ APPROVED
5. **Send Money** → ₹5,00,000 → AI scan → 🚫 BLOCKED + Trust Pyramid
6. **Supabase Table Editor** → `risk_audit_log` → show real DB row
7. **Wealth Coach** → ask any finance question → live Groq/llama response

*"Every rupee goes through 5 AI agents. Decisions are persisted to a live PostgreSQL database. This is not a mockup."*

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `db: error` on /health | Use `postgresql+asyncpg://` prefix and port 6543 |
| CORS error | Ensure FRONTEND_URL matches your Vercel URL exactly |
| Render slow first load | Free tier sleeps — first request takes ~30s |
| Tables not created | Check Render logs for "✅ Database tables created" |
| passlib error | Ensure `passlib[bcrypt]` in requirements.txt |
