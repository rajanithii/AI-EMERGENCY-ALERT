# LifeLine Full Stack - Setup & Running Guide

## 🚀 Quick Start

### Step 1: Install Dependencies

Open PowerShell and run:

```powershell
cd d:\newalert\newalert

# Install Python packages
pip install fastapi uvicorn sqlalchemy pydantic email-validator passlib[bcrypt]
```

### Step 2: Setup Email (Optional but Recommended)

Create `.env` file in `d:\newalert\newalert\` with:

```
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
```

**For Gmail Users:**
1. Enable 2-Factor Authentication on your Google account
2. Go to: https://myaccount.google.com/apppasswords
3. Create App Password for Mail → copy the 16-character password
4. Paste it as `EMAIL_PASSWORD` in `.env`

### Step 3: Start Backend Server

```powershell
cd d:\newalert\newalert
python -m uvicorn backend.main:app --reload --port 8000
```

You should see:
```
Uvicorn running on http://127.0.0.1:8000
```

### Step 4: Start Frontend (New Terminal)

```powershell
cd d:\newalert\newalert\frontend
python -m http.server 8001
```

Or use VS Code Live Server extension.

### Step 5: Open in Browser

The frontend uses the following HTML routes (ensure you're running the frontend server on port 8001):

```
"HTML File","Route/Path","Purpose"
"login-connected.html","/login-connected.html","Main login page (USE THIS)"
"signup.html","/signup.html","New user signup"
"role-select.html","/role-select.html","User/Hospital role select"
"profile-view.html","/profile-view.html","Patient profile"
"hospital-home.html","/hospital-home.html","Hospital dashboard"
"hospital-profile.html","/hospital-profile.html","Hospital profile"
```

- **API Docs**: `http://localhost:8000/docs` (Swagger UI)
- **API Health**: `http://localhost:8000/api/health`

---

## 📝 Default Test Accounts

### Patient Account
- Email: `rohith@gmail.com`
- Password: `123456`
- Role: `user`

### Hospital Account
- Email: `hospital@gmail.com`
- Password: `123456`
- Role: `receiver`

These accounts are automatically created when you run the app.

---

## 🔧 Project Structure

```
d:\newalert\
├── newalert/
│   ├── backend/
│   │   ├── main.py                 ✅ All 20+ API routes
│   │   ├── database.py             ✅ SQLite + SQLAlchemy
│   │   ├── auth.py                 ✅ Password hashing & OTP
│   │   ├── email_service.py        ✅ Email sending
│   │   ├── chatbot.py              ✅ Medical AI
│   │   ├── add_sample.py           ✅ Sample data loader
│   │   ├── lifeline.db             ✅ Database file
│   │   └── __init__.py
│   │
│   └── frontend/
│       ├── login-connected.html      ✅ Connected login
│       ├── login.html                ⚫ Original (use login-connected.html)
│       ├── signup.html               ⚫ Base signup
│       ├── role-select.html          ⚫ Role picker
│       ├── user.html                 ⚫ User dashboard
│       ├── profile-view.html         ⚫ User profile
│       ├── hospital-home.html        ⚫ Hospital dashboard
│       ├── hospital-profile.html     ⚫ Hospital profile
│       ├── integration-helper.js     ✅ API helper functions
│       └── style.css
│
├── API_ROUTES.md                   ✅ Complete API documentation
└── .env                             (Create this file)
```

---

## 🔗 API Routes Summary

| Category | Count | Examples |
|----------|-------|----------|
| 🔐 Auth | 4 | signup, login, verify-otp, auth-status |
| 👤 User | 5 | get profile, update profile, dashboard |
| 🏥 Hospital | 4 | get hospitals, get hospital profile, dashboard |
| 🚨 Emergency | 2 | send alert, nearby hospitals |
| 🤖 Chatbot | 2 | send message, chatbot status |
| 📊 General | 3 | health check, routes list |
| **TOTAL** | **20+** | See API_ROUTES.md for details |

---

## 🧪 Testing API Endpoints

### Option 1: Using Swagger UI (Easiest)
1. Open: `http://localhost:8000/docs`
2. Click on any endpoint
3. Click "Try it out"
4. Fill in test data
5. Click "Execute"

### Option 2: Using PowerShell

