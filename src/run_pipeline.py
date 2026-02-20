import os
import re
from langfuse import Langfuse
import dotenv


from .utils.models import PhilosophyStudyUnit
from .parse_content.core_idea import get_core_idea_card
from .parse_content.essay_motif import get_essay_motifs, extract_motif_content
from .parse_content.summary import get_summary
from .utils.parsers import parse_core_ideas_response, extract_summary_title

# 加载环境变量
dotenv.load_dotenv()

# 初始化 Langfuse 客户端
langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST"),
)
langfuse.auth_check()


def run_pipeline(
    book: str, author: str, chapter: str, article_text: str
) -> PhilosophyStudyUnit:
    print(f">>> 开始处理章节: {chapter}")

    # 创建根 Trace
    with langfuse.start_as_current_observation(
        name="Philosophy_Pipeline",
        metadata={"book": book, "chapter": chapter},
        as_type="trace",
    ) as root_span:

        unit: PhilosophyStudyUnit = {
            "metadata": {"book": book, "author": author, "chapter": chapter},
            "original_article": article_text,
            "core_ideas": [],
        }

        # 1. 提炼核心思想
        print("  [Step 1] 正在提炼核心思想卡...")
        with root_span.start_as_current_observation(
            name="Core_Idea_Generation", as_type="generation"
        ):
            raw_ideas_response = get_core_idea_card(article_text)

        # 注入元数据，让解析器自动生成标准格式和参考资料
        metadata = unit["metadata"]
        parsed_ideas = parse_core_ideas_response(raw_ideas_response, metadata=metadata)

        for idea_dict in parsed_ideas:
            unit["core_ideas"].append(idea_dict)
            print(f"  找到 {len(unit['core_ideas'])} 个核心思想点。")

        # 2. 生成母题
        for idea in unit["core_ideas"]:
            print(f"  [Step 2] 正在为 '{idea['title']}' 生成母题...")
            with root_span.start_as_current_observation(
                name="Motif_Generation",
                metadata={"idea_title": idea["title"]},
                as_type="generation",
            ):
                raw_motifs_response = get_essay_motifs(idea["core_idea"], article_text)

            # extract_motif_content 返回列表
            cleaned_motifs_list = extract_motif_content(raw_motifs_response)

            if cleaned_motifs_list:
                # 构建内存对象
                idea["motifs"] = []
                for m_content in cleaned_motifs_list:
                    t_match = re.search(r"###\s*(.*?)(?:\n|\Z)", m_content)
                    full_title = t_match.group(1).strip() if t_match else "未命名母题"
                    sep = ":" if ":" in full_title else ":"
                    if sep in full_title:
                        m_id, m_title = full_title.split(sep, 1)
                    else:
                        m_id, m_title = "母题", full_title

                    idea["motifs"].append(
                        {
                            "id": m_id.strip(),
                            "title": m_title.strip(),
                            "motif": m_content.strip(),
                        }
                    )
            else:
                print(f"    警告: 无法为 '{idea['title']}' 解析出母题内容")

        # 3. 最终总结与合成
        for idea in unit["core_ideas"]:
            print(f"  [Step 3] 正在合成综述文章: {idea['title']}...")
            with root_span.start_as_current_observation(
                name="Summary_Synthesis",
                metadata={"idea_title": idea["title"]},
                as_type="generation",
            ):
                # 拼装所有母题文本
                all_motifs_text = "\n\n".join([m["motif"] for m in idea["motifs"]])
                final_md = get_summary(article_text, idea["core_idea"], all_motifs_text)

            # 解析最终标题并注入脚注
            ref_footer = f"\n\n---\n**参考资料**：\n- 《{book}》 ({author}) : {chapter}"
            final_md += ref_footer
            summary = {"title": extract_summary_title(final_md), "summary": final_md}
            idea["summary"] = summary

    langfuse.flush()
    return unit
