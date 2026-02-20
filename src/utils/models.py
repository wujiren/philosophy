from typing import List, TypedDict, Optional


class Metadata(TypedDict):
    book: str
    author: str
    chapter: str


class Motif(TypedDict):
    id: str  # 例如: "母题一"
    title: str  # 母题的标题内容
    motif: str  # 包含破题角度、思辨性提问、立意进阶的完整规范文本


class Summary(TypedDict):
    title: str  # 摘要的标题内容
    summary: str  # 包含核心观点、关键词、分析、结论的完整规范文本


class CoreIdea(TypedDict):
    id: str  # 例如: "核心思想卡1"
    title: str  # 核心思想标题
    core_idea: str  # 包含思辨点、内容分析、结论、金句的完整规范文本
    motifs: List[Motif]
    summary: Summary


class PhilosophyStudyUnit(TypedDict):
    metadata: Metadata
    original_article: str
    core_ideas: List[CoreIdea]
