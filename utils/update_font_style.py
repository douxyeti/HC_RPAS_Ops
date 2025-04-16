import os
import re

def update_font_style(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remplacer font_style="H5" par font_style="Headline"
    updated_content = re.sub(r'font_style="H[0-9]"', 'font_style="Headline"', content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)

screens_dir = os.path.join('app', 'views', 'screens')
for file in os.listdir(screens_dir):
    if file.endswith('_dashboard_screen.py'):
        file_path = os.path.join(screens_dir, file)
        update_font_style(file_path)
        print(f"Updated {file}")
