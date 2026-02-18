import os
import re

def sanitize_filename(name):
    # Replace colons with dashes as requested
    name = name.replace(':', '——').replace('：', '——')
    # Remove characters that are generally problematic in filenames
    return re.sub(r'[\\/*?"<>|？。，！!]', '_', name).strip()

def split_core_ideas(source_dir, dest_dir):
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    # This regex matches from "## 核心思想卡" to the start of the next one or the end of the file.
    card_pattern = re.compile(r'(^## 核心思想卡\d+.*?)(?=\n## 核心思想卡\d+|\Z)', re.MULTILINE | re.DOTALL)
    # This regex extracts the proposition title
    prop_pattern = re.compile(r'### \**核心命题：\**(.*?)(?:\n|\Z)')

    for filename in os.listdir(source_dir):
        if not filename.endswith('.md'):
            continue

        file_path = os.path.join(source_dir, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        matches = list(card_pattern.finditer(content))
        if not matches:
            continue

        # Get the numeric prefix from original filename (e.g., "05")
        name_parts = filename.split('.', 1)
        prefix = name_parts[0] if len(name_parts) == 2 else os.path.splitext(filename)[0]

        # Re-iterating in normal order for saving
        for i, match in enumerate(matches, 1):
            full_card_content = match.group(1).strip()
            
            # Remove the "## 核心思想卡x" line from the beginning of the extracted content
            card_content_no_header = re.sub(r'^## 核心思想卡\d+\s*', '', full_card_content, count=1).strip()
            
            # Extract proposition for filename
            prop_match = prop_pattern.search(full_card_content)
            if prop_match:
                proposition = prop_match.group(1).strip().strip('*')
                safe_prop = sanitize_filename(proposition)
                new_filename = f"{safe_prop}.md"
            else:
                new_filename = f"{prefix}-{i}.md"
            
            dest_path = os.path.join(dest_dir, new_filename)
            with open(dest_path, 'w', encoding='utf-8') as f:
                f.write(card_content_no_header)
            print(f"Created: {dest_path}")

        # Now remove them from the original content
        new_original_content = content
        for match in reversed(matches):
            start, end = match.span()
            new_original_content = new_original_content[:start] + new_original_content[end:]
        
        # Strip extra whitespace and write back to original file
        new_original_content = new_original_content.strip()
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_original_content)
        print(f"Updated original: {file_path}")

if __name__ == "__main__":
    source = 'dataset/philosophical_proposition/核心思想卡'
    dest = 'dataset/philosophical_proposition/核心思想卡2'
    split_core_ideas(source, dest)
