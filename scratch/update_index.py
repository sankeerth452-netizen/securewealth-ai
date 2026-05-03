import sys

target_file = '/Users/sankeerthlatheesh/PycharmProject/securewealth-ai/frontend/index.html'

with open(target_file, 'r') as f:
    lines = f.readlines()

# The script block starts at line 507 (0-indexed 506) and ends at line 2224 (0-indexed 2223)
# Note: Since we replaced it once, the line numbers might have shifted, but we know it's between <script> tags.
# Let's find the script tags again to be safe.
content = "".join(lines)
import re
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
 * SECUREWEALTH TWIN v2.3 — Full Production Stabilization
 * Features: Apple UI, Safe DOM Access, Proper Lifecycle, and All Business Logic
 */

// ── CONSTANTS & GLOBAL STATE ──
const API = "https://securewealth-backend.onrender.com";
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
let wizardStep = 1;
let selectedRisk = USER.risk_appetite || 'medium';
let isInitialized = false;
let pendingInvestment = null;
let windowPopulatingApp = false;

// ── UTILITIES & SAFE DOM ACCESS ──

const ui = {
  get: (id) => document.getElementById(id),
  text: (id, val) => { const el = document.getElementById(id); if (el) el.innerText = val; },
  html: (id, val) => { const el = document.getElementById(id); if (el) el.innerHTML = val; },
  show: (id, display = 'block') => { const el = document.getElementById(id); if (el) el.style.display = display; },
  hide: (id) => { const el = document.getElementById(id); if (el) el.style.display = 'none'; },
  class: (id, cls, action = 'add') => { const el = document.getElementById(id); if (el) el.classList[action](cls); }
};

function saveUser() {
  localStorage.setItem('swt_user', JSON.stringify(USER));
}

async function safeFetch(endpoint, options = {}) {
  const url = endpoint.startsWith('http') ? endpoint : `${API}${endpoint}`;
  try {
    const res = await fetch(url, {
      headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
      ...options,
    });
    if (res.status === 401) { window.location.href = '/login'; return null; }
    if (!res.ok) return { error: true, message: `Server returned ${res.status}` };
    return await res.json();
  } catch (err) {
    console.error(`Network error at ${url}:`, err.message);
    return { error: true, message: 'Cannot reach server' };
  }
}

// ── ONBOARDING & WIZARD ──

function nextWizardStep() {
  ui.hide('wizard-step-' + wizardStep);
  ui.class('step-dot-' + wizardStep, 'active', 'remove');
  ui.class('step-dot-' + wizardStep, 'done', 'add');
  wizardStep++;
  ui.show('wizard-step-' + wizardStep);
  ui.class('step-dot-' + wizardStep, 'active', 'add');
}

function prevWizardStep() {
  ui.hide('wizard-step-' + wizardStep);
  ui.class('step-dot-' + wizardStep, 'active', 'remove');
  wizardStep--;
  ui.show('wizard-step-' + wizardStep);
  ui.class('step-dot-' + wizardStep, 'done', 'remove');
  ui.class('step-dot-' + wizardStep, 'active', 'add');
}

function selectRisk(level) {
  selectedRisk = level;
  ['low', 'medium', 'high'].forEach(l => {
    const el = ui.get('risk-' + l);
    if (el) el.classList.toggle('active', l === level);
  });
}

function fillDemo() {
  const fields = { 'f-name':'Priya Sharma', 'f-age':'28', 'f-exp':'beginner', 'f-income':'55000', 'f-expenses':'35000', 'f-savings':'120000', 'f-investments':'60000', 'f-goal':'Buy a house', 'f-timeline':'7' };
  Object.entries(fields).forEach(([id, val]) => { const el = ui.get(id); if(el) el.value = val; });
  selectRisk('medium');
  if (wizardStep === 1) nextWizardStep();
  if (wizardStep === 2) nextWizardStep();
}

