import os
import re
import sys

# 确保能导入 src.utils.parsers
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.utils.parsers import parse_core_ideas_response, sanitize_filename

def split_core_ideas(source_dir, dest_dir):
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    for filename in sorted(os.listdir(source_dir)):
        if not filename.endswith(".md"):
            continue

        file_path = os.path.join(source_dir, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 模拟 metadata 注入参考资料
        chapter_name = os.path.splitext(filename)[0]
        metadata = {
            "book": "西方现代思想讲义",
            "author": "刘擎",
            "chapter": chapter_name
        }

        # 调用统一的解析逻辑
        parsed_ideas = parse_core_ideas_response(content, metadata=metadata)
        
        if not parsed_ideas:
            continue

        prefix = chapter_name
        for i, idea in enumerate(parsed_ideas, 1):
            # 保存独立卡片
            safe_title = sanitize_filename(idea["title"])
            new_filename = f"{safe_title}.md"
            dest_path = os.path.join(dest_dir, new_filename)

            # 防止重名
            if os.path.exists(dest_path):
                new_filename = f"{prefix}-{new_filename}"
                dest_path = os.path.join(dest_dir, new_filename)

            with open(dest_path, "w", encoding="utf-8") as f:
                f.write(idea["content"])

        # 更新原始文件：移除已提取的部分 (这里保留原有的移除逻辑)
        # 简单起见，如果解析成功了，我们可以认为这些块需要被移除
        # 实际操作中，split_core_ideas 通常是为了清理“提炼”目录
        card_start_pattern = re.compile(r"^## 核心思想卡\d+.*", re.MULTILINE)
        new_original_content = content
        
        # 倒序移除以保证索引不变
        matches = list(card_start_pattern.finditer(content))
        for i in range(len(matches) - 1, -1, -1):
            start = matches[i].start()
            end = matches[i+1].start() if i+1 < len(matches) else len(content)
            # 如果这个块在 parsed_ideas 中（说明解析成功），则移除
            # 这里简单处理为全部移除解析成功的块
            new_original_content = new_original_content[:start] + new_original_content[end:]

        new_original_content = re.sub(r"\n{3,}", "\n\n", new_original_content).strip()
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_original_content)

        print(f"Processed {len(parsed_ideas)} cards from {filename}")

if __name__ == "__main__":
    source = "dataset/philosophical_proposition/核心思想提炼"
    dest = "dataset/philosophical_proposition/核心思想卡"
    split_core_ideas(source, dest)

    for file_name in os.listdir(source):
        with open(os.path.join(source, file_name), "r", encoding="utf-8") as f:
            content = f.read()
            if content.strip():
                print(content)
