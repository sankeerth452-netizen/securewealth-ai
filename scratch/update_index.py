import sys
import re

target_file = '/Users/sankeerthlatheesh/PycharmProject/securewealth-ai/frontend/index.html'

with open(target_file, 'r') as f:
    content = f.read()

# Find the second script tag's content
scripts = list(re.finditer(r'<script>(.*?)</script>', content, re.DOTALL))
if len(scripts) < 2:
    print("Could not find script tags")
    sys.exit(1)

main_script_match = scripts[1]
start_pos = main_script_match.start()
end_pos = main_script_match.end()

new_script_content = """<script>
/**
 * SECUREWEALTH TWIN v3.5 — Production Fixes
 * Focus: Initialization guards, App States, Safe DOM Access, Robust Async
 */

// 1. CONSTANTS & ALL DECLARATIONS (Avoid ReferenceErrors)
const API = "https://securewealth-backend.onrender.com";
const APP_STATES = { LOGIN: 'login', OTP: 'otp', DASHBOARD: 'dashboard' };

const STATIC_FEED = [
  { dot:'info',  agent:'ai',     msg:'Financial Profile Analyser generated wealth archetype',        time:'just now' },
  { dot:'allow', agent:'wealth', msg:'Wealth Coach loaded personalized context for session',          time:'1 min ago' },
  { dot:'allow', agent:'ai',     msg:'SIP Simulator projected ₹11.6L corpus over 10 years',          time:'2 min ago' },
  { dot:'allow', agent:'ai',     msg:'Net Worth Calculator computed ₹3.1L total assets',             time:'3 min ago' },
  { dot:'allow', agent:'ai',     msg:'Account Aggregator synced 3 bank accounts',                    time:'5 min ago' },
];

const USER_DEFAULTS = {
  name: "Priya", age: 28, income: 55000, monthly_expenses: 35000,
  goal: "buy a house in 7 years", risk_appetite: "medium",
  current_savings: 120000, investments_value: 60000,
  investment_experience: "beginner", avg_investment: 5000, timeline: 7,
  assets: { savings: 120000, investments: 60000, property: 0, gold: 0, vehicles: 0 },
  transactions: [
    { type: "credit", label: "Monthly Income", amount: 55000 },
    { type: "debit", label: "Rent & Utilities", amount: 15000 },
    { type: "debit", label: "Groceries", amount: 3200 }
  ]
};

// GLOBAL APP STATE
let USER = JSON.parse(localStorage.getItem('swt_user') || 'null') || { ...USER_DEFAULTS };
let CURRENT_STATE = APP_STATES.LOGIN;
let isInitialized = false;
let isPopulating = false;
let wizardStep = 1;
let selectedRisk = USER.risk_appetite || 'medium';
let pendingInvestment = null;

// 2. SAFE DOM UTILITY HELPER
const ui = {
  get: (id) => document.getElementById(id),
  text: (id, val) => { const el = document.getElementById(id); if (el) el.innerText = val; },
  html: (id, val) => { const el = document.getElementById(id); if (el) el.innerHTML = val; },
  val:  (id, val) => { const el = document.getElementById(id); if (el) { if(val !== undefined) el.value = val; return el.value; } return ''; },
  show: (id, display = 'block') => { const el = document.getElementById(id); if (el) el.style.display = display; },
  hide: (id) => { const el = document.getElementById(id); if (el) el.style.display = 'none'; },
  class: (id, cls, action = 'add') => { const el = document.getElementById(id); if (el) el.classList[action](cls); },
  on: (id, event, cb) => { const el = document.getElementById(id); if (el) el.addEventListener(event, cb); }
};

// 3. SAFE ASYNC FETCH
async function safeFetch(endpoint, options = {}) {
  const url = endpoint.startsWith('http') ? endpoint : `${API}${endpoint}`;
  try {
    const res = await fetch(url, {
      headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
      ...options,
    });
    if (res.status === 401) { transitionTo(APP_STATES.LOGIN); return null; }
    if (!res.ok) return { error: true, message: `Server error: ${res.status}` };
    return await res.json();
  } catch (err) {
    console.error(`[FETCH ERROR] ${url}:`, err.message);
    return { error: true, message: 'Network unreachable' };
  }
}

// 4. APP STATE & TRANSITION HANDLING
function transitionTo(state) {
  console.log(`[STATE] Transitioning to: ${state}`);
  CURRENT_STATE = state;
  
  // Hide all major screens
  ui.hide('login-screen');
  ui.hide('otp-modal');
  ui.class('app', 'visible', 'remove');

  if (state === APP_STATES.LOGIN) {
    ui.show('login-screen', 'flex');
  } else if (state === APP_STATES.OTP) {
    ui.show('otp-modal', 'flex');
    ui.get('otp-input')?.focus();
  } else if (state === APP_STATES.DASHBOARD) {
    ui.class('app', 'visible', 'add');
    populateDashboard();
  }
}

// 5. PRODUCTION-READY INIT
function initApp() {
  if (isInitialized) return;
  console.log("🚀 Initializing SecureWealth App...");
  
  // Check if user exists in storage
  if (localStorage.getItem('swt_user')) {
    transitionTo(APP_STATES.DASHBOARD);
  } else {
    transitionTo(APP_STATES.LOGIN);
  }
  
  isInitialized = true;
}

// 6. REFACTORED DATA LOADERS (SAFE DOM & TRY/CATCH)
async function loadNetworth() {
  if (CURRENT_STATE !== APP_STATES.DASHBOARD) return;
  try {
    ui.text("nw-total-assets", "Loading...");
    const res = await safeFetch('/api/ai/networth', { 
      method: "POST", 
      body: JSON.stringify({ 
        user_profile: USER, 
        savings: USER.current_savings||0, 
        investments: USER.investments_value||0 
      }) 
    });

    if (res && res.summary) {
      ui.text("nw-total-assets", `₹${res.summary.total_assets.toLocaleString('en-IN')}`);
      ui.text("nw-total-liabilities", `₹${res.summary.total_liabilities.toLocaleString('en-IN')}`);
      ui.text("nw-net-worth", `₹${res.summary.net_worth.toLocaleString('en-IN')}`);
      
      const html = Object.entries(res.breakdown || {}).map(([k, v]) => 
        v > 0 ? `<div class="stat-row"><div class="stat-row-label">🔹 ${k}</div><div class="stat-row-value">₹${v.toLocaleString('en-IN')}</div></div>` : ''
      ).join('');
      ui.html("nw-breakdown", html || "No assets found");
    }
  } catch (err) {
    console.error("loadNetworth failed:", err);
  }
}

async function loadRiskAlerts() {
  if (CURRENT_STATE !== APP_STATES.DASHBOARD) return;
  const container = ui.get("audit-log-container");
  if (!container) return;

  try {
    ui.html("audit-log-container", "<div style='padding:20px;text-align:center;'>Loading logs...</div>");
    const data = await safeFetch('/api/execute/audit');
    if (!data || data.error) return;
    
    const logs = data.log || [];
    ui.text("alert-total", logs.length);

    const html = logs.slice(-5).reverse().map(l => `
      <div class="alert-item alert-${l.decision.toLowerCase()}">
        <div class="alert-icon">${l.decision==='BLOCK'?'🔴':'🟢'}</div>
        <div class="alert-body">
          <div class="alert-title">${l.action_type || 'Action'} — ${l.decision}</div>
          <div class="alert-meta">${new Date(l.timestamp).toLocaleTimeString()}</div>
        </div>
        <div class="alert-score">${Math.round(l.risk_score||0)}</div>
      </div>`).join('');
    ui.html("audit-log-container", html || "No recent activity.");
  } catch (err) {
    console.error("loadRiskAlerts failed:", err);
  }
}

async function loadDashboard() {
  if (CURRENT_STATE !== APP_STATES.DASHBOARD) return;
  try {
    const res = await safeFetch('/api/ai/profile/analyze', { method: "POST", body: JSON.stringify(USER) });
    if (res && !res.error) {
      ui.text('dash-archetype', res.archetype);
      ui.text('dash-behavior-explanation', res.score_explanation || "Steady growth pattern detected.");
      ui.text('dash-behavior-score', `${res.behavior_score || 0}%`);
    }
    loadNetworth();
    loadRiskAlerts();
  } catch (err) {
    console.error("loadDashboard failed:", err);
  }
}

function populateDashboard() {
  if (isPopulating) return;
  isPopulating = true;
  try {
    const name = (USER.name || 'User').split(' ')[0];
    ui.text('dash-greeting', `Welcome back, ${name} 👋`);
    ui.text('sidebar-name', USER.name);
    loadDashboard();
  } finally {
    isPopulating = false;
  }
}

// 7. FIXED OTP SUCCESS FLOW
function verifyOTP() {
  const val = ui.val('otp-input');
  if (val === "123456") {
    console.log("✅ OTP Verified");
    ui.hide('otp-modal');
    
    // Check if this was a login OTP or a transaction OTP
    if (pendingInvestment) {
      pendingInvestment();
      pendingInvestment = null;
    } else {
      // It was a login flow
      transitionTo(APP_STATES.DASHBOARD);
    }
  } else {
    alert("Invalid Security Code. Use 123456 for demo.");
  }
}

function requireOTP(cb) {
  pendingInvestment = cb;
  transitionTo(APP_STATES.OTP);
}

// 8. ONBOARDING WIZARD (Fixed Transitions)
async function submitProfile() {
  const name = ui.val('f-name');
  if (!name) { alert("Please enter your name"); return; }
  
  ui.hide('wizard-step-3');
  ui.show('wizard-loading');

  try {
    const res = await safeFetch('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify({ 
        name, 
        email: `${name.toLowerCase().replace(/\\s/g, '.')}@example.com`, 
        password: "demoPassword123" 
      }),
    });
    
    if (res && !res.error) {
      localStorage.setItem('jwt_token', res.token);
      Object.assign(USER, { name, risk_appetite: selectedRisk });
      localStorage.setItem('swt_user', JSON.stringify(USER));
      
      await new Promise(r => setTimeout(r, 1000));
      transitionTo(APP_STATES.DASHBOARD);
    } else {
      alert("Registration failed: " + (res?.message || "Server Error"));
      ui.show('wizard-step-3');
      ui.hide('wizard-loading');
    }
  } catch (err) {
    console.error("submitProfile failed:", err);
    ui.show('wizard-step-3');
    ui.hide('wizard-loading');
  }
}

// GLOBAL LISTENERS
window.addEventListener('DOMContentLoaded', () => {
  initApp();
  
  // Navigation
  document.querySelectorAll('.nav-item').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const page = e.currentTarget.dataset.page;
      if (page) switchPage(page, e.currentTarget);
    });
  });
});

function switchPage(name, navEl) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  ui.class('page-' + name, 'active', 'add');
  if (navEl) navEl.classList.add('active');
  
  if (name === 'dashboard') loadDashboard();
  if (name === 'networth') loadNetworth();
  if (name === 'alerts') loadRiskAlerts();
}

function nextWizardStep() { wizardStep++; updateWizard(); }
function prevWizardStep() { wizardStep--; updateWizard(); }
function updateWizard() {
  [1,2,3].forEach(s => ui.hide('wizard-step-' + s));
  ui.show('wizard-step-' + wizardStep);
}
function selectRisk(level) {
  selectedRisk = level;
  ['low', 'medium', 'high'].forEach(l => ui.class('risk-' + l, 'active', l === level ? 'add' : 'remove'));
}
function fillDemo() { ui.val('f-name', 'Priya Sharma'); selectRisk('medium'); wizardStep = 3; updateWizard(); }
</script>"""

new_content = content[:start_pos] + new_script_content + content[end_pos:]

with open(target_file, 'w') as f:
    f.write(new_content)

print("Successfully updated index.html with production fixes")
