import re
import textwrap
from typing import List, Dict, Optional
from .models import CoreIdea


def sanitize_filename(name: str) -> str:
    """清理文件名中的非法字符"""
    name = name.replace(":", "——").replace("：", "——")
    name = re.sub(r'[\\/*?"<>|？。，！!]', "_", name)
    name = name.replace("*", "")
    return name.strip()


def extract_summary_title(markdown_text: str) -> str:
    """从合成文章中提取一级标题作为标题"""
    match = re.search(r"^#\s*(.*?)(?:\n|\Z)", markdown_text, re.MULTILINE)
    if match:
        return match.group(1).strip().strip("*")
    return "未命名总结"


def parse_core_ideas_response(
    response_text: str, metadata: Optional[Dict] = None
) -> List[CoreIdea]:
    """
    深度解析 AI 返回的核心思想块。
    支持字段提取、格式标准化重组，并可选注入参考资料。
    """
    # 匹配 ## 核心思想卡n
    card_start_pattern = re.compile(r"^## 核心思想卡\d+.*", re.MULTILINE)
    matches = list(card_start_pattern.finditer(response_text))

    core_ideas: List[CoreIdea] = []
    required_fields = ["思辨点", "内容分析", "思辨结论", "金句"]

    for i, match in enumerate(matches):
        start = match.start()
        next_start = (
            matches[i + 1].start() if i + 1 < len(matches) else len(response_text)
        )
        block = response_text[start:next_start]

        # 1. 提取 ID 和 标题 (###)
        id_match = re.search(r"##\s*(核心思想卡\d+)", block)
        title_match = re.search(r"^###\s*(.*?)(?:\n|\Z)", block, re.MULTILINE)

        if not (id_match and title_match):
            continue

        idea_id = id_match.group(1).strip()
        raw_title = title_match.group(1).strip().strip("*")
        # 去除标题前缀
        title = re.sub(r"^(核心命题|核心思想)[：:]\s*", "", raw_title)

        # 2. 提取并清理各个字段内容
        sections = {}
        is_valid = True
        for field in required_fields:
            # 兼容加粗和冒号
            field_pattern = rf"^- \*\*({field})\*\*：(.*?)(?=\n- \*\*|\n##|\n#|\Z)"
            f_match = re.search(field_pattern, block, re.DOTALL | re.MULTILINE)
            if f_match:
                sections[field] = f_match.group(2).strip()
            else:
                is_valid = False
                break

        if not is_valid:
            continue

        # 3. 标准化重组 (Reconstruction)
        display_title = title.replace("——", "：")
        output_lines = [
            f"### {display_title}",
            "",
            f"- **思辨点**：{sections['思辨点']}",
            "",
        ]

        # 内容分析缩进处理
        analysis_clean = textwrap.dedent(sections["内容分析"]).strip()
        if "\n" in analysis_clean:
            indented_analysis = textwrap.indent(analysis_clean, "  ")
            output_lines.append(f"- **内容分析**：\n{indented_analysis}")
        else:
            output_lines.append(f"- **内容分析**：{analysis_clean}")

        output_lines.append("")
        output_lines.append(f"- **思辨结论**：{sections['思辨结论']}")
        output_lines.append("")
        output_lines.append(f"- **金句**：{sections['金句']}")

        # 4. 可选注入参考资料
        if metadata:
            output_lines.append("")
            output_lines.append("### 参考资料 ：")
            output_lines.append("")
            output_lines.append(
                f"- 《{metadata['book']}》 ({metadata['author']}) : {metadata['chapter']}"
            )
        idea_dict: CoreIdea = {
            "title": title,
            "core_idea": "\n".join(output_lines).strip() + "\n",
            "motifs": [],
        }
        core_ideas.append(idea_dict)

    return core_ideas