async function submitProfile() {
  const name     = ui.get('f-name')?.value.trim()     || USER_DEFAULTS.name;
  const age      = parseInt(ui.get('f-age')?.value)    || USER_DEFAULTS.age;
  const exp      = ui.get('f-exp')?.value              || USER_DEFAULTS.investment_experience;
  const income   = parseFloat(ui.get('f-income')?.value)   || USER_DEFAULTS.income;
  const expenses = parseFloat(ui.get('f-expenses')?.value) || USER_DEFAULTS.monthly_expenses;
  const savings  = parseFloat(ui.get('f-savings')?.value)  || USER_DEFAULTS.current_savings;
  const invValue = parseFloat(ui.get('f-investments')?.value) || USER_DEFAULTS.investments_value;
  const goal     = ui.get('f-goal')?.value             || USER_DEFAULTS.goal;
  const timeline = parseInt(ui.get('f-timeline')?.value)   || USER_DEFAULTS.timeline;

  ui.hide('wizard-step-3');
  ui.show('wizard-loading');

  try {
    const res = await safeFetch('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify({ name, email: `${name.toLowerCase().replace(/\\s/g, '.')}@example.com`, password: "demoPassword123" }),
    });
    if (res && !res.error) {
      localStorage.setItem('jwt_token', res.token);
      localStorage.setItem('account_number', res.account_number);
    }
  } catch(e) { console.error("Signup failed:", e); }

  Object.assign(USER, { name, age, investment_experience: exp, income, monthly_expenses: expenses, current_savings: savings, investments_value: invValue, goal: `${goal} in ${timeline} years`, risk_appetite: selectedRisk, avg_investment: Math.round((income-expenses)*0.1), timeline });
  saveUser();

  await new Promise(r => setTimeout(r, 1000));
  ui.hide('login-screen');
  ui.class('app', 'visible', 'add');
  populateAppFromUser();
}

// ── CORE DATA LOADERS ──

async function loadDashboard() {
  if (!ui.get('page-dashboard')?.classList.contains('active')) return;
  try {
    const [nwRes, profRes] = await Promise.all([
      safeFetch('/api/ai/networth', { method: "POST", body: JSON.stringify({ savings: USER.current_savings||0, investments: USER.investments_value||0, property_value: USER.assets?.property||0, gold_value: USER.assets?.gold||0, vehicle_value: USER.assets?.vehicles||0 }) }),
      safeFetch('/api/ai/profile/analyze', { method: "POST", body: JSON.stringify(USER) })
    ]);

    if (nwRes && !nwRes.error) {
      const nw = nwRes.summary;
      ui.text('dash-networth', `₹${nw.net_worth.toLocaleString('en-IN')}`);
      ui.text('dash-income', `₹${USER.income.toLocaleString('en-IN')}`);
      ui.text('dash-savings', `₹${nw.total_assets.toLocaleString('en-IN')}`);
      ui.text('dash-savings-rate', ((nw.total_assets / (USER.income * 12)) * 100).toFixed(1) + "%");
      
      const assetsList = [ { label: "💰 Savings", val: USER.current_savings }, { label: "📈 Mutual Funds", val: USER.investments_value }, { label: "🪙 Gold", val: USER.assets?.gold }, { label: "🏠 Property", val: USER.assets?.property }, { label: "🚗 Vehicles", val: USER.assets?.vehicles } ];
      const total = nw.total_assets || 1;
      const html = assetsList.map(a => a.val > 0 ? `<div class="stat-row" style="padding: 10px 0;"><div class="stat-row-label">${a.label}</div><div class="stat-row-value">₹${a.val.toLocaleString('en-IN')} <span style="font-size:11px; color:var(--text-secondary); margin-left:4px;">(${Math.round(a.val/total*100)}%)</span></div></div>` : '').join('');
      ui.html("dash-portfolio", html);
    }

    if (profRes && !profRes.error) {
      ui.text('dash-archetype', profRes.archetype);
      ui.text('dash-desc', profRes.archetype.includes("Disciplined") ? "Consistent builder." : "Growth focused.");
      ui.html('dash-tags', `<span class="signal-tag">💪 ${profRes.strength}</span><span class="signal-tag">⚠️ ${profRes.weakness}</span>`);
      if (profRes.behavior_score !== undefined) {
        ui.text('dash-behavior-score', `${profRes.behavior_score} (${profRes.behavior_label})`);
        const el = ui.get('dash-behavior-score');
        if (el) el.style.color = profRes.behavior_score >= 70 ? 'var(--teal)' : 'var(--amber)';
      }
    }
    renderTransactions();
  } catch (e) { console.error("Dashboard load failed", e); }
}

async function loadNetworth() {
  if (!ui.get('page-networth')?.classList.contains('active')) return;
  try {
    const res = await safeFetch('/api/ai/networth', { method: "POST", body: JSON.stringify({ user_profile: USER, savings: USER.current_savings||0, investments: USER.investments_value||0, property_value: USER.assets?.property||0, gold_value: USER.assets?.gold||0, vehicle_value: USER.assets?.vehicles||0 }) });
    if (res && res.summary) {
      ui.text("nw-total-assets", `₹${res.summary.total_assets.toLocaleString('en-IN')}`);
      ui.text("nw-total-liabilities", `₹${res.summary.total_liabilities.toLocaleString('en-IN')}`);
      ui.text("nw-net-worth", `₹${res.summary.net_worth.toLocaleString('en-IN')}`);
      
      const icons = { savings:'🏦', investments:'📈', property:'🏠', gold:'🪙', vehicles:'🚗' };
      const html = Object.entries(res.breakdown || {}).map(([k, v]) => v > 0 ? `<div class="stat-row"><div class="stat-row-label">${icons[k]||'🔹'} ${k}</div><div class="stat-row-value">₹${v.toLocaleString('en-IN')}</div></div>` : '').join('');
      ui.html("nw-breakdown", html || "No assets found");
    }
  } catch (e) { console.error("Networth load failed", e); }
}

