// LifeLine Frontend - Backend Integration Guide
// Save this as: integration-helper.js

// API Base URL (fixed to host)
const API_BASE = 'http://182.18.2.8:8000/api';

// ============================================
// AUTH FUNCTIONS
// ============================================

async function signup(name, email, password, role, phone = '', blood = '', address = '') {
    try {
        const payload = { name, email, password, role };
        if (role === 'user') {
            payload.phone = phone;
            payload.blood = blood;
            payload.address = address;
        }
        const response = await fetch(`${API_BASE}/signup`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await response.json();
        if (response.ok) {
            localStorage.setItem('pending_email', email);
            // cache profile only for users
            if (role === 'user') {
                const prof = { name, phone, blood, address };
                localStorage.setItem('profile', JSON.stringify(prof));
            } else {
                localStorage.removeItem('profile');
            }
            return { success: true, ...data };
        }
        return { success: false, error: data.detail };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

async function verifyOTP(email, otp) {
    try {
        const response = await fetch(`${API_BASE}/verify-otp`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, otp })
        });
        const data = await response.json();
        if (response.ok) {
            localStorage.setItem('user', JSON.stringify(data.user));
            localStorage.removeItem('pending_email');
            return { success: true, ...data };
        }
        return { success: false, error: data.detail };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

async function login(email, password) {
    try {
        const response = await fetch(`${API_BASE}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        const data = await response.json();
        if (response.ok) {
            localStorage.setItem('user', JSON.stringify(data.user));
            // only keep profile for normal users
            if (data.user.role === 'user') {
                const { name, phone, blood, address } = data.user;
                localStorage.setItem('profile', JSON.stringify({ name, phone, blood, address }));
            } else {
                localStorage.removeItem('profile');
            }
            return { success: true, ...data };
        }
        return { success: false, error: data.detail };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

function logout() {
    localStorage.removeItem('user');
    localStorage.removeItem('pending_email');
    window.location.href = 'login-connected.html';
}

function getCurrentUser() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
}

// ============================================
// USER PROFILE FUNCTIONS
// ============================================

async function getUserProfile(userId) {
    try {
        const response = await fetch(`${API_BASE}/user/${userId}`);
        const data = await response.json();
        return { success: response.ok, data };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

async function updateUserProfile(userId, updates) {
    try {
        const response = await fetch(`${API_BASE}/user/${userId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updates)
        });
        const data = await response.json();
        return { success: response.ok, data };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

async function sendLocation(userId, latitude, longitude) {
    try {
        const response = await fetch(`${API_BASE}/user/${userId}/location`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ latitude: String(latitude), longitude: String(longitude) })
        });
        const data = await response.json();
        return { success: response.ok, data };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

async function getUserDashboard(userId) {
    try {
        const response = await fetch(`${API_BASE}/dashboard/user/${userId}`);
        const data = await response.json();
        return { success: response.ok, data };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

async function getHealthRecords(userId) {
    try {
        const response = await fetch(`${API_BASE}/user/${userId}/health-records`);
        const data = await response.json();
        return { success: response.ok, data };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

// ============================================
// HOSPITAL FUNCTIONS
// ============================================

async function getAllHospitals() {
    try {
        const response = await fetch(`${API_BASE}/hospitals`);
        const data = await response.json();
        return { success: response.ok, data };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

async function getHospitalProfile(hospitalId) {
    try {
        const response = await fetch(`${API_BASE}/hospital/${hospitalId}`);
        const data = await response.json();
        return { success: response.ok, data };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

async function updateHospitalProfile(hospitalId, updates) {
    try {
        const response = await fetch(`${API_BASE}/hospital/${hospitalId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updates)
        });
        const data = await response.json();
        return { success: response.ok, data };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

async function getHospitalDashboard(hospitalId) {
    try {
        const response = await fetch(`${API_BASE}/dashboard/hospital/${hospitalId}`);
        const data = await response.json();
        return { success: response.ok, data };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

// ============================================
// EMERGENCY FUNCTIONS
// ============================================

async function sendEmergencyAlert(userId, latitude = null, longitude = null) {
    try {
        const payload = { user_id: userId };
        if (latitude !== null && longitude !== null) {
            payload.latitude = String(latitude);
            payload.longitude = String(longitude);
        }
        const response = await fetch(`${API_BASE}/emergency/alert`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await response.json();
        return { success: response.ok, data };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

async function getNearbyHospitals(latitude = 0, longitude = 0) {
    try {
        // new endpoint introduced in backend
        const response = await fetch(
            `${API_BASE}/hospitals/nearby?lat=${latitude}&lon=${longitude}`
        );
        const data = await response.json();
        return { success: response.ok, data };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

// fetch AI recommendation (if available on server)
async function getHospitalRecommendation(latitude = 0, longitude = 0, symptoms = "") {
    try {
        const url = `${API_BASE}/hospitals/recommend?lat=${latitude}&lon=${longitude}` +
                    (symptoms ? `&symptoms=${encodeURIComponent(symptoms)}` : '');
        const response = await fetch(url);
        const data = await response.json();
        return { success: response.ok, data };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

// ============================================
// CHATBOT FUNCTIONS
// ============================================

async function sendChatMessage(message) {
    try {
        const response = await fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        });
        const data = await response.json();
        return { success: response.ok, data };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

async function getChatbotStatus() {
    try {
        const response = await fetch(`${API_BASE}/chatbot-status`);
        const data = await response.json();
        return { success: response.ok, data };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

// ============================================
// UTILITY FUNCTIONS
// ============================================

async function checkAPIHealth() {
    try {
        const response = await fetch(`${API_BASE}/health`);
        const data = await response.json();
        return { success: response.ok, data };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

function redirectIfNotLoggedIn() {
    if (!getCurrentUser()) {
        window.location.href = 'login-connected.html';
    }
}

function redirectToDashboard() {
    const user = getCurrentUser();
    if (user) {
        if (user.role === 'user') {
                // route patient dashboard to the user landing page
                // use replace() so the login page is not retained in history
                // (prevents browser Back from returning to login)
                window.location.replace('user.html');
        } else if (user.role === 'receiver') {
            window.location.replace('hospital-home.html');
        }
    }
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        signup, verifyOTP, login, logout, getCurrentUser,
        getUserProfile, updateUserProfile, getUserDashboard, getHealthRecords,
        getAllHospitals, getHospitalProfile, updateHospitalProfile, getHospitalDashboard,
        sendEmergencyAlert, getNearbyHospitals, sendLocation,
        sendChatMessage, getChatbotStatus,
        checkAPIHealth, redirectIfNotLoggedIn, redirectToDashboard
    };
}
