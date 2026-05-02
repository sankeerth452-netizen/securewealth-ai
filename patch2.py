
import re

with open('frontend/index.html', 'r') as f:
    html = f.read()

# Replace login section
old_login = '''<!-- ══════════════ LOGIN SCREEN ══════════════ -->
<div id="login-screen">
  <div class="login-box">
    <div class="login-logo">
      <div class="logo-icon">🛡</div>
      <div class="logo-text">SecureWealth Twin</div>
    </div>
    <div class="login-title">Welcome back</div>
    <div class="login-sub">Your AI-powered financial guardian</div>

    <div class="form-group">
      <label class="form-label">Email address</label>
      <input class="form-input" type="email" placeholder="priya@example.com" id="login-email">
    </div>
    <div class="form-group">
      <label class="form-label">Password</label>
      <input class="form-input" type="password" placeholder="••••••••" id="login-pass">
    </div>
    <button class="btn-primary" onclick="doLogin()">Sign In</button>

    <div class="login-divider">or</div>
    <button class="demo-btn" onclick="doLogin()">🚀 Continue with Demo Account</button>

    <div style="margin-top:20px; padding:12px; background:rgba(0,212,170,0.06); border:1px solid rgba(0,212,170,0.15); border-radius:10px; font-size:12px; color:var(--text-muted); text-align:center;">
      🔒 For simulation & demo purposes only. Not real financial advice.
    </div>
  </div>
</div>'''

new_login = '''<!-- ══════════════ LOGIN SCREEN ══════════════ -->
<div id="login-screen">
  <div class="login-box" style="width:480px;">
    <div class="login-logo"><div class="logo-icon">🛡</div><div class="logo-text">SecureWealth Twin</div></div>
    <div class="wizard-steps">
      <div class="wizard-step active" id="step-dot-1">1</div>
      <div class="wizard-step-line"></div>
      <div class="wizard-step" id="step-dot-2">2</div>
      <div class="wizard-step-line"></div>
      <div class="wizard-step" id="step-dot-3">3</div>
    </div>
    <div id="wizard-step-1" class="wizard-page">
      <div class="login-title">Who are you?</div>
      <div class="login-sub">Let\'s personalize your experience</div>
      <div class="form-group"><label class="form-label">Full Name</label><input class="form-input" id="f-name" placeholder="Priya Sharma" type="text"></div>
      <div class="form-group"><label class="form-label">Age</label><input class="form-input" id="f-age" placeholder="28" type="number" min="18" max="80"></div>
      <div class="form-group"><label class="form-label">Investment Experience</label>
        <select class="form-input" id="f-exp">
          <option value="none">None — Just getting started</option>
          <option value="beginner" selected>Beginner — Basic knowledge</option>
          <option value="intermediate">Intermediate — Some experience</option>
        </select>
      </div>
      <button class="btn-primary" onclick="nextWizardStep()">Continue →</button>
      <div class="login-divider">or</div>
      <button class="demo-btn" onclick="fillDemo()">🚀 Use Demo Profile</button>
    </div>
    <div id="wizard-step-2" class="wizard-page" style="display:none;">
      <div class="login-title">Your finances</div>
      <div class="login-sub">We use this to personalize your advice</div>
      <div class="form-group"><label class="form-label">Monthly Income (₹)</label><input class="form-input" id="f-income" placeholder="55000" type="number"></div>
      <div class="form-group"><label class="form-label">Monthly Expenses (₹)</label><input class="form-input" id="f-expenses" placeholder="35000" type="number"></div>
      <div class="form-group"><label class="form-label">Current Savings (₹)</label><input class="form-input" id="f-savings" placeholder="120000" type="number"></div>
      <div class="form-group"><label class="form-label">Existing Investments (₹)</label><input class="form-input" id="f-investments" placeholder="60000" type="number"></div>
      <div style="display:flex;gap:10px;"><button class="demo-btn" style="width:auto;padding:12px 20px;" onclick="prevWizardStep()">← Back</button><button class="btn-primary" onclick="nextWizardStep()">Continue →</button></div>
    </div>
    <div id="wizard-step-3" class="wizard-page" style="display:none;">
      <div class="login-title">Your goals</div>
      <div class="login-sub">What are you building wealth for?</div>
      <div class="form-group"><label class="form-label">Primary Goal</label>
        <select class="form-input" id="f-goal">
          <option value="Buy a house">🏠 Buy a House</option>
          <option value="Retirement planning">🌴 Retirement Planning</option>
          <option value="Children\'s education">📚 Children\'s Education</option>
          <option value="Build emergency fund">🛡 Emergency Fund</option>
          <option value="Start a business">💼 Start a Business</option>
          <option value="Wealth building">📈 General Wealth Building</option>
        </select>
      </div>
      <div class="form-group"><label class="form-label">Goal Timeline (years)</label><input class="form-input" id="f-timeline" placeholder="7" type="number" min="1" max="40"></div>
      <div class="form-group"><label class="form-label">Risk Appetite</label>
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:4px;">
          <div class="risk-choice" id="risk-low" onclick="selectRisk(\'low\')"><div style="font-size:18px;margin-bottom:4px;">🛡</div><div style="font-size:12px;font-weight:600;">Low</div><div style="font-size:10px;color:var(--text-muted);">Safe &amp; stable</div></div>
          <div class="risk-choice active" id="risk-medium" onclick="selectRisk(\'medium\')"><div style="font-size:18px;margin-bottom:4px;">⚖️</div><div style="font-size:12px;font-weight:600;">Medium</div><div style="font-size:10px;color:var(--text-muted);">Balanced</div></div>
          <div class="risk-choice" id="risk-high" onclick="selectRisk(\'high\')"><div style="font-size:18px;margin-bottom:4px;">🚀</div><div style="font-size:12px;font-weight:600;">High</div><div style="font-size:10px;color:var(--text-muted);">Growth focused</div></div>
        </div>
      </div>
      <div style="display:flex;gap:10px;"><button class="demo-btn" style="width:auto;padding:12px 20px;" onclick="prevWizardStep()">← Back</button><button class="btn-primary" id="submit-btn" onclick="submitProfile()">🧬 Analyze My Profile</button></div>
    </div>
    <div id="wizard-loading" style="display:none;text-align:center;padding:40px 0;">
      <div style="font-size:48px;margin-bottom:16px;animation:shield-pulse 1s ease-in-out infinite;">🧬</div>
      <div style="font-family:var(--font-display);font-size:18px;font-weight:700;margin-bottom:8px;" id="loading-text">Analyzing your profile...</div>
      <div style="font-size:13px;color:var(--text-muted);">Building your Financial DNA</div>
      <div style="margin-top:20px;display:flex;justify-content:center;gap:4px;"><div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div></div>
    </div>
    <div style="margin-top:16px;font-size:11px;color:var(--text-muted);text-align:center;">🔒 Simulation &amp; demo purposes only. Not real financial advice.</div>
  </div>
</div>'''

html = html.replace(old_login, new_login)

with open('frontend/index.html', 'w') as f:
    f.write(html)

found = new_login[:50] in html
print("Login replaced:", new_login[:50] in open('frontend/index.html').read())