async function loadRiskAlerts() {
  if (!ui.get('page-alerts')?.classList.contains('active')) return;
  try {
    const data = await safeFetch('/api/execute/audit');
    if (!data || data.error) return;
    const logs = data.log || [];
    
    ui.text("alert-total", logs.length);
    let warn = 0, block = 0, protectedAmt = 0;
    logs.forEach(l => { if(l.decision==='WARN') warn++; if(l.decision==='BLOCK'){ block++; protectedAmt += (l.amount||0); } });
    ui.text("alert-warns", warn);
    ui.text("alert-blocks", block);
    ui.text("alert-protected", `Protected ₹${protectedAmt.toLocaleString('en-IN')}`);

    const html = logs.slice(-10).reverse().map(l => `
      <div class="alert-item alert-${l.decision.toLowerCase()}">
        <div class="alert-icon">${l.decision==='BLOCK'?'🔴':l.decision==='WARN'?'🟡':'🟢'}</div>
        <div class="alert-body">
          <div class="alert-title">${l.action_type || 'Transaction'} — ₹${(l.amount||0).toLocaleString('en-IN')} ${l.decision}</div>
          <div class="alert-meta">${(l.signals||[]).join(' · ')} · ${new Date(l.timestamp).toLocaleTimeString()}</div>
        </div>
        <div class="alert-score">${Math.round(l.risk_score||0)}</div>
      </div>`).join('');
    ui.html("audit-log-container", html || "No activity logs.");
  } catch (e) { console.error("Alerts load failed", e); }
}

// ── APP LIFECYCLE ──

function switchPage(name, navEl) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  ui.class('page-' + name, 'active', 'add');
  if (navEl) navEl.classList.add('active');
  
  if (name === 'networth') loadNetworth();
  if (name === 'dashboard') { loadDashboard(); loadActivityFeed(); populateBankCard(); }
  if (name === 'alerts') loadRiskAlerts();
  if (name === 'transfer') { populateBankCard(); resetTransfer(); }
}

async function populateAppFromUser() {
  if (windowPopulatingApp) return;
  windowPopulatingApp = true;
  try {
    const initials = (USER.name || 'P').split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase();
    ui.text('sidebar-avatar', initials);
    ui.text('sidebar-name', USER.name);
    ui.text('sidebar-role', (USER.risk_appetite||'Medium') + ' Investor');
    
    const hour = new Date().getHours();
    ui.text('dash-greeting', `${hour < 12 ? 'Good morning' : hour < 17 ? 'Good afternoon' : 'Good evening'}, ${USER.name.split(' ')[0]} 👋`);

    updateChart();
    loadDashboard();
    loadNetworth();
    loadRiskAlerts();
    renderTransactions();
    populateBankCard();
    loadActivityFeed();
  } finally { windowPopulatingApp = false; }
}

function initApp() {
  if (isInitialized) return;
  console.log("🚀 Initializing SecureWealth Twin...");
  isInitialized = true;

  if (localStorage.getItem('swt_user')) {
    ui.hide('login-screen');
    ui.class('app', 'visible', 'add');
    populateAppFromUser();
  } else {
    ui.show('login-screen', 'flex');
  }
}

// ── GLOBAL LISTENERS ──

window.addEventListener('DOMContentLoaded', () => {
  initApp();
  
  // Refresh loop
  setInterval(() => {
    const active = document.querySelector('.page.active')?.id;
    if (active === 'page-dashboard') loadDashboard();
    if (active === 'page-alerts') loadRiskAlerts();
  }, 10000);
});

// ── FEATURE FUNCTIONS ──

async function sendChat() {
  const input = ui.get('chat-input');
  if (!input || !input.value.trim()) return;
  const msg = input.value.trim();
  input.value = '';
  addMessage('user', msg);
  showTyping();
  try {
    const res = await safeFetch('/api/ai/chat', { method: 'POST', body: JSON.stringify({ message: msg, user_profile: USER }) });
    removeTyping();
    if (res && !res.error) handleChatResponse(res, msg);
  } catch(e) { removeTyping(); }
}

