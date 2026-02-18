import os
from openai import OpenAI
import dotenv
import json

dotenv.load_dotenv()


def get_core_idea_card(content):

    client = OpenAI(
        api_key=os.environ.get("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com"
    )
    prompt = """## 任务
你的任务是根据用户输入的`原文`以及多个根据`原文`提炼的`哲学命题`，从原文中提炼`核心思想卡`

## 核心思想卡
核心思想卡的形式如下：
```
## 核心思想卡1
### [核心思想的标题，如“世界的祛魅”：清醒后的荒凉]
- **思辨点**：[思辨点的具体内容，通常表现为一种辩证关系的陈述]
- **内容分析**：
    - [思辨的分析思辨点的几个方面]
- **思辨结论**：[综合正反两面得出的结论性观点，可加粗强调]
- **金句**：[原文中关于该命题的最具代表性的句子]

## 核心思想卡2
...
```

## 其他说明
- 核心思想卡的标题应准确概括该思想的核心内容，具有吸引力和概括性。
- 思辨点要有辩证性，体现对立统一的关系。
- 内容分析需从多个方面展开，并得出思辨结论。
- 金句需直接引用原文中最能体现该思想的句子。
- 不需要考虑`原文`中`思考题`相关的内容

## 示例
```
## 核心思想卡1
### “世界的祛魅”：清醒后的荒凉
-   **思辨点**：理性驱散了愚昧，但也带走了意义。
-   **内容分析**：
    -   **正面（得/进步）**：祛魅是人类文明的“梦醒时分”。它用科学理性驱散了迷信和巫术，让人们从对神秘力量的恐惧和依赖中解放出来。人不再需要向神灵祈求答案，而是可以通过自己的理性去认识和改造世界。这是现代科学和社会进步的基础。
    -   **反面（失/困境）**：梦醒之后的世界是“荒凉”的。当世界被还原为冷冰冰的物理规律（如H2O只是水，日食只是天体现象），人与世界那种有机的、充满意义的联系就被切断了。古代社会中那种“嵌入”宇宙、安身立命的整体感消失了，人们失去了默认的信仰和终极价值的依托，精神上陷入无家可归的状态。
-   **思辨结论**：**“清澈”之后是“荒凉”。** 我们无法退回蒙昧，但也必须直面意义缺失的精神危机。韦伯不带价值评判地揭示了这一现代性的根本境况。
- **金句**：科学永远无法回答：我们做出什么样的选择才是“值得”的，我们过什么样的生活才是“有意义”的，我们生命的“目的”究竟是什么。科学也许可以给出最优的“方案”，但永远无法教给我们一个最优的“选择”。
```
"""

    response = client.chat.completions.create(
        model="deepseek-reasoner",
        messages=[
            {
                "role": "system",
                "content": prompt,
            },
            {"role": "user", "content": content},
        ],
        stream=False,
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    base_dir = "dataset/philosophical_proposition/素材"
    article_dir = "dataset/articals"
    save_dir = "dataset/philosophical_proposition/核心思想卡"
    file_path_dict = {}
    for idx in os.listdir(base_dir):
        for file in os.listdir(os.path.join(base_dir, idx)):
            file_path_dict.setdefault(file, []).append(
                os.path.join(base_dir, idx, file)
            )
    for file_name, file_path_list in file_path_dict.items():
        with open(os.path.join(article_dir, file_name)) as f:
            content = f.read()
        file_path_list.sort()
        proposose_list = []
        for file_path in file_path_list:
            with open(file_path) as f:
                proposose_list.append(f.read())
        prompt = f"""
## 原文：
```
{content}
```

### 提炼的哲学命题：
```哲学命题1
{proposose_list[0]}
```
---
```哲学命题2
{proposose_list[1]}
```
---
```哲学命题3    
{proposose_list[2]}
```
---
```哲学命题4
{proposose_list[3]}
```
---
```哲学命题5
{proposose_list[4]}
```
"""
        response = get_core_idea_card(prompt)
        with open(os.path.join(save_dir, file_name), "w") as f:
            f.write(response)
