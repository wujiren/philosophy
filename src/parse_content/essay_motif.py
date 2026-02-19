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
你的任务是根据用户输入的哲学命题，分析这个核心命题适用的高考议论文母题有哪些

## 母题分析
母题的形式如下：
```
### 母题一：[母题标题]
-   **适用题目举例：** “信息茧房”、“算法推荐”、“大数据时代我们是否更自由”、“真相与后真相”
-   **破题角度：**
    [破题角度分析]

-   **立意进阶：**
    [立意进阶分析]

## 母题二：
...
```

## 其他说明
- 母题标题需准确概括命题与高考常见话题的结合点。
- 适用题目举例应列举典型的高考作文题或相关话题。
- 破题角度需紧扣命题核心，从1-2个具体层面展开分析。
- 立意进阶应引导思考如何从个人体验上升到时代反思。

## 示例
```
### 母题一：信息时代与认知局限
-   **适用题目举例：** “信息茧房”、“算法推荐”、“大数据时代我们是否更自由”、“真相与后真相”

-   **破题角度：**
    1.  **虚假需求与思维萎缩：** 在信息环境中，个体往往只接触让自己感到舒适的内容，这相当于命题所说的“虚假需求”——人们以为自己在自由选择信息，实则被这种“舒适的不自由”所塑造。久而久之，批判性、否定性和超越性的思考维度（如质疑信息来源的全面性、反思信息环境的合理性）日益萎缩，人们只关心如何在现有信息流内“过得更好”，而不再质疑这个信息框架本身是否合理。
    2.  **社会一体化与反对的同化：** 社会系统（如主流媒体、社交平台）展现出强大的“一体化”能力，能够排斥、化解甚至“招安”一切反叛力量。任何对信息垄断的批判，可能被收编为一种“另类声音”或“争议话题”而纳入商业逻辑，从而消解其否定性。最终，所有对立面都被消解，社会在信息层面成为一个高度稳定、封闭的循环。

-   **立意进阶：**
    -   **问自己：** 我每天所接触的信息，有多少是主动探寻未知，又有多少只是被动接受那些让我感到舒适的内容？当我在这个信息框架内“过得舒适”时，是否已经放弃了跳出框架去想象一种全然不同的信息生态的可能？
    -   **问时代：** 在一个信息极大丰富的时代，真正的自由是否仅仅意味着拥有更多选择，还是更在于保持那份对信息环境本身的批判性思考？当批判的声音被系统化解或边缘化，时代如何避免陷入“只有肯定、没有否定”的信息封闭？
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
    base_dir = "dataset/philosophical_proposition/核心思想卡2"
    save_dir = "dataset/philosophical_proposition/母题"
    os.makedirs(save_dir,exist_ok=True)
    for file_name in os.listdir(base_dir):

        with open(os.path.join(base_dir, file_name)) as f:
            content = f.read()
        
        response = get_core_idea_card(content)
        with open(os.path.join(save_dir, file_name), "w") as f:
            f.write(response)
