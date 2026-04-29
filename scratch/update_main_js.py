import os

js_file = r'c:\Users\User\Desktop\프로젝트1\intel_project_stat_1-main\static\js\main.js'
data_file = r'c:\Users\User\Desktop\프로젝트1\intel_project_stat_1-main\scratch\map_data.js'

with open(js_file, 'r', encoding='utf-8') as f:
    js_content = f.readlines()

with open(data_file, 'r', encoding='utf-8') as f:
    new_data = f.read()

# Find the start and end of SEOUL_MAP_DATA
start_line = -1
end_line = -1

for i, line in enumerate(js_content):
    if 'const SEOUL_MAP_DATA = [' in line:
        start_line = i
    if start_line != -1 and '];' in line and i > start_line:
        end_line = i
        break

if start_line != -1 and end_line != -1:
    new_content = js_content[:start_line] + [new_data] + js_content[end_line+1:]
    
    # Also update label logic
    full_new_content = "".join(new_content)
    
    # Update regex for coordinates
    old_regex = r"const coords = d.path.match\(/\\d\+,\d\+/g\).map\(c => c.split\(','\).map\(Number\)\);"
    new_regex = r"const coords = d.path.match(/[\d.]+\s+[\d.]+/g).map(c => c.trim().split(/\s+/).map(Number));"
    
    # Actually, let's be more precise with the replacement
    full_new_content = full_new_content.replace(
        "const coords = d.path.match(/(\\d+),(\\d+)/g).map(c => c.split(',').map(Number));",
        "const coords = d.path.match(/[\\d.]+\\s+[\\d.]+/g).map(c => c.trim().split(/\\s+/).map(Number));"
    )
    
    with open(js_file, 'w', encoding='utf-8') as f:
        f.write(full_new_content)
    print("Successfully updated main.js")
else:
    print("Could not find SEOUL_MAP_DATA block")
