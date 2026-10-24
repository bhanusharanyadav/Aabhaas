# Aabhaas Option A — Public Alert Website Starter

This starter adds a separate public alert website and FastAPI service inside the existing Aabhaas repository. It does not modify `Dashboard/app.py` and does not yet connect the AI/ML model or IoT sensors.

## Folders

- `backend/`: FastAPI API, Supabase database integration, protected alert creation/resolution endpoints.
- `public-website/`: mobile-friendly public website that checks for active alerts every 5 seconds.
- `backend/supabase_schema.sql`: initial database table schema.

## 1. Create the Supabase database

1. Create a project at https://supabase.com/.
2. Open SQL Editor.
3. Run the contents of `backend/supabase_schema.sql`.
4. Copy the Project URL and server-side service-role key from your project settings. Keep the service-role key private.

## 2. Run the backend locally

In a terminal at the repository root:

```bash
python -m venv .venv
```

Windows:
```powershell
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
$env:SUPABASE_URL="https://YOUR_PROJECT.supabase.co"
$env:SUPABASE_SERVICE_ROLE_KEY="YOUR_SERVER_ONLY_KEY"
$env:ADMIN_API_KEY="a-long-random-secret"
$env:PUBLIC_WEBSITE_ORIGINS="http://localhost:5500,http://127.0.0.1:5500"
uvicorn main:app --app-dir backend --reload --port 8000
```

API docs: http://127.0.0.1:8000/docs

Do not commit actual credentials to GitHub.

## 3. Run the public website locally

1. Open `public-website/config.js`.
2. Keep `API_BASE_URL` as `http://127.0.0.1:8000` for local testing.
3. Serve the folder using VS Code Live Server (port 5500) or another local static server.
4. Open the served `index.html` page.

Opening the HTML file directly with `file://` may cause browser CORS/fetch issues; use a local web server.

## 4. Trigger a test alert

With the backend running, use the Swagger UI at http://127.0.0.1:8000/docs or run this PowerShell example:

```powershell
$headers = @{ "X-Admin-Key" = "a-long-random-secret" }
$body = @{
  title = "TEST — Landslide Risk Alert"
  severity = "HIGH"
  message = "This is a test alert. This is not an official warning."
  location = "Test Monitoring Area"
  source = "MANUAL"
  risk_score = 75
} | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/alerts" -Headers $headers -ContentType "application/json" -Body $body
```

The API key in the command must exactly match `ADMIN_API_KEY`.

## 5. Deploy separately on Render

Create a new Web Service from the same GitHub repository:
- Root directory: leave blank.
- Build command: `pip install -r backend/requirements.txt`
- Start command: `uvicorn main:app --app-dir backend --host 0.0.0.0 --port $PORT`

Set these environment variables in the backend service:
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `ADMIN_API_KEY` (long random secret)
- `PUBLIC_WEBSITE_ORIGINS` (the deployed public website's exact origin, e.g. `https://your-site.netlify.app`)

Deploy the static `public-website/` folder using a static hosting service, then update `public-website/config.js` with the deployed API base URL and redeploy the static site.

## Security and safety notes

- Never expose `SUPABASE_SERVICE_ROLE_KEY` in frontend JavaScript.
- Never use the public alert page to create or resolve alerts.
- This starter currently allows only one active alert at a time; a new alert automatically resolves the previous active alert. Change this rule if you need simultaneous alerts for multiple regions.
- The current prototype uses a shared admin API key. Before a real public safety rollout, replace this with stronger authentication, auditing, rate limiting, monitoring, and validated operational procedures.
- The website polls only while it is open. It does not send push notifications or SMS.
- “No active alert” is not a guarantee of safety. This prototype is not an official emergency warning service.
- AI/ML and IoT trigger integrations are not implemented yet; they are follow-up steps after testing the manual alert flow.