function verifyOTP() {
  const val = ui.get('otp-input')?.value;
  if (val === "123456") {
    ui.hide('otp-modal');
    if (pendingInvestment) pendingInvestment();
    pendingInvestment = null;
  } else { alert("Invalid Code. Use 123456"); }
}

function addMessage(role, text) {
  const messages = ui.get('chat-messages');
  if (!messages) return;
  const div = document.createElement('div');
  div.className = `msg ${role==='ai'?'ai':'user'}`;
  div.innerHTML = `<div class="msg-avatar">${role==='ai'?'W':'P'}</div><div class="msg-bubble">${text}</div>`;
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
}

function showTyping() {
  const messages = ui.get('chat-messages');
  if (!messages) return;
  const div = document.createElement('div');
  div.className = 'msg ai'; div.id = 'typing-indicator';
  div.innerHTML = `<div class="msg-avatar">W</div><div class="msg-bubble"><div class="typing-dots"><div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div></div></div>`;
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
}

function removeTyping() { const el = ui.get('typing-indicator'); if (el) el.remove(); }

function populateBankCard() {
  const bal = (USER.current_savings||0) + (USER.investments_value||0);
  ui.text('bc-name', USER.name || 'Account Holder');
  ui.text('bc-balance', `₹${bal.toLocaleString('en-IN')}`);
}

function renderTransactions() {
  const container = ui.get('transactions-list');
  if (!container) return;
  const txs = USER.transactions || [];
  container.innerHTML = txs.length ? txs.map(tx => `<div class="tx-row"><span>${tx.label}</span><span class="${tx.type}">${tx.type==='debit'?'-':'+'}₹${tx.amount.toLocaleString('en-IN')}</span></div>`).join('') : "No transactions.";
}

function resetTransfer() {
  const fields = ['tx-amount', 'tx-recipient', 'otp-input', 'pin1', 'pin2', 'pin3', 'pin4'];
  fields.forEach(f => { const el = ui.get(f); if(el) el.value = ''; });
  ui.hide('otp-modal');
}

// ── CHART LOGIC ──
function updateChart() {
  const data = [];
  let val = USER.current_savings || 0;
  for (let i = 0; i < 12; i++) { val += (USER.income * 0.2); val *= 1.008; data.push(val); }
  const minV = Math.min(...data), maxV = Math.max(...data), w = 400, h = 160, tp = 15, bp = 140, r = (maxV - minV) || 1, ys = bp - tp, xs = w / (data.length - 1);
  const pts = data.map((v, i) => ({ x: i * xs, y: bp - ((v - minV) / r) * ys }));
  let d = `M${pts[0].x},${pts[0].y}`;
  for (let i = 1; i < pts.length; i++) { const mx = (pts[i-1].x + pts[i].x) / 2; d += ` Q${mx},${pts[i-1].y} ${pts[i].x},${pts[i].y}`; }
  const l = ui.get("dash-chart-line"), a = ui.get("dash-chart-area"), dt = ui.get("dash-chart-dot");
  if (l && a && dt) { l.setAttribute("d", d); a.setAttribute("d", `${d} L${w},${h} L0,${h} Z`); dt.setAttribute("cx", pts[pts.length-1].x); dt.setAttribute("cy", pts[pts.length-1].y); }
}

// ── ACTIVITY FEED LOGIC ──
async function loadActivityFeed() {
  const feed = ui.get('activity-feed'); if (!feed) return;
  let items = [...STATIC_FEED];
  try {
    const data = await safeFetch('/api/execute/audit');
    if (data && !data.error) {
      (data.log || []).slice(-3).reverse().forEach(l => {
        items.unshift({ dot: l.decision.toLowerCase(), agent: l.decision==='BLOCK'?'fraud':'wealth', msg: `Shield scanned ₹${(l.amount||0).toLocaleString()} → ${l.decision}`, time: new Date(l.timestamp).toLocaleTimeString() });
      });
    }
  } catch(e) {}
  feed.innerHTML = items.slice(0, 5).map(i => `<div class="activity-item"><div class="activity-dot ${i.dot}"></div><div class="activity-content"><div class="activity-msg">${i.msg}</div><div class="activity-time">${i.time}</div></div></div>`).join('');
}

function handleChatResponse(data, query) {
  addMessage('ai', data.reply || data.ai_explanation || 'Evaluation complete.');
}

function requireOTP(amt, cb) { pendingInvestment = cb; ui.show('otp-modal', 'flex'); }

</script>"""

new_content = content[:start_pos] + new_script_content + content[end_pos:]

with open(target_file, 'w') as f:
    f.write(new_content)

print("Successfully updated index.html with full logic")
