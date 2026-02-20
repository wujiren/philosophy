import os
import re
import textwrap
from openai import OpenAI
import dotenv

dotenv.load_dotenv()


def get_essay_motifs(content, article_content):
    client = OpenAI(
        api_key=os.environ.get("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com"
    )

    prompt = """## 任务
你的任务是根据用户输入的哲学命题及其对应的原文内容，**提炼2-3个最核心、最具思辨张力**的高考议论文母题。

## 输入说明
1. **核心思想卡**：提炼出的哲学命题、内容分析、思辨结论及金句。
2. **原文内容**：该命题所对应的详细背景和论述。

## 母题分析规范
每个母题的分析必须包含以下五个部分，请严格遵循各模块的功能定位：

### 母题一：[母题标题]
- **破题角度：**
    【功能：确立视角】结合原文及核心思想，提供一个新颖、深刻的分析视角，将抽象的核心思想转化为可展开的论述起点。破题应揭示问题的深层结构，而非简单复述现象。
    
- **思辨性提问：**
    【功能：深化矛盾】围绕核心思辨点，提出1-2个具有启发性的问题。**问题应保持开放性，只问不答**，引导学生思考核心矛盾的不同侧面。问题应从破题角度自然延伸，形成递进逻辑。
    
- **立意进阶：**
    【功能：哲学回应】针对上述问题，从哲学层面提供一种具有深度的思考方向或观点回应。**进阶应给出观点，而非再提问题**。要实现从“现象分析”到“哲学思考”的跃升，展现个人的思想见解。

## 
## 思辨张力参考库
（保留您原有的张力列表，供AI参考）
| 母题领域 | 内在的思辨张力（矛盾双方） | 需要你思辨的问题 |
| :--- | :--- | :--- |
| **个人与时代** | 个体意志 vs. 时代洪流 | 人是时代的产物，还是时代的创造者？是顺势而为，还是逆流而上？ |
| **传统与创新** | 守正（根） vs. 出奇（新） | 传统是创新的包袱，还是创新的土壤？如何在尊重规律中实现突破？ |
| **科技与人文** | 工具理性（效率） vs. 价值理性（意义） | 科技让生活更美好，还是让人更异化？效率和温度可以兼得吗？ |
| **处世与品格** | 出世（淡泊） vs. 入世（担当） | 独善其身与兼济天下，哪个更有价值？在复杂的世界如何坚守本心？ |

## 其他要求
- 请务必结合“原文内容”中更丰富的论述细节，使得母题与核心思想卡高度契合。
- **母题数量控制在2-3个，确保每个母题都紧扣核心思想，宁缺毋滥。**
- 母题需要体现思辨张力，建议参考上述思辨张力库。
- “破题角度”和“立意进阶”应具有深度，避免泛泛而谈。

## 输出示例
```
### 母题一：[母题标题]
- **破题角度：**
   [破题角度分析]

- **思辨性提问：**
   [思辨性提问分析]

- **立意进阶：**
   [立意进阶分析]

## 母题二：
...
```    
"""

    user_content = f"### 核心思想卡\n{content}\n\n### 原文内容\n{article_content}"

    response = client.chat.completions.create(
        model="deepseek-reasoner",
        messages=[
            {
                "role": "system",
                "content": prompt,
            },
            {"role": "user", "content": user_content},
        ],
        stream=False,
    )

    return response.choices[0].message.content


def extract_motif_content(response):
    """
    1. 查找所有以 '### 母题' 开头的板块。
    2. 校验每个板块是否包含：破题角度、思辨性提问、立意进阶。
    3. 重新拼装标准格式，统一 2 空格缩进，字段间加空行，剔除杂质。
    """
    # 匹配所有母题板块
    motif_blocks = re.split(r"(?=###\s*母题)", response)
    valid_motifs = []
    required_fields = ["破题角度", "思辨性提问", "立意进阶"]
    for block in motif_blocks:
        if not block.strip() or "### 母题" not in block:
            continue
        # 提取标题
        title_match = re.search(r"###\s*(母题.*?)(?:\n|\Z)", block)
        if not title_match:
            continue
        title = title_match.group(1).strip()
        # 提取各个字段
        sections = {}
        for field in required_fields:
            # 兼容中英文冒号，匹配到下一个字段开始或板块结束
            pattern = rf"-\s*\*\*({field})\s*[：:]\s*\*\*(.*?)(?=\n-\s*\*\*|\n###|\Z)"
            alt_pattern = (
                rf"-\s*\*\*({field})\*\*\s*[：:]\s*(.*?)(?=\n-\s*\*\*|\n###|\Z)"
            )
            f_match = re.search(pattern, block, re.DOTALL) or re.search(
                alt_pattern, block, re.DOTALL
            )
            if f_match:
                sections[field] = f_match.group(2).strip()
        # 重新拼装标准格式
        reconstructed = [f"### {title}"]
        for field in required_fields:
            content = sections.get(field, "（未提取到内容）")
            # 逐行清理，解决缩进不统一问题
            lines = [l.strip() for l in content.splitlines() if l.strip()]
            content_clean = "\n".join(lines)
            if content_clean:
                # 统一采用：换行 + 2空格缩进 的格式
                indented_content = textwrap.indent(content_clean, "  ")
                reconstructed.append(f"- **{field}：**\n{indented_content}")
            else:
                reconstructed.append(f"- **{field}：** （未提取到内容）")
        # 使用 \n\n 连接确保字段间有空行
        valid_motifs.append("\n\n".join(reconstructed))
    return valid_motifs


if __name__ == "__main__":
    base_dir = "dataset/philosophical_proposition/核心思想卡"
    save_dir = "dataset/philosophical_proposition/母题"
    articles_dir = "dataset/articals"
    os.makedirs(save_dir, exist_ok=True)

    for file_name in os.listdir(base_dir):
        if not file_name.endswith(".md"):
            continue

        file_path = os.path.join(base_dir, file_name)
        with open(file_path, "r", encoding="utf-8") as f:
            full_content = f.read()

        # 提取参考资料
        # 匹配格式：### 参考资料 ：
        #
        # - 西方现代思想讲义(刘擎)：38.泰勒 如何“成为你自己”
        ref_match = re.search(
            r"### 参考资料\s*[:：]\s*\n\s*-\s*(.*?)\((.*?)\)[:：]\s*(.*)", full_content
        )

        article_content = ""
        clean_content = full_content

        if ref_match:
            book = ref_match.group(1).strip()
            author = ref_match.group(2).strip()
            chapter = ref_match.group(3).strip()

            # 去除参考资料部分的内容作为核心思想卡内容
            clean_content = full_content[: ref_match.start()].strip()

            # 读取原文
            article_filename = f"{chapter}.md"
            article_path = os.path.join(articles_dir, article_filename)

            if os.path.exists(article_path):
                with open(article_path, "r", encoding="utf-8") as af:
                    article_content = af.read()
            else:
                print(f"警告：未找到原文文件 {article_path}")
        else:
            print(f"注意：文件 {file_name} 未能解析出参考资料")

        print(f"正在处理: {file_name}...")
        response = get_essay_motifs(clean_content, article_content)
        final_response = "\n\n".join(extract_motif_content(response))
        save_path = os.path.join(save_dir, file_name)
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(final_response)
        print(f"已保存: {save_path}")
