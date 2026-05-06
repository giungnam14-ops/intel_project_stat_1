import re

file_path = r'C:\Users\User\.gemini\antigravity\brain\4de9a517-477b-49fa-b81e-43641c491e07\.system_generated\steps\31\content.md'
output_path = r'c:\Users\User\Desktop\프로젝트1\intel_project_stat_1-main\scratch\map_data.js'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

matches = re.findall(r'<path d="(.*?)" id="(.*?)"', content)
if not matches:
    matches = re.findall(r'<path id="(.*?)" d="(.*?)"', content)
    matches = [(d, i) for i, d in matches]

districts = []
for d, i in matches:
    districts.append({
        'name': i,
        'path': d
    })

with open(output_path, 'w', encoding='utf-8') as f:
    f.write("const SEOUL_MAP_DATA = [\n")
    for dist in districts:
        f.write(f"    {{ name: '{dist['name']}', path: '{dist['path']}' }},\n")
    f.write("];\n")
