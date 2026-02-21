import json
import os
from src.run_pipeline import run_pipeline
from src.parse_content.summary import save_as_docx


if __name__ == "__main__":

    with open("dataset/道德经.md") as file:
        content_lines = [f for f in file.readlines() if f.strip()]
    content_list = []
    for l in content_lines:
        content_list.append(
            {
                "book": "道德经",
                "author": "老子",
                "chapter": l.strip(),
                "article_text": l.strip().split(".")[-1],
            }
        )
    data_save_dir = "dataset/道德经思辨/data"
    article_save_dir = "dataset/道德经思辨/article"
    for content in content_list:
        save_name = content["chapter"].strip().split(".")[0]
        if os.path.exists(f"{data_save_dir}/{save_name}.json"):
            continue
        data = run_pipeline(
            **content,
        )

        for i, idea in enumerate(data["core_ideas"]):
            title = f"{article_save_dir}/{save_name}_{idea['summary']['title']}"
            with open(f"{title}.md", "w") as f:
                f.write(idea["summary"]["summary"])
            save_as_docx(
                idea["summary"]["summary"],
                f"{title}.docx",
            )
        with open(f"{data_save_dir}/{save_name}.json", "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