**Test Health Check:**
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/health" -Method Get
```

**Test Login:**
```powershell
$body = @{
    email = "rohith@gmail.com"
    password = "123456"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/api/login" `
  -Method Post `
  -Headers @{"Content-Type"="application/json"} `
  -Body $body
```

### Option 3: Using JavaScript in Browser Console

```javascript
// Load the helper
fetch('http://localhost:8001/integration-helper.js')

// Example signup with emergency profile information (only required for role 'user')
signup('Alice','alice@example.com','pass123','user','+911234567890','A+','123 Main St')
    .then(result => console.log('signup', result));

// Receiver signup does not send profile data
signup('Bob','bob@hospital.com','letmein','receiver')
    .then(result => console.log('signup receiver', result));

// Test login
login('rohith@gmail.com', '123456').then(result => {
  console.log(result);
  if(result.success) {
    localStorage.setItem('user', JSON.stringify(result.user));
  }
});

// Get user dashboard
getUserDashboard(1).then(result => console.log(result));

// Send chat
sendChatMessage('I have chest pain').then(result => console.log(result));
```

---

## 🎯 Use Cases

### 1. **Patient Signup & Login**
```
1. Go to login-connected.html
2. Click heart to open card
3. Click "Create one" link
4. Fill signup form with name, email, password, medical condition, blood group and address → sends OTP to email

### Environment variables

Make sure to add your tokens to `.env` in the backend folder:

```
HUGGING_FACE_TOKEN=<your hugging face token>
GROQ_API_KEY=<your groq/ai key>
```

AI recommendations will only work when `GROQ_API_KEY` is set and the `groq` client is installed.

### User map

The user dashboard now includes a map showing your current location and nearby hospitals.  Grant location permission when prompted and watch the map populate automatically.
5. Enter OTP → account created
6. Login with credentials
7. Redirected to user dashboard
```

### 2. **Send Emergency Alert**
```javascript
// From user dashboard
const user = getCurrentUser();
const result = await sendEmergencyAlert(user.id);
// Alert sent to all hospitals in system
```

### 3. **Chat with Medical Bot**
```javascript
const response = await sendChatMessage('I have fever');
// Bot responds: "You may have fever. Stay hydrated..."
// If severe symptoms detected → Emergency alert triggered
```

### 4. **View User Profile**
```javascript
const user = getCurrentUser();
const profile = await getUserProfile(user.id);
// Update profile if needed
await updateUserProfile(user.id, { name: 'New Name' });
```

### 5. **Hospital Dashboard**
```javascript
const hospital = getCurrentUser();
const dashboard = await getHospitalDashboard(hospital.id);
// Shows: active alerts, total patients, emergency requests
```

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'fastapi'"
```powershell
pip install fastapi uvicorn sqlalchemy pydantic email-validator passlib[bcrypt]
```

### "Email credentials not configured"
Create `.env` file with `EMAIL_ADDRESS` and `EMAIL_PASSWORD`

### "Cannot connect to localhost:8000"
Make sure backend is running:
```powershell
cd d:\newalert\newalert
python -m uvicorn backend.main:app --reload --port 8000
```

### "CORS error in frontend"
CORS is already enabled in `main.py`. Make sure you're using correct URLs:
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:8001`

### Database not updating
Delete `backend/lifeline.db` and restart server (recreates database)

---

## 📱 Frontend Files Mapping

| File | Purpose | Status |
|------|---------|--------|
| `login-connected.html` | Patient login form | ✅ **USE THIS** |
| `signup.html` | New user registration | ⚫ Needs connection |
| `role-select.html` | Choose user/hospital role | ⚫ Needs connection |
| `profile-view.html` | Patient profile | ⚫ Needs connection |
| `hospital-home.html` | Hospital dashboard | ⚫ Needs connection |
| `hospital-profile.html` | Hospital profile | ⚫ Needs connection |

---

## 🔄 Integration Flow

```
Browser (Frontend HTML)
    ↓
    ├─ Loads integration-helper.js
    ├─ User enters credentials
    ├─ Calls login() function
    ↓
API Server (FastAPI)
    ├─ Receives POST /api/login
    ├─ Validates credentials
    ├─ Checks password hash
    ├─ Returns user data
    ↓
Database (SQLite)
    ├─ Queries users table
    ├─ Returns user record
    ↓
Frontend
    ├─ Stores user in localStorage
    ├─ Redirects to dashboard
```

---

## 🎓 Learning Resources

1. **FastAPI Docs**: https://fastapi.tiangolo.com/
2. **SQLAlchemy Docs**: https://docs.sqlalchemy.org/
3. **JavaScript Fetch API**: https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API
4. **Email with Python**: https://docs.python.org/3/library/smtplib.html

---

## 💡 Next Steps

1. ✅ Backend running on port 8000
2. ✅ Frontend running on port 8001
3. 🔄 Connect all frontend HTML files using integration-helper.js
4. 🔄 Add database persistence for user locations
5. 🔄 Implement real-time notifications (WebSocket)
6. 🔄 Deploy to production (AWS/Heroku)

---

## 📞 Support

If you encounter issues:
1. Check error messages in terminal
2. Review API_ROUTES.md for endpoint details
3. Test API with Swagger UI: http://localhost:8000/docs
4. Check browser console for frontend errors (F12)
5. Verify .env file exists with email credentials

---

**Made with ❤️ by LifeLine Team**
