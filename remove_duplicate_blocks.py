import os
import re

def remove_duplicate_blocks(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Оставляем только первый {% extends %}
    extends_tags = list(re.finditer(r'{%\s*extends\s+["\'][^"\']+["\']\s*%}', content))
    if len(extends_tags) > 1:
        first_end = extends_tags[0].end()
        content = content[:first_end] + re.sub(
            r'{%\s*extends\s+["\'][^"\']+["\']\s*%}\s*', '',
            content[first_end:]
        )

    # Оставляем только первую пару {% block content %}…{% endblock %}
    block_pattern = r'{%\s*block\s+content\s*%}'
    endblock_pattern = r'{%\s*endblock\s*%}'
    starts = [m.start() for m in re.finditer(block_pattern, content)]
    if len(starts) > 1:
        new_content = []
        idx = 0
        first_start = starts[0]
        new_content.append(content[:first_start])
        match = re.search(endblock_pattern, content[first_start:])
        first_end = first_start + (match.end() if match else 0)
        new_content.append(content[first_start:first_end])
        idx = first_end
        for start in starts[1:]:
            rel = re.search(endblock_pattern, content[start:])
            if rel:
                end = start + rel.end()
                if idx < start:
                    new_content.append(content[idx:start])
                idx = max(idx, end)
        new_content.append(content[idx:])
        content = ''.join(new_content)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    templates_dir = os.path.join(os.getcwd(), 'templates')
    for root, _, files in os.walk(templates_dir):
        for file in files:
            if file.endswith('.html'):
                path = os.path.join(root, file)
                remove_duplicate_blocks(path)
                print(f'Processed {path}')

if __name__ == '__main__':
    main()
