from typing import Optional, TypedDict, Union

from agents.models import LLMInterface


class ArticleInputs(TypedDict):
    """
    A dictionary type definition for storing input data related to articles.

    Attributes:
        article_id (Union[int, Optional[list[int]]]): The unique identifier for the article. Can be a single integer or a list of integers.
        article_content (Union[str, Optional[list[str]]]): The content of the article. Can be a single string or a list of strings.
        article_title (Union[str, Optional[list[str]]]): The title of the article. Can be a single string or a list of strings.
        meta_desc (Union[str, Optional[list[str]]]): The meta description of the article. Can be a single string or a list of strings.
        article_url (Union[str, Optional[list[str]]]): The URL of the article. Can be a single string or a list of strings.
        content_category (Union[str, Optional[list[str]]]): The category of the content. Can be a single string or a list of strings.
        article_category_names (Union[str, Optional[list[str]]]): The category names for the article. Can be a single string or a list of strings.
        page_views (Union[int, Optional[list[int]]]): The number of page views the article has received. Can be a single integer or a list of integers.
        additional_input (Optional[str]): The additional input added by the user in the User Annotation Excel file
        main_article_content (Optional[str]): Stores the original article content of the "main article", only applicable for live-healthy article harmonisation.
    """

    article_id: Union[int, Optional[list[int]]]
    article_content: Union[str, Optional[list[str]]]
    article_title: Union[str, Optional[list[str]]]
    meta_desc: Union[str, Optional[list[str]]]
    article_url: Union[str, Optional[list[str]]]
    content_category: Union[str, Optional[list[str]]]
    article_category_names: Union[str, Optional[list[str]]]
    page_views: Union[int, Optional[list[int]]]
    additional_input: Optional[str]
    main_article_content: Optional[str]


class SkipLLMEvals(TypedDict):
    """
    A dictionary type definition for storing input data related to skipping LLM evaluations. This is typically used when
    running into errors raised from the Azure Content FFilter

    Attributes:
        decision (bool): Flag indicating if the LLM evaluations should be skipped.
        explanation (str): A string indicating why the LLM evaluations should be skipped. Typically derived from the error
            message
    """

    decision: bool
    explanation: Optional[str]


class ContentFlags(TypedDict):
    """
    A dictionary type definition for storing flags related to content evaluation.

    Attributes:
        is_unreadable (bool): Flag indicating if the content is unreadable.
        low_word_count (bool): Flag indicating if the content has a low word count.
    """

    is_unreadable: bool
    low_word_count: bool


class ContentJudge(TypedDict):
    """
    A dictionary type definition for storing judgments related to content evaluation.

    Attributes:
        readability (dict[str, str]): A dictionary containing readability evaluations (explanation), where keys are criteria
            and values are corresponding judgments.
        structure (dict[str, str]): A dictionary containing structure evaluations (decision and explanation), where keys
            are criteria and values are corresponding judgments.
    """

    readability: dict[str, str]
    structure: dict[str, str]


class TitleFlags(TypedDict):
    """
    A dictionary type definition for storing flags related to title evaluation.

    Attributes:
        long_title (bool): Flag indicating if the title is considered too long.
    """

    long_title: bool


class TitleJudge(TypedDict):
    """
    A dictionary type definition for storing judgments related to title evaluation.

    Attributes:
        title (dict[str, str]): A dictionary containing title evaluations, where keys are criteria and values are corresponding judgments.
    """

    title: dict[str, str]


class MetaFlags(TypedDict):
    """
    A dictionary type definition for storing flags related to meta description evaluation.

    Attributes:
        not_within_char_count (bool): Flag indicating if the meta description does not meet the required character count.
    """

    not_within_char_count: bool


class MetaJudge(TypedDict):
    """
    A dictionary type definition for storing judgments related to meta description evaluation.

    Attributes:
        meta_desc (dict[str, str]): A dictionary containing meta description evaluations, where keys are criteria and values
            are corresponding judgments.
    """

    meta_desc: dict[str, str]


class ChecksAgents(TypedDict):
    """
    A dictionary type definition for agents used in content evaluation checks.

    Attributes:
        evaluation_agent (LLMInterface): The agent responsible for performing content evaluations.
        explanation_agent (LLMInterface): The agent responsible for providing explanations for the evaluations.
    """

    evaluation_agent: LLMInterface
    explanation_agent: LLMInterface


