import os

file_path = '/Users/sankeerthlatheesh/PycharmProject/securewealth-ai/frontend/index.html'

with open(file_path, 'r') as f:
    lines = f.readlines()

new_body_content = """
  <div id="login-screen" class="bg-apple-bg fixed inset-0 z-[100] flex items-center justify-center p-6">
    <div class="login-box glass border border-apple-border shadow-2xl p-12 rounded-apple max-w-md w-full fade-in-up">
      <div class="flex items-center gap-3 mb-10">
        <div class="w-10 h-10 bg-apple-text rounded-apple-sm flex items-center justify-center text-white text-xl shadow-inner">🛡</div>
        <div class="text-2xl font-bold tracking-tight">SecureWealth</div>
      </div>

      <!-- Step 1 -->
      <div id="wizard-step-1">
        <h1 class="text-4xl font-extrabold mb-2 tracking-tight text-apple-text">Who are you?</h1>
        <p class="text-apple-muted mb-8 text-lg">Personalize your AI wealth experience.</p>
        
        <div class="space-y-5">
          <div>
            <label class="text-[10px] font-bold uppercase tracking-widest text-apple-muted mb-2 block">Full Name</label>
            <input type="text" id="f-name" class="w-full bg-apple-bg border border-apple-border rounded-apple-sm px-4 py-3 focus:outline-none focus:ring-1 focus:ring-apple-text transition-all text-apple-text" placeholder="John Appleseed">
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="text-[10px] font-bold uppercase tracking-widest text-apple-muted mb-2 block">Age</label>
              <input type="number" id="f-age" class="w-full bg-apple-bg border border-apple-border rounded-apple-sm px-4 py-3 focus:outline-none focus:ring-1 focus:ring-apple-text transition-all text-apple-text" placeholder="25">
            </div>
            <div>
              <label class="text-[10px] font-bold uppercase tracking-widest text-apple-muted mb-2 block">Experience</label>
              <select id="f-exp" class="w-full bg-apple-bg border border-apple-border rounded-apple-sm px-4 py-3 focus:outline-none focus:ring-1 focus:ring-apple-text transition-all text-apple-text appearance-none">
                <option value="none">None</option>
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="expert">Expert</option>
              </select>
            </div>
          </div>
        </div>
        <button onclick="nextWizardStep()" class="w-full bg-apple-text text-white py-4 rounded-apple-sm font-bold mt-10 hover:opacity-90 active:scale-[0.98] transition-all">Continue</button>
        <div class="text-center mt-6">
          <button onclick="fillDemo()" class="text-apple-muted text-xs hover:text-apple-text transition-colors uppercase tracking-widest font-bold">Demo Setup</button>
        </div>
      </div>

      <!-- Step 2 -->
      <div id="wizard-step-2" style="display:none;">
        <h1 class="text-4xl font-extrabold mb-2 tracking-tight text-apple-text text-center">Your finances</h1>
        <p class="text-apple-muted mb-10 text-center">We use this to secure your wealth in real-time.</p>
        <div class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="text-[10px] font-bold uppercase tracking-widest text-apple-muted mb-2 block">Monthly Income</label>
              <input type="number" id="f-income" class="w-full bg-apple-bg border border-apple-border rounded-apple-sm px-4 py-3 focus:outline-none focus:ring-1 focus:ring-apple-text transition-all text-apple-text">
            </div>
            <div>
              <label class="text-[10px] font-bold uppercase tracking-widest text-apple-muted mb-2 block">Expenses</label>
              <input type="number" id="f-expenses" class="w-full bg-apple-bg border border-apple-border rounded-apple-sm px-4 py-3 focus:outline-none focus:ring-1 focus:ring-apple-text transition-all text-apple-text">
            </div>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="text-[10px] font-bold uppercase tracking-widest text-apple-muted mb-2 block">Current Savings</label>
              <input type="number" id="f-savings" class="w-full bg-apple-bg border border-apple-border rounded-apple-sm px-4 py-3 focus:outline-none focus:ring-1 focus:ring-apple-text transition-all text-apple-text">
            </div>
            <div>
              <label class="text-[10px] font-bold uppercase tracking-widest text-apple-muted mb-2 block">Investments</label>
              <input type="number" id="f-investments" class="w-full bg-apple-bg border border-apple-border rounded-apple-sm px-4 py-3 focus:outline-none focus:ring-1 focus:ring-apple-text transition-all text-apple-text">
            </div>
          </div>
        </div>
        <div class="flex gap-4 mt-12">
          <button onclick="prevWizardStep()" class="flex-1 border border-apple-border py-4 rounded-apple-sm font-bold hover:bg-black/[0.03] transition-all text-apple-text">Back</button>
          <button onclick="nextWizardStep()" class="flex-1 bg-apple-text text-white py-4 rounded-apple-sm font-bold hover:opacity-90 active:scale-[0.98] transition-all">Continue</button>
        </div>
      </div>

      <!-- Step 3 -->
      <div id="wizard-step-3" style="display:none;">
        <h1 class="text-4xl font-extrabold mb-2 tracking-tight text-apple-text">Your goals</h1>
        <p class="text-apple-muted mb-10">Define what you're building wealth for.</p>
        <div class="space-y-6">
          <div>
            <label class="text-[10px] font-bold uppercase tracking-widest text-apple-muted mb-2 block">Primary Goal</label>
            <input type="text" id="f-goal" class="w-full bg-apple-bg border border-apple-border rounded-apple-sm px-4 py-3 focus:outline-none focus:ring-1 focus:ring-apple-text transition-all text-apple-text" placeholder="Retire at 45">
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="text-[10px] font-bold uppercase tracking-widest text-apple-muted mb-2 block">Timeline (Years)</label>
              <input type="number" id="f-timeline" class="w-full bg-apple-bg border border-apple-border rounded-apple-sm px-4 py-3 focus:outline-none focus:ring-1 focus:ring-apple-text transition-all text-apple-text">
            </div>
            <div>
              <label class="text-[10px] font-bold uppercase tracking-widest text-apple-muted mb-2 block">Risk Appetite</label>
              <div class="flex gap-1 bg-apple-bg p-1 border border-apple-border rounded-apple-sm">
                <button id="risk-low" onclick="selectRisk('low')" class="flex-1 py-2 rounded-[8px] text-xs font-bold transition-all hover:bg-white hover:shadow-sm">Low</button>
                <button id="risk-medium" onclick="selectRisk('medium')" class="flex-1 py-2 rounded-[8px] text-xs font-bold bg-white shadow-sm">Med</button>
                <button id="risk-high" onclick="selectRisk('high')" class="flex-1 py-2 rounded-[8px] text-xs font-bold transition-all hover:bg-white hover:shadow-sm">High</button>
              </div>
            </div>
          </div>
        </div>
        <div class="flex gap-4 mt-12">
          <button onclick="prevWizardStep()" class="flex-1 border border-apple-border py-4 rounded-apple-sm font-bold hover:bg-black/[0.03] transition-all text-apple-text">Back</button>
          <button onclick="submitProfile()" class="flex-1 bg-apple-text text-white py-4 rounded-apple-sm font-bold hover:opacity-90 active:scale-[0.98] transition-all">Finish</button>
        </div>
      </div>

      <!-- Progress Dots -->
      <div class="flex justify-center gap-2 mt-12">
        <div id="step-dot-1" class="w-1.5 h-1.5 rounded-full bg-apple-border transition-all duration-300 [&.active]:w-4 [&.active]:bg-apple-text active"></div>
        <div id="step-dot-2" class="w-1.5 h-1.5 rounded-full bg-apple-border transition-all duration-300 [&.active]:w-4 [&.active]:bg-apple-text"></div>
        <div id="step-dot-3" class="w-1.5 h-1.5 rounded-full bg-apple-border transition-all duration-300 [&.active]:w-4 [&.active]:bg-apple-text"></div>
      </div>
    </div>

    <!-- Fullscreen Loading -->
    <div id="wizard-loading" style="display:none;" class="fixed inset-0 z-[110] bg-white flex flex-col items-center justify-center p-6 text-center">
      <div class="relative w-24 h-24 mb-10">
        <div class="absolute inset-0 border-[6px] border-apple-bg rounded-full"></div>
        <div class="absolute inset-0 border-[6px] border-t-apple-text rounded-full animate-spin"></div>
      </div>
      <h2 class="text-4xl font-extrabold mb-4 tracking-tight">Creating your vault</h2>
      <p class="text-xl text-apple-muted max-w-sm leading-relaxed">Securing your financial data with industrial-grade encryption.</p>
    </div>
  </div>

  <div id="app" class="hidden min-h-screen bg-apple-bg">
    <!-- Navbar Sidebar -->
    <aside class="w-[260px] glass border-r border-apple-border fixed inset-y-0 left-0 z-50 flex flex-col p-8">
      <div class="flex items-center gap-3 mb-16">
        <div class="w-9 h-9 bg-apple-text rounded-apple-sm flex items-center justify-center text-white text-xl shadow-lg">🛡</div>
        <div class="text-xl font-bold tracking-tight">SecureWealth</div>
      </div>

      <nav class="flex-1 space-y-2">
        <div class="text-[10px] font-bold uppercase tracking-widest text-apple-muted mb-6 px-3 opacity-60">Portfolio</div>
        <button onclick="switchPage('dashboard', this)" class="nav-item active flex items-center gap-4 w-full px-4 py-3 rounded-apple-sm text-[15px] font-semibold transition-all hover:bg-black/5 [&.active]:bg-black/5 [&.active]:text-apple-text text-apple-muted">
          <span class="text-lg opacity-60">▣</span> Dashboard
        </button>
        <button onclick="switchPage('chat', this)" class="nav-item flex items-center gap-4 w-full px-4 py-3 rounded-apple-sm text-[15px] font-semibold transition-all hover:bg-black/5 text-apple-muted">
          <span class="text-lg opacity-60">💬</span> AI Coach
        </button>
        <button onclick="switchPage('transfer', this)" id="nav-transfer" class="nav-item flex items-center gap-4 w-full px-4 py-3 rounded-apple-sm text-[15px] font-semibold transition-all hover:bg-black/5 text-apple-muted">
          <span class="text-lg opacity-60">↑</span> Transfer
        </button>
        <button onclick="switchPage('simulator', this)" class="nav-item flex items-center gap-4 w-full px-4 py-3 rounded-apple-sm text-[15px] font-semibold transition-all hover:bg-black/5 text-apple-muted">
          <span class="text-lg opacity-60">📊</span> Simulator
        </button>

        <div class="pt-8 mb-6">
          <div class="text-[10px] font-bold uppercase tracking-widest text-apple-muted mb-6 px-3 opacity-60">Protection</div>
          <button onclick="switchPage('alerts', this)" class="nav-item flex items-center gap-4 w-full px-4 py-3 rounded-apple-sm text-[15px] font-semibold transition-all hover:bg-black/5 text-apple-muted">
            <span class="text-lg opacity-60">🛡</span> Risk Shield
          </button>
        </div>
      </nav>

      <div class="mt-auto pt-8 border-t border-apple-border">
        <div class="flex items-center gap-4 px-3 cursor-pointer group" onclick="switchPage('profile', this)">
          <div id="sidebar-avatar" class="w-10 h-10 bg-apple-text text-white rounded-full flex items-center justify-center text-sm font-bold shadow-md transition-transform group-hover:scale-105">P</div>
          <div class="min-width-0">
            <div id="sidebar-name" class="text-sm font-bold truncate text-apple-text">Priya Sharma</div>
            <div id="sidebar-role" class="text-[11px] text-apple-muted font-medium truncate uppercase tracking-tighter">Wealth Architect</div>
          </div>
        </div>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="ml-[260px] flex-1 p-16 max-w-[1400px] mx-auto">
      
      <!-- DASHBOARD PAGE -->
      <div id="page-dashboard" class="page active">
        <header class="mb-20 fade-in-up">
          <div class="flex justify-between items-end mb-4">
            <h1 id="dash-greeting" class="text-7xl font-extrabold tracking-tight text-apple-text">Good morning.</h1>
            <div class="text-right">
                <div class="text-[11px] font-bold uppercase tracking-widest text-apple-muted mb-1">Status</div>
                <div class="flex items-center gap-2 text-apple-teal font-bold">
                    <span class="w-2 h-2 rounded-full bg-apple-teal animate-pulse"></span>
                    Protected by AI
                </div>
            </div>
          </div>
          <p class="text-2xl text-apple-muted font-medium max-w-2xl leading-relaxed">Your financial ecosystem is performing optimally and secured by Cortex Shield.</p>
        </header>

        <!-- Dynamic Bento Grid -->
        <div class="grid grid-cols-12 gap-8 mb-20">
          <div class="col-span-8 bg-white rounded-apple border border-apple-border p-12 shadow-sm hover:shadow-xl transition-all duration-500 group fade-in-up" style="animation-delay: 0.1s;">
            <div class="flex justify-between items-start mb-12">
              <div>
                <div class="text-[10px] font-bold uppercase tracking-widest text-apple-muted mb-6 opacity-60">Current Net Worth</div>
                <div id="dash-networth" class="text-8xl font-extrabold tracking-tighter text-apple-text mb-4">₹3,42,000</div>
              </div>
              <div class="bg-apple-bg rounded-apple-sm px-4 py-2 text-apple-teal font-bold text-sm shadow-sm group-hover:scale-105 transition-transform">↑ +₹12.4k</div>
            </div>
            
            <div class="grid grid-cols-3 gap-8 pt-10 border-t border-apple-border/50">
              <div>
                <div class="text-[10px] font-bold uppercase tracking-widest text-apple-muted mb-3">Savings</div>
                <div id="dash-savings" class="text-2xl font-bold text-apple-text">₹1,20,000</div>
              </div>
              <div>
                <div class="text-[10px] font-bold uppercase tracking-widest text-apple-muted mb-3">Monthly Income</div>
                <div id="dash-income" class="text-2xl font-bold text-apple-text">₹85,000</div>
              </div>
              <div>
                <div class="text-[10px] font-bold uppercase tracking-widest text-apple-muted mb-3">Savings Rate</div>
                <div id="dash-savings-rate" class="text-2xl font-bold text-apple-teal">32%</div>
              </div>
            </div>
          </div>

          <div class="col-span-4 flex flex-col gap-8">
            <div class="bg-apple-text text-white rounded-apple p-10 shadow-2xl relative overflow-hidden group fade-in-up" style="animation-delay: 0.2s;">
              <div class="relative z-10">
                <div class="text-[10px] font-bold uppercase tracking-widest opacity-40 mb-6">AI Profile</div>
                <div id="dash-archetype" class="text-4xl font-extrabold mb-4 tracking-tight">Bold Grower</div>
                <p id="dash-desc" class="text-sm opacity-70 leading-relaxed font-medium">Prioritizing expansion while maintaining high-liquidity reserves.</p>
                <div id="dash-tags" class="flex flex-wrap gap-2 mt-8"></div>
              </div>
              <!-- Abstract decoration -->
              <div class="absolute -right-12 -bottom-12 w-48 h-48 bg-white/10 rounded-full blur-3xl group-hover:scale-125 transition-transform duration-700"></div>
            </div>

            <div class="bg-white rounded-apple border border-apple-border p-10 shadow-sm hover:shadow-md transition-all fade-in-up" style="animation-delay: 0.3s;">
                <div class="text-[10px] font-bold uppercase tracking-widest text-apple-muted mb-6">Security Score</div>
                <div class="flex items-end justify-between">
                    <div id="dash-behavior-score" class="text-6xl font-extrabold tracking-tighter text-apple-text">84</div>
                    <div class="text-[10px] font-bold text-apple-muted mb-2">Excellent</div>
                </div>
                <div class="w-full bg-apple-bg h-1.5 rounded-full mt-6 overflow-hidden">
                    <div class="bg-apple-teal h-full w-[84%] rounded-full shadow-[0_0_8px_rgba(0,212,170,0.4)]"></div>
                </div>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-12 gap-10">
          <div class="col-span-8 space-y-10">
            <!-- Asset Allocation Section -->
            <section class="fade-in-up" style="animation-delay: 0.4s;">
                <div class="flex items-center justify-between mb-8">
                    <h3 class="text-3xl font-extrabold tracking-tight text-apple-text">Asset Allocation</h3>
                    <button class="text-apple-blue font-bold text-sm hover:underline">Rebalance Portfolio</button>
                </div>
                <div id="dash-portfolio" class="bg-white rounded-apple border border-apple-border overflow-hidden shadow-sm">
                    <!-- Populated by JS -->
                </div>
            </section>

            <!-- Intelligence Feed -->
            <section class="fade-in-up" style="animation-delay: 0.5s;">
                <div class="flex items-center justify-between mb-8">
                    <h3 class="text-3xl font-extrabold tracking-tight text-apple-text">Intelligence Feed</h3>
                    <div class="text-xs font-bold text-apple-muted px-3 py-1 bg-apple-bg rounded-full">Real-time Analysis</div>
                </div>
                <div id="activity-feed" class="space-y-4">
                    <!-- Populated by JS -->
                </div>
            </section>
          </div>

          <aside class="col-span-4 space-y-10 fade-in-up" style="animation-delay: 0.6s;">
            <!-- Quick Actions -->
            <div class="bg-white rounded-apple border border-apple-border p-10 shadow-sm">
                <h4 class="text-[10px] font-bold uppercase tracking-widest text-apple-muted mb-8">Quick Actions</h4>
                <div class="space-y-4">
                    <button onclick="switchPage('transfer', document.getElementById('nav-transfer'))" class="w-full flex items-center justify-between p-4 rounded-apple-sm hover:bg-apple-bg transition-all group">
                        <div class="flex items-center gap-4">
                            <span class="w-10 h-10 rounded-full bg-apple-bg flex items-center justify-center text-lg group-hover:scale-110 transition-transform">↑</span>
                            <span class="font-bold text-sm">Move Capital</span>
                        </div>
                        <span class="text-apple-muted opacity-0 group-hover:opacity-100 transition-opacity">→</span>
                    </button>
                    <button onclick="switchPage('chat', this)" class="w-full flex items-center justify-between p-4 rounded-apple-sm hover:bg-apple-bg transition-all group">
                        <div class="flex items-center gap-4">
                            <span class="w-10 h-10 rounded-full bg-apple-bg flex items-center justify-center text-lg group-hover:scale-110 transition-transform">💬</span>
                            <span class="font-bold text-sm">Ask AI Coach</span>
                        </div>
                        <span class="text-apple-muted opacity-0 group-hover:opacity-100 transition-opacity">→</span>
                    </button>
                    <button onclick="simulateFraud()" class="w-full flex items-center justify-between p-4 rounded-apple-sm hover:bg-red-50 transition-all group">
                        <div class="flex items-center gap-4 text-red-500">
                            <span class="w-10 h-10 rounded-full bg-red-50 flex items-center justify-center text-lg group-hover:scale-110 transition-transform">🛡️</span>
                            <span class="font-bold text-sm">Simulate Attack</span>
                        </div>
                        <span class="text-red-300 opacity-0 group-hover:opacity-100 transition-opacity">→</span>
                    </button>
                </div>
            </div>

            <!-- Risk Shield Monitor -->
            <div class="bg-white rounded-apple border border-apple-border p-10 shadow-sm text-center">
                <div class="text-[10px] font-bold uppercase tracking-widest text-apple-muted mb-8">Risk Shield</div>
                <div id="dash-risk-level" class="text-6xl font-extrabold text-apple-teal tracking-tighter mb-4">LOW</div>
                <div id="dash-risk-delta" class="text-xs font-bold text-apple-muted bg-apple-bg px-4 py-2 rounded-full inline-block">72h No Threats</div>
                
                <div id="dash-pyramid" class="grid grid-cols-2 gap-3 mt-10">
                    <div class="pyramid-item active p-4 bg-apple-bg rounded-apple-sm border border-apple-border/50 text-center">
                        <div class="pyr-dot w-2 h-2 rounded-full bg-apple-teal mx-auto mb-3 shadow-[0_0_8px_rgba(0,212,170,0.5)]"></div>
                        <div class="pyr-label text-[10px] font-bold uppercase tracking-widest opacity-60">Identity</div>
                    </div>
                    <div class="pyramid-item active p-4 bg-apple-bg rounded-apple-sm border border-apple-border/50 text-center">
                        <div class="pyr-dot w-2 h-2 rounded-full bg-apple-teal mx-auto mb-3 shadow-[0_0_8px_rgba(0,212,170,0.5)]"></div>
                        <div class="pyr-label text-[10px] font-bold uppercase tracking-widest opacity-60">Context</div>
                    </div>
                    <div class="pyramid-item active p-4 bg-apple-bg rounded-apple-sm border border-apple-border/50 text-center">
                        <div class="pyr-dot w-2 h-2 rounded-full bg-apple-teal mx-auto mb-3 shadow-[0_0_8px_rgba(0,212,170,0.5)]"></div>
                        <div class="pyr-label text-[10px] font-bold uppercase tracking-widest opacity-60">Behavior</div>
                    </div>
                    <div class="pyramid-item active p-4 bg-apple-bg rounded-apple-sm border border-apple-border/50 text-center">
                        <div class="pyr-dot w-2 h-2 rounded-full bg-apple-teal mx-auto mb-3 shadow-[0_0_8px_rgba(0,212,170,0.5)]"></div>
                        <div class="pyr-label text-[10px] font-bold uppercase tracking-widest opacity-60">Intent</div>
                    </div>
                </div>
            </div>
          </aside>
        </div>
      </div>

      <!-- CHAT PAGE -->
      <div id="page-chat" class="page h-[calc(100vh-8rem)] flex flex-col fade-in-up">
        <header class="mb-12">
          <h1 class="text-5xl font-extrabold tracking-tight text-apple-text">Wealth Coach</h1>
          <p class="text-xl text-apple-muted font-medium mt-2">Personalized intelligence for your financial future.</p>
        </header>
        <div id="chat-messages" class="flex-1 overflow-y-auto space-y-8 pr-6 custom-scrollbar">
          <!-- Messages dynamically populated -->
        </div>
        <div class="mt-12 relative max-w-4xl mx-auto w-full group">
          <input type="text" id="chat-input" class="w-full bg-white border border-apple-border rounded-full px-10 py-6 text-lg focus:outline-none focus:ring-2 focus:ring-apple-text/5 shadow-lg transition-all" placeholder="Ask about your net worth or simulate a SIP...">
          <button id="send-btn" onclick="sendChat()" class="absolute right-4 top-4 w-12 h-12 bg-apple-text text-white rounded-full flex items-center justify-center text-xl hover:scale-105 active:scale-95 transition-all shadow-xl">↑</button>
        </div>
      </div>

      <!-- TRANSFER PAGE -->
      <div id="page-transfer" class="page fade-in-up">
        <header class="mb-16">
          <h1 class="text-5xl font-extrabold tracking-tight text-apple-text">Deploy Capital</h1>
          <p class="text-xl text-apple-muted font-medium mt-2">Move funds securely through Cortex Shield.</p>
        </header>
        
        <div class="grid grid-cols-12 gap-12">
            <div class="col-span-7">
                <div class="bg-white rounded-apple border border-apple-border p-12 shadow-sm">
                    <div class="space-y-8">
                      <div>
                        <label class="text-[10px] font-bold uppercase tracking-widest text-apple-muted mb-3 block">Recipient Account Name</label>
                        <input type="text" id="tx-recipient" class="w-full bg-apple-bg border border-apple-border rounded-apple-sm px-6 py-4 text-lg focus:outline-none focus:ring-1 focus:ring-apple-text transition-all" placeholder="Enter full name">
                      </div>
                      <div class="grid grid-cols-2 gap-8">
                        <div>
                            <label class="text-[10px] font-bold uppercase tracking-widest text-apple-muted mb-3 block">Account Number</label>
                            <input type="text" id="tx-account" class="w-full bg-apple-bg border border-apple-border rounded-apple-sm px-6 py-4 text-lg focus:outline-none transition-all" placeholder="···· ···· ···· 1234">
                        </div>
                        <div>
                            <label class="text-[10px] font-bold uppercase tracking-widest text-apple-muted mb-3 block">Amount (₹)</label>
                            <input type="number" id="tx-amount" class="w-full bg-apple-bg border border-apple-border rounded-apple-sm px-6 py-4 text-lg font-bold text-apple-text focus:outline-none transition-all" placeholder="0.00">
                        </div>
                      </div>
                      <div class="pt-8 border-t border-apple-border/50 flex items-center justify-between">
                          <div class="text-sm text-apple-muted font-medium">Real-time risk assessment active</div>
                          <button onclick="initiateTransfer()" class="bg-apple-text text-white px-10 py-5 rounded-apple-sm font-bold text-lg hover:opacity-90 active:scale-95 transition-all shadow-xl">Verify & Transfer</button>
                      </div>
                    </div>
                </div>
            </div>
            
            <div class="col-span-5">
                <div class="bank-card-gradient rounded-apple p-10 text-white shadow-2xl min-h-[260px] flex flex-col justify-between mb-8">
                    <div class="flex justify-between items-start">
                        <div class="text-xl font-bold italic tracking-tighter opacity-80">NOVA Platinum</div>
                        <div class="w-12 h-8 bg-white/20 rounded-apple-sm backdrop-blur-md"></div>
                    </div>
                    <div>
                        <div class="text-sm opacity-50 uppercase tracking-widest mb-1">Source Account</div>
                        <div id="bc-number" class="text-2xl font-mono tracking-[0.3em] mb-8">···· ···· ···· 4821</div>
                        <div class="flex justify-between items-end">
                            <div>
                                <div class="text-[10px] opacity-40 uppercase tracking-widest mb-1">Account Holder</div>
                                <div id="bc-name" class="text-lg font-bold">Priya Sharma</div>
                            </div>
                            <div class="text-right">
                                <div class="text-[10px] opacity-40 uppercase tracking-widest mb-1">Available Liquidity</div>
                                <div id="bc-balance" class="text-2xl font-bold">₹1,20,000</div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="bg-white rounded-apple border border-apple-border p-8 shadow-sm">
                    <h5 class="text-[10px] font-bold uppercase tracking-widest text-apple-muted mb-6">Security Context</h5>
                    <ul class="space-y-4">
                        <li class="flex items-center gap-3 text-sm font-medium">
                            <span class="text-apple-teal">●</span> Identity Verified (Biometrics)
                        </li>
                        <li class="flex items-center gap-3 text-sm font-medium">
                            <span class="text-apple-teal">●</span> Location Authorized (Home)
                        </li>
                        <li class="flex items-center gap-3 text-sm font-medium opacity-40">
                            <span>○</span> Behavioral Pattern Alignment
                        </li>
                    </ul>
                </div>
            </div>
        </div>
      </div>

    </main>
  </div>
"""

# Find line 68 (<body>) and start of script
# Script usually starts around line 2296 (now maybe different)
start_line_idx = 68 # 0-indexed is 67
end_line_idx = -1

for i, line in enumerate(lines):
    if i > start_line_idx and '// ── CHARTS ──' in line:
        end_line_idx = i
        break

# In view_file output, // ── CHARTS ── was at 1498
# But since I replaced 1616 lines with ~70 lines, it should be much earlier.
# Let's re-find it.
if end_line_idx == -1:
    # Try searching for the function start
    for i, line in enumerate(lines):
        if 'function updateDashboardChart' in line:
            end_line_idx = i
            break

print(f"DEBUG: start_line_idx={start_line_idx}, end_line_idx={end_line_idx}")

new_lines = lines[:start_line_idx] + [new_body_content] + lines[end_line_idx:]

with open(file_path, 'w') as f:
    f.writelines(new_lines)

print("SUCCESS: index.html body overhauled.")
