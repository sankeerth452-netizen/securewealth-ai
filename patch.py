
with open('frontend/index.html', 'r') as f:
    html = f.read()

# 1. Add IDs to sidebar user card
html = html.replace(
    '<div class="user-avatar">P</div>\n        <div class="user-info">\n          <div class="user-name">Priya Sharma</div>\n          <div class="user-role">Steady Planner</div>',
    '<div class="user-avatar" id="sidebar-avatar">P</div>\n        <div class="user-info">\n          <div class="user-name" id="sidebar-name">...</div>\n          <div class="user-role" id="sidebar-role">Loading...</div>'
)

# 2. Add ID to alerts badge
html = html.replace(
    '<span style="margin-left:auto;background:var(--red);color:white;font-size:10px;padding:2px 7px;border-radius:10px;font-weight:700;">3</span>',
    '<span id="alert-badge" style="margin-left:auto;background:var(--red);color:white;font-size:10px;padding:2px 7px;border-radius:10px;font-weight:700;display:none;">0</span>'
)

# 3. Dashboard greeting
html = html.replace(
    '<div class="page-title">Good morning, Priya 👋</div>',
    '<div class="page-title" id="dash-greeting">Good morning 👋</div>'
)

# 4. DNA card IDs
html = html.replace(
    '<div class="dna-archetype">Steady Planner</div>\n          <div class="dna-desc">Consistent saver with medium risk appetite, focused on long-term goals</div>\n          <div class="dna-tags">\n            <span class="dna-tag">Savings Rate 36.4%</span>\n            <span class="dna-tag">Medium Risk</span>\n            <span class="dna-tag">7-Year Horizon</span>\n            <span class="dna-tag">Beginner Investor</span>\n          </div>',
    '<div class="dna-archetype" id="dash-archetype">Loading...</div>\n          <div class="dna-desc" id="dash-desc">Analyzing your profile...</div>\n          <div class="dna-tags" id="dash-tags"></div>'
)

# 5. Stats row IDs
html = html.replace('<div class="card-value">₹3.2L</div>\n          <div class="card-delta">↑ +12.4% this year</div>', '<div class="card-value" id="dash-networth">...</div>\n          <div class="card-delta" id="dash-nw-delta">Your total wealth</div>')
html = html.replace('<div class="card-value">₹55K</div>\n          <div class="card-delta" style="color:var(--text-secondary)">Salaried</div>', '<div class="card-value" id="dash-income">...</div>\n          <div class="card-delta" style="color:var(--text-secondary)">Monthly Income</div>')
html = html.replace('<div class="card-value">₹20K</div>\n          <div class="card-delta">↑ 36.4% savings rate</div>', '<div class="card-value" id="dash-monthly-savings">...</div>\n          <div class="card-delta" id="dash-savings-rate">Monthly Savings</div>')
html = html.replace('<div class="card-value" style="color:var(--teal)">LOW</div>\n          <div class="card-delta">🛡 All clear today</div>', '<div class="card-value" style="color:var(--teal)" id="dash-risk-level">LOW</div>\n          <div class="card-delta" id="dash-risk-delta">🛡 All clear today</div>')

# 6. Goals container ID
html = html.replace(
    '<!-- Goals -->\n        <div class="card">\n          <div class="section-title">Goals Progress</div>\n          <div class="goal-item">',
    '<!-- Goals -->\n        <div class="card">\n          <div class="section-title">Goals Progress</div>\n          <div id="dash-goals"><div class="goal-item">'
)
html = html.replace(
    '<div class="goal-meta"><span>₹25K saved</span><span>₹1L target</span></div>\n          </div>\n        </div>',
    '<div class="goal-meta"><span>₹25K saved</span><span>₹1L target</span></div>\n          </div></div>\n        </div>'
)

# 7. Risk shield ID
html = html.replace(
    '<div class="risk-shield-widget shield-low">\n            <div class="shield-icon">🛡️</div>\n            <div class="shield-score">LOW</div>\n            <div class="shield-level">All Clear</div>\n          </div>\n          <div class="pyramid-grid">',
    '<div class="risk-shield-widget shield-low" id="dash-shield-widget">\n            <div class="shield-icon">🛡️</div>\n            <div class="shield-score" id="dash-shield-score">LOW</div>\n            <div class="shield-level" id="dash-shield-level">All Clear</div>\n          </div>\n          <div class="pyramid-grid" id="dash-pyramid">'
)