class ArticleEvaluation(TypedDict):
    """
    A dictionary type definition for article evaluation extracted from the Excel sheet, as well as personality evaluation of the article.

    Attributes:
        reasons_for_irrelevant_title (Optional[str]): A String storing the reasons for irrelevant title from article evaluation process and extracted from the User Annotation Excel File
            Can be `None` if no evaluation are availble.
        reasons_for_irrelevant_meta_desc (Optional[str]): A String storing the reasons for irrelevant meta desc from article evaluation process and extracted from the User Annotation Excel File
            Can be `None` if no evaluation are availble.
        reasons_for_poor_readability (Optional[str]): A String storing the reasons for poor readability from article evaluation process and extracted from the User Annotation Excel File
            Can be `None` if no evaluation are availble.
        writing_has_personality (Optional[str]): The optimised title of the article.
            Can be `None` if no personality evaluation is required.
        change_summary (Optional[str]): The summary of the changes that happened from the original article to the optimised article.
            Can be `None` if the article has not undergone rewriting.
    """

    reasons_for_irrelevant_title: Optional[str]
    reasons_for_irrelevant_meta_desc: Optional[str]
    reasons_for_poor_readability: Optional[str]
    writing_has_personality: Optional[bool]
    change_summary: Optional[str]


class OptimisedArticle(TypedDict):
    """
    A dictionary type definition for storing data related to an optimised article.

    Attributes:
        researcher_keypoints (Optional[list[str]]): A list of key points identified by the researcher.
            Can be `None` if no key points are available.
        compiled_keypoints (Optional[str]): A compiled summary of key points.
            Can be `None` if no compiled summary is available.
        optimised_content (Optional[str]): The optimised content of the article.
            Can be `None` if the content has not been optimised.
        optimised_writing (Optional[str]): The optimised version of the article's writing.
            Can be `None` if the writing has not been optimised.
        optimised_writing_XML (Optional[str]): The optimised XML version of the article's writing.
            Can be `None` if the writing has not been optimised.
        optimised_article_title (Optional[str]): The optimised title of the article.
            Can be `None` if the title has not been optimised.
        optimised_meta_desc (Optional[str]): The optimised meta description of the article.
            Can be `None` if the meta description has not been optimised.
    """

    researcher_keypoints: Optional[list[str]]
    compiled_keypoints: Optional[str]
    sorted_content: Optional[str]
    optimised_content: Optional[str]
    optimised_writing: Optional[str]
    optimised_writing_XML: Optional[str]
    optimised_article_title: Optional[list]
    optimised_meta_desc: Optional[list]


class OptimisationFlags(TypedDict):
    """
    A dictionary type definition for storing flags related to article optimisation.

    Attributes:
        flag_for_content_optimisation (bool): Flag indicating if the content needs to be optimised.
        flag_for_title_optimisation (bool): Flag indicating if the title needs to be optimised.
        flag_for_meta_desc_optimisation (bool): Flag indicating if the meta description needs to be optimised.
        flag_for_writing_optimisation (bool): Flag indicating if the writing needs to be optimised.
    """

    flag_for_content_optimisation: bool
    flag_for_title_optimisation: bool
    flag_for_meta_desc_optimisation: bool
    flag_for_writing_optimisation: bool


class OptimisationAgents(TypedDict):
    """
    A dictionary type definition for agents involved in the article optimisation process.

    Attributes:
        researcher_agent (LLMInterface): The agent responsible for researching and identifying key points in the article.
        compiler_agent (LLMInterface): The agent responsible for compiling key points into a summary.
        content_optimisation_agent (LLMInterface): The agent responsible for optimising the content of the article.
        writing_optimisation_agent (LLMInterface): The agent responsible for optimising the writing of the article.
        title_optimisation_agent (LLMInterface): The agent responsible for optimising the article title.
        meta_desc_optimisation_agent (LLMInterface): The agent responsible for optimising the meta description of the article.
        readability_optimisation_agent (LLMInterface): The agent responsible for optimising the readability of the article.
        personality_evaluation_agent (LLMInterface): The agent responsible for evaluating the article's adherence to the required personality and voice.
        writing_evaluation_agent (LLMInterface): The agent responsible for evaluating the quality and effectiveness of the writing.
        writing_postprocessor_agent (LLMInterface): The agent responsible for producing a summary of the changes between the original and optimised article and output the optimised article in XML format.
    """

    researcher_agent: LLMInterface
    compiler_agent: LLMInterface
    content_optimisation_agent: LLMInterface
    writing_optimisation_agent: LLMInterface
    title_optimisation_agent: LLMInterface
    meta_desc_optimisation_agent: LLMInterface
    readability_optimisation_agent: LLMInterface
    personality_evaluation_agent: LLMInterface
    writing_postprocessor_agent: LLMInterface
