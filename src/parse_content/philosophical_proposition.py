import os
from openai import OpenAI


def get_philosophical_proposition(content):

    client = OpenAI(
        api_key=os.environ.get("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com"
    )
    prompt = "阅读用户输入的哲学文章，分析文章中哲学命题是什么？"
    response = client.chat.completions.create(
        model="deepseek-chat",
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
