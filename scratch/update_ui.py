import os

file_path = '/Users/sankeerthlatheesh/PycharmProject/securewealth-ai/frontend/index.html'

with open(file_path, 'r') as f:
    lines = f.readlines()

new_head = """<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<script src="https://cdn.tailwindcss.com"></script>
<script>
  tailwind.config = {
    theme: {
      extend: {
        fontFamily: {
          sans: ['Inter', 'sans-serif'],
        },
        colors: {
          apple: {
            bg: '#fbfbfb',
            card: '#ffffff',
            text: '#1d1d1f',
            muted: '#86868b',
            blue: '#0071e3',
            teal: '#00d4aa',
            border: '#d2d2d7',
          }
        },
        borderRadius: {
          'apple': '20px',
          'apple-sm': '12px',
        }
      }
    }
  }
</script>
<style>
  body { 
    background-color: #fbfbfb; 
    -webkit-font-smoothing: antialiased;
    color: #1d1d1f;
  }
  .glass {
    background: rgba(255, 255, 255, 0.72);
    backdrop-filter: saturate(180%) blur(20px);
    -webkit-backdrop-filter: saturate(180%) blur(20px);
  }
  .page { display: none; transition: opacity 0.4s ease, transform 0.4s ease; opacity: 0; transform: translateY(10px); }
  .page.active { display: block; opacity: 1; transform: translateY(0); }
  
  .fade-in-up {
    animation: fadeInUp 0.8s cubic-bezier(0.4, 0, 0.2, 1) forwards;
  }
  @keyframes fadeInUp {
    from { opacity: 0; transform: translateY(30px); }
    to { opacity: 1; transform: translateY(0); }
  }

  ::-webkit-scrollbar { width: 5px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb { background: #d2d2d7; border-radius: 10px; }
  
  .bank-card-gradient {
    background: linear-gradient(135deg, #1d1d1f 0%, #434343 100%);
  }
</style>
</head>
<body class="font-sans antialiased bg-apple-bg text-apple-text">
"""

# Find the start of line 7 and end of line 1622
# Actually, I'll just find the range from <link to </body>
start_idx = -1
end_idx = -1

for i, line in enumerate(lines):
    if '<link href="https://fonts.googleapis.com/css2?family=Syne' in line:
        start_idx = i
    if '</body>' in line:
        # We want to replace everything up to body tag
        pass

# Since I know the lines from view_file:
# Line 7: <link ...
# Line 1622: </style>
# Line 1623: <body>

# Replace lines 7 to 1623 (1-indexed)
# In 0-indexed: lines[6:1623]
new_lines = lines[:6] + [new_head] + lines[1623:]

with open(file_path, 'w') as f:
    f.writelines(new_lines)

print("SUCCESS: index.html updated head and styles.")