# 8. AI Insights container ID
html = html.replace(
    '<div class="section-title">AI Insights</div>\n          <div class="stat-row">\n            <div class="stat-row-label">💡 <span>Start a ₹5,000/month SIP now</span></div>',
    '<div class="section-title">AI Insights</div>\n          <div id="dash-insights"><div class="stat-row">\n            <div class="stat-row-label">💡 <span>Loading AI insights...</span></div>'
)
html = html.replace(
    '<span class="tag tag-blue">Opportunity</span>\n          </div>\n          <div class="stat-row">\n            <div class="stat-row-label">🎯 <span>On track for house goal by 2031</span></div>\n            <span class="tag tag-green">On Track</span>\n          </div>',
    '<span class="tag tag-blue">Opportunity</span>\n          </div></div>'
)

# 9. Portfolio breakdown ID
html = html.replace(
    '<div class="section-title">Portfolio Breakdown</div>\n          <div class="stat-row">\n            <div class="stat-row-label"><span style="width:10px;height:10px;background:var(--teal);border-radius:50%;display:inline-block;margin-right:4px;"></span> Savings Account</div>',
    '<div class="section-title">Portfolio Breakdown</div>\n          <div id="dash-portfolio"><div class="stat-row">\n            <div class="stat-row-label"><span style="width:10px;height:10px;background:var(--teal);border-radius:50%;display:inline-block;margin-right:4px;"></span> Savings Account</div>'
)
html = html.replace(
    '<div class="stat-row-value">₹60,000</div>\n          </div>\n        </div>\n      </div>\n    </div>',
    '<div class="stat-row-value">₹60,000</div>\n          </div></div>\n        </div>\n      </div>\n    </div>'
, 1)

# 10. Chat welcome message ID
html = html.replace(
    'Hi Priya! 👋 I\'m your SecureWealth Coach. I know your profile — ₹55K income, goal to buy a house in 7 years, medium risk appetite.<br><br>\n                  How can I help you grow and protect your wealth today?',
    '<span id="chat-welcome-msg">Hi! 👋 I\'m your SecureWealth Coach. How can I help you grow and protect your wealth today?</span>'
)

# 11. Chat sidebar profile IDs
html = html.replace(
    '<div class="stat-row-value" style="font-size:13px;">₹55,000/mo</div>',
    '<div class="stat-row-value" style="font-size:13px;" id="chat-profile-income">...</div>'
)
html = html.replace(
    '<div class="stat-row-value" style="font-size:13px;">Medium</div>',
    '<div class="stat-row-value" style="font-size:13px;" id="chat-profile-risk">...</div>'
)
html = html.replace(
    '<div class="stat-row-value" style="font-size:13px; max-width:120px; text-align:right;">House in 7yr</div>',
    '<div class="stat-row-value" style="font-size:13px; max-width:120px; text-align:right;" id="chat-profile-goal">...</div>'
)

# 12. Net worth page IDs
html = html.replace('<div class="card-value" style="color:var(--teal)">₹3,20,000</div>\n          <div class="card-delta">Across 4 categories</div>', '<div class="card-value" style="color:var(--teal)" id="nw-total-assets">...</div>\n          <div class="card-delta" id="nw-assets-cats">Calculating...</div>')
html = html.replace('<div class="card-value" style="color:var(--red)">₹0</div>\n          <div class="card-delta" style="color:var(--teal)">✓ Debt free</div>', '<div class="card-value" style="color:var(--red)" id="nw-total-liabilities">...</div>\n          <div class="card-delta" id="nw-liabilities-note" style="color:var(--teal)">Calculating...</div>')
html = html.replace('<div class="card-value" style="color:var(--gold)">₹3,20,000</div>\n          <div class="card-delta" style="color:var(--gold)">↑ Growing steadily</div>', '<div class="card-value" style="color:var(--gold)" id="nw-net-worth">...</div>\n          <div class="card-delta" style="color:var(--gold)" id="nw-growth-note">Growing steadily</div>')
html = html.replace(
    '<div class="section-title">Assets Breakdown</div>\n          <div class="stat-row">\n            <div class="stat-row-label">🏦 Savings Account</div>',
    '<div class="section-title">Assets Breakdown</div>\n          <div id="nw-breakdown"><div class="stat-row">\n            <div class="stat-row-label">🏦 Savings Account</div>'
)
html = html.replace(
    '<div class="stat-row-value" style="color:var(--text-muted)">Not added</div>\n          </div>\n          <div class="stat-row">\n            <div class="stat-row-label">🚗 Vehicle</div>\n            <div class="stat-row-value" style="color:var(--text-muted)">Not added</div>\n          </div>\n          <button class="btn-sm" style="width:100%;margin-top:16px;">+ Add Asset</button>',
    '<div class="stat-row-value" style="color:var(--text-muted)">Not added</div>\n          </div></div>'
)
# Health score ID
html = html.replace(
    '>78</div>\n            <div style="font-size:16px;color:var(--teal);font-weight:600;margin-top:4px;">Good</div>\n            <div style="font-size:13px;color:var(--text-secondary);margin-top:8px;">You\'re on the right track!</div>',
    ' id="nw-health-score">78</div>\n            <div style="font-size:16px;color:var(--teal);font-weight:600;margin-top:4px;" id="nw-health-status">Good</div>\n            <div style="font-size:13px;color:var(--text-secondary);margin-top:8px;" id="nw-health-msg">You\'re on the right track!</div>'
)

