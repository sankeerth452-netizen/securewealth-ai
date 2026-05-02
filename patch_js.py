import re

def main():
    with open('frontend/index.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # Replacements:
    # 1. fetch(`${API}/api/ai/networth`  -> safeFetch(`/api/ai/networth`
    # and remove .json() calls directly tied to them.

    # Find and replace specific blocks to use safeFetch
    # Example:
    # const res = await fetch(`${API}/api/execute/audit`);
    # const data = await res.json();
    # -> const data = await safeFetch(`/api/execute/audit`);
    
    content = re.sub(
        r'const res = await fetch\(`\$\{API\}(/api/execute/audit)`\);\s*(?:if \(!res\.ok\) throw new Error\(.*?\);\s*)?const data = await res\.json\(\);',
        r'const data = await safeFetch(`\1`);\n    if (data && data.error) throw new Error(data.message);',
        content
    )

    content = re.sub(
        r'const res = await fetch\(`\$\{API\}(/api/execute/audit)`\);\s*if \(res\.ok\) \{\s*const data = await res\.json\(\);',
        r'const data = await safeFetch(`\1`);\n    if (data && !data.error) {\n',
        content
    )

    content = re.sub(
        r'const res = await fetch\(`\$\{API\}(/api/simulate/fraud)`,\s*\{\s*method:\s*\'POST\',\s*headers:\s*\{.*?\}\s*\}\);\s*const data = await res\.json\(\);',
        r'const data = await safeFetch(`\1`, {\n      method: \'POST\'\n    });',
        content
    )

    content = re.sub(
        r'const res = await fetch\(`\$\{API\}(/api/execute)`,\s*\{\s*method:\s*\'POST\',\s*headers:\s*\{.*?\},\s*body:\s*(JSON\.stringify\(\{.*?\})\s*\}\s*\}\);\s*const data = await res\.json\(\);',
        r'const data = await safeFetch(`\1`, {\n      method: \'POST\',\n      body: \2\n    });',
        content,
        flags=re.DOTALL
    )

    content = re.sub(
        r'const res = await fetch\(`\$\{API\}(/api/ai/chat)`,\s*\{\s*method:\s*\'POST\',\s*headers:\s*\{.*?\},\s*body:\s*(JSON\.stringify\(\{.*?\})\s*\}\s*\}\);\s*const data = await res\.json\(\);',
        r'const data = await safeFetch(`\1`, {\n        method: \'POST\',\n        body: \2\n      });',
        content,
        flags=re.DOTALL
    )

    content = re.sub(
        r'const res = await fetch\(`\$\{API\}(/api/ai/networth)`,\s*\{\s*method:\s*"POST",\s*headers:\s*\{.*?\},\s*body:\s*(JSON\.stringify\(\{.*?\})\s*\}\s*\}\);\s*const data = await res\.json\(\);',
        r'const data = await safeFetch(`\1`, {\n      method: "POST",\n      body: \2\n    });',
        content,
        flags=re.DOTALL
    )
    
    content = re.sub(
        r'const res = await fetch\(`\$\{API\}(/api/ai/simulate)`,\s*\{\s*method:\s*"POST",\s*headers:\s*\{.*?\},\s*body:\s*(JSON\.stringify\(\{.*?\})\s*\}\s*\}\);\s*const data = await res\.json\(\);',
        r'const data = await safeFetch(`\1`, {\n    method: "POST",\n    body: \2\n  });',
        content,
        flags=re.DOTALL
    )

    content = re.sub(
        r'fetch\(`\$\{API\}(/api/ai/chat)`,\s*\{\s*method:\s*\'POST\',\s*headers:\s*\{.*?\},\s*body:\s*(JSON\.stringify\(\{.*?\})\s*\}\s*\}\)\.then\(r => r\.json\(\)\)',
        r'safeFetch(`\1`, {\n    method: \'POST\',\n    body: \2\n  })',
        content,
        flags=re.DOTALL
    )

    with open('frontend/index.html', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    main()
