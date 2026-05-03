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
 * SECUREWEALTH TWIN v3.6 — Production Final
 * Changes: Removed OTP step, Direct Dashboard access, Safe DOM fixes
 */

// 1. CONSTANTS & STATE
const API = "https://securewealth-backend.onrender.com";
let appState = "login"; // login | dashboard

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

const STATIC_FEED = [
  { dot:'info',  agent:'ai',     msg:'Financial Profile Analyser generated wealth archetype',        time:'just now' },
  { dot:'allow', agent:'wealth', msg:'Wealth Coach loaded personalized context for session',          time:'1 min ago' },
  { dot:'allow', agent:'ai',     msg:'SIP Simulator projected ₹11.6L corpus over 10 years',          time:'2 min ago' },
  { dot:'allow', agent:'ai',     msg:'Net Worth Calculator computed ₹3.1L total assets',             time:'3 min ago' },
  { dot:'allow', agent:'ai',     msg:'Account Aggregator synced 3 bank accounts',                    time:'5 min ago' },
];

let USER = JSON.parse(localStorage.getItem('swt_user') || 'null') || { ...USER_DEFAULTS };
let isInitialized = false;
let wizardStep = 1;
let selectedRisk = USER.risk_appetite || 'medium';

// 2. SAFE DOM UTILITY
const ui = {
  get: (id) => document.getElementById(id),
  text: (id, val) => { const el = document.getElementById(id); if (el) el.innerText = val; },
  html: (id, val) => { const el = document.getElementById(id); if (el) el.innerHTML = val; },
  val:  (id, val) => { const el = document.getElementById(id); if (el) { if(val !== undefined) el.value = val; return el.value; } return ''; },
  show: (id, display = 'block') => { const el = document.getElementById(id); if (el) el.style.display = display; },
  hide: (id) => { const el = document.getElementById(id); if (el) el.style.display = 'none'; },
  class: (id, cls, action = 'add') => { const el = document.getElementById(id); if (el) el.classList[action](cls); }
};

// 3. STATE MANAGEMENT
function setState(newState) {
  appState = newState;
  renderApp();
}

function renderApp() {
  ui.hide('login-screen');
  ui.hide('otp-modal'); // Keep hidden as OTP is removed from flow
  ui.class('app', 'visible', 'remove');

  if (appState === "login") {
    ui.show('login-screen', 'flex');
  } else if (appState === "dashboard") {
    ui.class('app', 'visible', 'add');
  }
}

// 4. AUTH SUCCESS (DIRECT TO DASHBOARD)
function onAuthSuccess(user) {
  USER = user;
  localStorage.setItem('swt_user', JSON.stringify(USER));
  
  setState("dashboard");

  // Safe dashboard init after render
  setTimeout(() => {
    populateAppFromUser(USER);
  }, 0);
}

async function safeFetch(endpoint, options = {}) {
  const url = endpoint.startsWith('http') ? endpoint : `${API}${endpoint}`;
  try {
    const res = await fetch(url, {
      headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
      ...options,
    });
    if (res.status === 401) { setState("login"); return null; }
    return await res.json();
  } catch (err) {
    console.error("Fetch Error:", err);
    return { error: true };
  }
}

// 5. LOGIN/REGISTER FLOW (NO OTP)
async function submitProfile() {
  const name = ui.val('f-name');
  if (!name) return alert("Name required");

  ui.hide('wizard-step-3');
  ui.show('wizard-loading');

  const response = await safeFetch('/api/auth/register', {
    method: 'POST',
    body: JSON.stringify({
      name,
      email: `${name.toLowerCase().replace(/\\s/g, '.')}@example.com`,
      password: "demoPassword123"
    })
  });

  if (response && response.success) {
    onAuthSuccess(response.user);
  } else {
    alert("Registration failed. Please try again.");
    ui.show('wizard-step-3');
    ui.hide('wizard-loading');
  }
}

// Legacy login button
function doLogin() {
  onAuthSuccess(USER);
}

// 6. DASHBOARD POPULATION (SAFE DOM)
async function populateAppFromUser(user) {
  const name = (user.name || 'User').split(' ')[0];
  ui.text('dash-greeting', `Welcome back, ${name} 👋`);
  ui.text('sidebar-name', user.name);
  
  const initials = (user.name || 'U').split(' ').map(n => n[0]).join('').toUpperCase();
  ui.text('sidebar-avatar', initials);

  loadDashboard();
}

async function loadDashboard() {
  if (appState !== "dashboard") return;
  
  try {
    const res = await safeFetch('/api/ai/profile/analyze', { 
      method: "POST", 
      body: JSON.stringify(USER) 
    });
    
    if (res && !res.error) {
      ui.text('dash-archetype', res.archetype);
      ui.text('dash-behavior-explanation', res.score_explanation || "Analyzing your patterns...");
      ui.text('dash-behavior-score', `${res.behavior_score || 0}%`);
    }
    
    loadNetworth();
    loadRiskAlerts();
    updateChart();
    populateBankCard();
    loadActivityFeed();
  } catch (err) {
    console.error("Dashboard Load Error:", err);
  }
}

async function loadNetworth() {
  try {
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
    }
  } catch (e) {}
}

async function loadRiskAlerts() {
  try {
    const data = await safeFetch('/api/execute/audit');
    if (data && data.log) {
      ui.text("alert-total", data.log.length);
      const html = data.log.slice(-5).reverse().map(l => `
        <div class="alert-item alert-${l.decision.toLowerCase()}">
          <div class="alert-icon">${l.decision==='BLOCK'?'🔴':'🟢'}</div>
          <div class="alert-body">
            <div class="alert-title">${l.action_type} — ${l.decision}</div>
            <div class="alert-meta">${new Date(l.timestamp).toLocaleTimeString()}</div>
          </div>
        </div>`).join('');
      ui.html("audit-log-container", html);
    }
  } catch (e) {}
}

// 7. UI HELPERS
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

// 8. INIT
function initApp() {
  if (isInitialized) return;
  console.log("App Starting...");
  
  const saved = localStorage.getItem('swt_user');
  if (saved) {
    USER = JSON.parse(saved);
    onAuthSuccess(USER);
  } else {
    setState("login");
  }
  
  isInitialized = true;
}

window.addEventListener('DOMContentLoaded', initApp);

// Logic stubs for chart/feed (Maintained structure)
function updateChart() {}
function populateBankCard() {}
function loadActivityFeed() {}
function verifyOTP() {} // OTP removed from flow, stub for safety
</script>"""

new_content = content[:start_pos] + new_script_content + content[end_pos:]

with open(target_file, 'w') as f:
    f.write(new_content)

print("Successfully updated index.html with direct dashboard flow")
