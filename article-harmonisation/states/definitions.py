from typing import Optional, TypedDict

from agents.models import LLMInterface


class ArticleInputs(TypedDict):
    article_id: int
    article_content: str
    article_title: str
    meta_desc: str
    article_url: str
    content_category: str
    article_category_names: str
    page_views: int


class ContentFlags(TypedDict):
    is_unreadable: bool
    low_word_count: bool


class ContentJudge(TypedDict):
    readability: str
    structure: str


class TitleFlags(TypedDict):
    long_title: bool


class TitleJudge(TypedDict):
    title: str


class MetaFlags(TypedDict):
    not_within_char_count: bool


class MetaJudge(TypedDict):
    meta_desc: str


class ChecksAgents(TypedDict):
    evaluation_agent: LLMInterface
    explanation_agent: LLMInterface


# TODO: Explore combining ArticleInputs and OriginalArticles class
class OriginalArticles(TypedDict):
    article_content: list[str]
    article_title: Optional[list[str]]
    content_category: Optional[list[str]]
    meta_desc: Optional[list[str]]


class OptimisedArticle(TypedDict):
    researcher_keypoints: Optional[list[str]]
    compiled_keypoints: Optional[str]
    optimised_content: Optional[str]
    optimised_writing: Optional[str]
    optimised_article_title: Optional[str]
    optimised_meta_desc: Optional[str]


class OptimisationFlags(TypedDict):
    flag_for_content_optimisation: bool
    flag_for_title_optimisation: bool
    flag_for_meta_desc_optimisation: bool


class OptimisationAgents(TypedDict):
    researcher_agent: LLMInterface
    compiler_agent: LLMInterface
    content_optimisation_agent: LLMInterface
    writing_optimisation_agent: LLMInterface
    title_optimisation_agent: LLMInterface
    meta_desc_optimisation_agent: LLMInterface