# 13. Risk alerts page IDs
html = html.replace('<div class="card-value">12</div>\n          <div class="card-delta">This session</div>', '<div class="card-value" id="alert-total">0</div>\n          <div class="card-delta">This session</div>')
html = html.replace('<div class="card-value" style="color:var(--amber)">2</div>\n          <div class="card-delta" style="color:var(--amber);">Reviewed by you</div>', '<div class="card-value" style="color:var(--amber)" id="alert-warns">0</div>\n          <div class="card-delta" style="color:var(--amber);">Reviewed by you</div>')
html = html.replace('<div class="card-value" style="color:var(--red)">1</div>\n          <div class="card-delta" style="color:var(--red)">Protected ₹1,00,000</div>', '<div class="card-value" style="color:var(--red)" id="alert-blocks">0</div>\n          <div class="card-delta" style="color:var(--red)" id="alert-protected">Protected ₹0</div>')
html = html.replace(
    '<div class="section-title">Audit Log</div>\n\n        <div class="alert-item alert-block">',
    '<div class="section-title">Audit Log</div>\n        <div id="audit-log-container"><div style="padding:20px;text-align:center;color:var(--text-muted);font-size:13px;">Loading audit log...</div></div>\n        <div style="display:none"><div class="alert-item alert-block">'
)
html = html.replace(
    '<div class="alert-score" style="color:var(--teal)">0</div>\n        </div>\n\n      </div>\n    </div>',
    '<div class="alert-score" style="color:var(--teal)">0</div>\n        </div></div>\n\n      </div>\n    </div>'
)

# 14. Profile page IDs
html = html.replace('<div class="profile-avatar">P</div>', '<div class="profile-avatar" id="prof-avatar">P</div>')
html = html.replace('<div class="profile-name">Priya Sharma</div>', '<div class="profile-name" id="prof-name">...</div>')
html = html.replace('<div class="profile-role">Steady Planner · Joined April 2026</div>', '<div class="profile-role" id="prof-role">Loading...</div>')
html = html.replace(
    '<span class="tag tag-green">✓ KYC Verified (Demo)</span>\n            <span class="tag tag-blue">Medium Risk</span>\n            <span class="tag tag-amber">Beginner Investor</span>',
    '<span class="tag tag-green" id="prof-badge-kyc">✓ KYC Verified (Demo)</span>\n            <span class="tag tag-blue" id="prof-badge-risk">Medium Risk</span>\n            <span class="tag tag-amber" id="prof-badge-exp">Beginner Investor</span>'
)
html = html.replace('<div class="stat-row-value">28 years</div>', '<div class="stat-row-value" id="prof-age">...</div>')
html = html.replace('<div class="stat-row-value">₹55,000</div>', '<div class="stat-row-value" id="prof-income">...</div>')
html = html.replace('<div class="stat-row-value">₹35,000</div>', '<div class="stat-row-value" id="prof-expenses">...</div>')
html = html.replace('<div class="stat-row-value">Buy a House</div>', '<div class="stat-row-value" id="prof-goal">...</div>')
html = html.replace('<div class="stat-row-value">7 years</div>', '<div class="stat-row-value" id="prof-timeline">...</div>')
html = html.replace('<div class="stat-row-value">Medium</div>', '<div class="stat-row-value" id="prof-risk">...</div>')
html = html.replace('<div style="font-size:14px;font-weight:500;">💻 MacBook Air</div>', '<div style="font-size:14px;font-weight:500;" id="prof-device">💻 This Device</div>')
html = html.replace('<div style="font-size:14px;font-weight:500;">Today, 2:20 AM</div>', '<div style="font-size:14px;font-weight:500;" id="prof-login-time">Just now</div>')
html = html.replace('<div style="font-size:14px;font-weight:500;">🛡 LOW</div>\n            <div style="margin-top:6px;"><span class="tag tag-green">All clear</span></div>', '<div style="font-size:14px;font-weight:500;" id="prof-session-risk">🛡 LOW</div>\n            <div style="margin-top:6px;" id="prof-session-tag"><span class="tag tag-green">All clear</span></div>')

with open('frontend/index.html', 'w') as f:
    f.write(html)

print("HTML IDs patched successfully")
