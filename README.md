# 🚨 LifeLine — AI Emergency SOS Alert System

<div align="center">

![LifeLine Banner](https://img.shields.io/badge/LifeLine-Emergency%20SOS-red?style=for-the-badge&logo=heart&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-orange?style=for-the-badge)
![AI Powered](https://img.shields.io/badge/AI-Powered-purple?style=for-the-badge&logo=openai&logoColor=white)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge)

### *"Every second counts. LifeLine makes sure help is already on the way."*

**A real-time AI-powered emergency alert system that connects patients to the nearest hospital — automatically, intelligently, instantly.**

[🚀 Features](#-features) • [🧠 How It Works](#-how-it-works) • [⚙️ Tech Stack](#️-tech-stack) • [🛠️ Setup](#️-local-setup) • [📸 Screenshots](#-screenshots) • [🗺️ Roadmap](#️-roadmap)

</div>

---

## 🌟 What is LifeLine?

LifeLine is an **AI-powered emergency SOS web application** built to bridge the critical gap between someone in distress and the nearest available hospital — in under 10 seconds.

When a user triggers an SOS:
- A **5-second countdown** gives them a chance to cancel accidental triggers
- Their **GPS location** is captured automatically
- Their **pre-registered medical conditions** are sent to the API
- The AI finds the **shortest-distance hospital** using routing analysis
- The hospital receives an **instant real-time alert** with patient details and location

> 💡 Built as a Hackathon project. Designed for real-world deployment in India's emergency response ecosystem.

---

## 🚀 Features

| Feature | Description |
|---|---|
| 🆘 **One-Tap SOS** | Single button triggers the entire emergency flow |
| ⏱️ **5-Second Safety Countdown** | Prevents accidental alerts with a cancellable timer |
| 📍 **Auto GPS Location Capture** | Browser geolocation API captures exact coordinates |
| 🧠 **AI Hospital Routing** | Finds shortest-distance hospital using pre-registered medical data |
| 🏥 **Hospital Dashboard** | Real-time alert receiver for hospital staff |
| 🗺️ **Live Alert Map** | Real-time map showing active SOS locations |
| 📋 **Medical Profile Integration** | Pre-registered conditions sent with every alert |
| 🔐 **Encrypted Data** | Patient data encrypted using `cryptography` library |
| ⚡ **Real-time Updates** | Instant sender ↔ receiver communication |

---

## 🧠 How It Works

```
USER PRESSES SOS BUTTON
        │
        ▼
┌─────────────────────┐
│  5-Second Countdown │  ← User can cancel if accidental
│  ⏱️  5 4 3 2 1...   │
└────────┬────────────┘
         │ (not cancelled)
         ▼
┌─────────────────────┐
│  GPS Location        │  ← Browser Geolocation API
│  📍 lat, lng capture │
└────────┬────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  AI Analysis (FastAPI Backend)       │
│  • Patient's pre-registered          │
│    medical conditions                │
│  • Location coordinates              │
│  • Distance to all registered        │
│    hospitals                         │
│  → Returns: Nearest suitable hospital│
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────┐     ┌──────────────────────┐
│  Patient sees:       │     │  Hospital receives:   │
│  ✅ Alert sent       │     │  🔔 SOS Notification  │
│  🏥 Hospital name    │     │  📍 Patient location  │
│  📏 Distance/ETA    │     │  🩺 Medical conditions│
│  🗺️ Live map        │     │  ⏰ Time of alert     │
└─────────────────────┘     └──────────────────────┘
```

---

## ⚙️ Tech Stack

### Backend
| Technology | Purpose |
|---|---|
| **Python 3.10+** | Core language |
| **FastAPI** | High-performance REST API framework |
| **SQLAlchemy** | ORM for database operations |
| **SQLite** | Lightweight database (upgradeable to PostgreSQL) |
| **Uvicorn** | ASGI server |
| **cryptography** | Patient data encryption |
| **python-dotenv** | Environment variable management |
| **requests** | External API calls for routing |

### Frontend
| Technology | Purpose |
|---|---|
| **HTML5 / CSS3** | Structure and styling |
| **JavaScript** | SOS countdown, geolocation, real-time updates |
| **Geolocation API** | Browser GPS capture |
| **Leaflet.js / Maps API** | Live alert map visualization |

---

## 🛠️ Local Setup

### Prerequisites
- Python 3.10+
- pip
- Git

### Step 1: Clone the Repository
```bash
git clone https://github.com/<your-username>/lifeline.git
cd lifeline
```

### Step 2: Create Virtual Environment
```bash
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

# Windows CMD
.venv\Scripts\activate.bat

# Mac / Linux
source .venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install fastapi uvicorn sqlalchemy requests python-dotenv cryptography
```

### Step 4: Set Up Environment Variables
```bash
cp .env.example .env
# Edit .env with your configuration
```

### Step 5: Initialize Database
```bash
python -c "from newalert.backend.database import init_db; init_db()"
```

### Step 6: Run the Server
```bash
# Development (localhost — allows browser geolocation)
python -m uvicorn newalert.backend.main:app --reload --host 127.0.0.1 --port 8000
```

### Step 7: Open in Browser
```
http://127.0.0.1:8000
```

> ⚠️ **Note:** Browsers require HTTPS for geolocation on non-localhost origins. Use `localhost` for development or deploy with HTTPS for production.

---

## 📁 Project Structure

```
lifeline/
├── newalert/
│   └── backend/
│       ├── main.py          ← FastAPI app entry point
│       ├── database.py      ← SQLAlchemy models & DB init
│       ├── routes/
│       │   ├── alert.py     ← SOS alert endpoints
│       │   └── hospital.py  ← Hospital dashboard endpoints
│       └── utils/
│           ├── geo.py       ← Distance calculation & routing
│           └── encrypt.py   ← Data encryption utilities
├── frontend/
│   ├── index.html           ← User SOS page
│   ├── hospital.html        ← Hospital dashboard
│   └── static/
│       ├── style.css
│       └── app.js           ← Countdown, geolocation logic
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🔐 Security & Privacy

- ✅ Patient medical data is **encrypted** before storage
- ✅ `.env`, `certs/`, and `lifeline.db` are **gitignored** — never committed
- ✅ Location data is only used during active alert — not stored permanently
- ✅ Hospital access is **authenticated** — no public access to patient data

---

## 🗺️ Roadmap

- [x] SOS button with 5-second countdown
- [x] GPS location capture
- [x] AI-powered nearest hospital routing
- [x] Hospital real-time alert dashboard
- [x] Live alert map
- [x] Medical profile integration
- [ ] 🔜 SMS/WhatsApp notification to family contacts
- [ ] 🔜 Deploy on AWS EC2 with HTTPS
- [ ] 🔜 Mobile PWA (installable on phone)
- [ ] 🔜 Multi-language support (Tamil, Hindi)
- [ ] 🔜 Ambulance tracking integration
- [ ] 🔜 Voice-activated SOS trigger

---

## 🏆 Built For

> **Inter-College Hackathon 2025** — Problem Statement: *AI Solutions for Rural Healthcare*
>
> 🥇 Selected to represent college | Successfully built & demonstrated working prototype

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

```bash
git checkout -b feature/your-feature-name
git commit -m "Add: your feature description"
git push origin feature/your-feature-name
```

---

## 👨‍💻 Author

**Rajanithi N**
- 🎓 AI & Data Science Student — Dhanalakshmi Srinivasan University
- 📧 rajanithiff@gmail.com
- 🏅 IBM | Google | Microsoft | AWS Certified (Coursera)

---

## 📄 License

This project is licensed under the MIT License.

---

<div align="center">

**⭐ If LifeLine helped or inspired you, give it a star!**

*Built with ❤️ to save lives*

</div>
