LifeLine — Emergency SOS web app

Short: LifeLine lets users send SOS alerts with location, and hospitals can view alerts.

Quickstart (local development)

1. Create and activate a Python virtual environment

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# or cmd
.venv\Scripts\activate.bat
```

2. Install dependencies

```bash
pip install fastapi uvicorn sqlalchemy requests python-dotenv cryptography
```

3. Initialize the database (if needed)

```bash
python -c "from newalert.backend.database import init_db; init_db()"
```

4. Run the server (bind to host):

```bash
# Development on localhost (allows browser geolocation)
python -m uvicorn newalert.backend.main:app --reload --host 127.0.0.1 --port 8000

# Or run on specific host/IP (browsers will block geolocation over HTTP on IPs)
python -m uvicorn newalert.backend.main:app --reload --host 182.18.2.8 --port 8000
```

Notes about geolocation and GitHub

- Browsers require HTTPS for geolocation from non-localhost origins. For testing on a remote IP use HTTPS or open via `localhost`.
- Do NOT commit `.env`, `certs/`, or `lifeline.db` to the repo. `.gitignore` is included to help.

Pushing to GitHub (example)

```bash
git init
git add .
git commit -m "Initial commit"
# Create a repo on GitHub (web) and then:
git remote add origin git@github.com:<your-username>/<repo-name>.git
git branch -M main
git push -u origin main
```

Or, if you have GitHub CLI installed:

```bash
gh repo create <repo-name> --public --source=. --remote=origin --push
```

If you want, I can create the remote repo for you (requires GitHub token/CLI).