import re
from abc import ABC, abstractmethod

import tiktoken


def prompt_tool(model: str):
    """
    Returns a LLMPrompt object based on the string input

    Args:
        model (str): a String input stating the model used

    Returns:
        LLMPrompt: a LLMPrompt object for the respective model type

    Raises:
        ValueError: if the input model is not supported
    """
    match model.lower():
        case "mistral":
            return MistralPrompts()

        case "llama3":
            return LlamaPrompts()

        case "azure":
            return AzurePrompts()

        case _:
            raise ValueError(f"Prompts for model ({model}) have not been created.")


class LLMPrompt(ABC):
    """
    Abstract class for all LLM prompt classes.
    All models will have a prompt class, which must inherit from this class, hence they must all include the following methods.

    This class inherits from ABC class.
    """

    @staticmethod
    @abstractmethod
    def return_readability_evaluation_prompt():
        """
        Abstract method for returning a readability evaluation prompt.
        """
        pass

    @staticmethod
    @abstractmethod
    def return_structure_evaluation_prompt():
        """
        Abstract method for returning a content structure evaluation prompt.
        """
        pass

    @staticmethod
    @abstractmethod
    def return_title_evaluation_prompt():
        """
        Abstract method for returning a title evaluation prompt.
        """
        pass

    @staticmethod
    @abstractmethod
    def return_meta_desc_evaluation_prompt():
        """
        Abstract method for returning a meta description evaluation prompt.
        """
        pass

    @staticmethod
    @abstractmethod
    def return_researcher_prompt():
        """
        Abstract method for returning a researcher prompt
        """
        pass

    @staticmethod
    @abstractmethod
    def return_compiler_prompt():
        """
        Abstract method for returning a compiler prompt
        """
        pass

    @staticmethod
    @abstractmethod
    def return_content_prompt():
        """
        Abstract method for returning a content optimisation prompt
        """
        pass

    @staticmethod
    @abstractmethod
    def return_writing_prompt():
        """
        Abstract method for returning a writing optimisation prompt
        """
        pass

    @staticmethod
    @abstractmethod
    def return_title_prompt():
        """
        Abstract method for returning a title optimisation prompt
        """
        pass

    @staticmethod
    @abstractmethod
    def return_meta_desc_prompt():
        """
        Abstract method for returning a meta description optimisation prompt
        """
        pass


class AzurePrompts(LLMPrompt):
    """
    This class contains methods that stores and returns the prompts for ChatGPT models.

    This class inherits from the LLMPrompt class

    Refer to https://platform.openai.com/docs/guides/prompt-engineering/strategy-write-clear-instructions for more information.
    """

    @staticmethod
    def return_decision_prompt() -> list[tuple[str, str]]:
        """
        Returns the decision prompt where the chain output will be a boolean (True/False)

        Returns:
            list[tuple[str, str]]: a list containing the decision prompt. {text} is the only input required to invoke the prompt.
        """

        decision_prompt = [
            (
                "system",
                """
                You are to evaluate whether an article should be optimised given the critique provided.
                Return a boolean (True/False) indicating whether the article should be optimised given the critique provided.
                """,
            ),
            ("human", "Evaluate the following text:\n{text}"),
        ]

        return decision_prompt

    @staticmethod
    def return_summarization_prompt() -> list[tuple[str, str]]:
        """
        Returns the summarization prompt where the chain output will be a string

        Returns:
            list[tuple[str, str]]: a list containing the summarization prompt. {text} is the only input required to invoke the prompt.
        """

        evaluation_summary_prompt = [
            (
                "system",
                """
                Summarize the following text into 3 to 5 sentences. Ensure the summary is concise, succinct, and direct, focusing only on the most essential points.
                You must maintain the goal and context of providing the critique and recommendation to the individual. There should be greater focus on the areas of improvement.
                """,
            ),
            ("human", "Evaluate the following text:\n{text}"),
        ]

        return evaluation_summary_prompt

    @staticmethod
    def return_readability_evaluation_prompt() -> list[tuple[str, str]]:
        """
        Returns the readability evaluation prompt where the chain output will be a string

        Returns:
            list[tuple[str, str]]: a list containing the readability evaluation prompt. {article} is the only input required to invoke the prompt.
        """

        readability_evaluation_prompt = [
            (
                "system",
                """
                I want you to act as an expert in readability analysis.
                Your task is to evaluate and critique the readability of the provided article. Your analysis should cover the following aspects:

                Let's think step by step.

                1. You are to conduct a detailed analysis and critique following the criteria below:
                    - **Sentence Structure**: Assess the complexity of sentences. Identify  and list out ALL long, convoluted sentences and suggest ways to simplify them.
                    - **Vocabulary**: Evaluate the complexity of the vocabulary used. Highlight and list out ALL overly complex words. Suggest simpler words or phrases as an alternative.
                    - **Coherence and Flow**: Analyze the coherence and logical flow of the text. Point out any abrupt transitions or lack of clarity and provide suggestions for improvement.
                2. You are to explain why the article has poor readability by performing the following instructions below:
                    - **Overall Assessment**: Summarize the overall readability of the article,
                    - **Explanation**: Explain why the article suffers from poor readability.
                    - **Recommendation**: Provide specific examples and actionable recommendations for improvement.
                """,
            ),
            ("human", "Evaluate the following article:\n{article}"),
        ]
        return readability_evaluation_prompt

    @staticmethod
    def return_structure_evaluation_prompt() -> list[tuple[str, str]]:
        """
        Returns the structure evaluation prompt where the chain output will be a string

        Returns:
            list[tuple[str, str]]: a list containing the structure evaluation prompt. {article} is the only input required to invoke the prompt.
        """

        structure_evaluation_prompt = [
            (
                "system",
                """
                Objective: Critique the content structure of the article, evaluating its effectiveness and coherence based on the following criteria -

                1. Opening
                Introduction
                -   Does the introduction grab the attention of readers quickly and effectively?
                -   Does the introduction outline the content of the article clearly?

                2. Content Structure
                Main Body
                -   Are subheadings used effectively to organize content?
                -   Are paragraphs short, focused, and easy to read?
                -   Does the article incorporate lists where appropriate?

                3. Writing Style
                Tone and Language
                -   Is the tone conversational?
                -   Does the article avoid unexplained jargon or overly technical language?
                -   Is the language appropriate for the audience's level of knowledge?
                -   Does the article make the content more relatable and personal by writing from a second-person point of view, e.g. using pronouns such as "you" or "your"?

                4. Closing
                Conclusion
                -   Are clear next steps and call-to-action for the reader provided?
                -   Does the conclusion reinforce the main message?

                5. Overall Effectiveness
                Value
                -   Does the article provide practical, actionable information?
                -   Does it fulfill the promise made by the headline and introduction?

                Length
                -   Is the length appropriate for the topic and audience (generally 300-1500 words)?
                -   Is the content thorough without unnecessary padding?

                Instructions:
                1.  Carefully read through the article.
                2.  Use the criteria above to evaluate each section.
                3.  Provide detailed feedback, noting strengths and areas for improvement.
                4.  Suggest specific changes or enhancements where applicable.
                """,
            ),
            ("human", "Evaluate the following article:\n{article}"),
        ]

        return structure_evaluation_prompt

    @staticmethod
    def return_title_evaluation_prompt(step: str) -> list[tuple[str, str]]:
        """
        Returns the title evaluation prompt where the chain output will be a string

        Returns:
            list[tuple[str, str]]: a list containing the title evaluation prompt. {title} and {article} are the inputs required to invoke the prompt.
        """
        match step:
            case "diseases-and-conditions":
                title_evaluation_prompt = [
                    (
                        "system",
                        """
                        Objective: Assess the relevance of the article title by qualitatively comparing it with the content of the article, ensuring a detailed and contextual analysis.

                        Steps to Follow -
                        1.  Identify the Title:
                        -   What is the title of the article?

                        2.  Analyze the Title:
                        -   Does the title only feature the name/ synonym/ abbreviation/ common name of the disease?
                        -   What main topic or benefit does the title convey?
                        -   Is the title specific and clear in its message?

                        3.  Review the Content:
                        -   Read the entire article carefully.
                        -   Summarize the main points and key themes of the article.
                        -   Note any specific sections or statements that align with or diverge from the title's promise.

                        4.  Compare Title and Content:
                        -   Does the content directly address the main topic or benefit stated in the title?
                        -   Are the main themes and messages of the article consistent with the expectations set by the title?
                        -   Identify any significant information in the article that is not reflected in the title and vice versa.

                        5.  Evaluate Relevance:
                        -   Provide a detailed explanation of how well the title reflects the content.
                        -   Use specific examples or excerpts from the article to support your evaluation.
                        -   Highlight any discrepancies or misalignment between the title and the content.

                        Your assessment should emphasize the relevance of the article and explain why the title is irrelevant as and when needed.
                        """,
                    ),
                    ("human", """ Title: "10 Tips for Effective Time Management" """),
                    (
                        "assistant",
                        """
                        Content Summary:
                        -   The article introduces the importance of time management, discusses ten detailed tips, provides examples for each tip, and concludes with the benefits of good time management.

                        Comparison and Evaluation:
                        -   The title promises "10 Tips for Effective Time Management," and the article delivers on this promise by providing ten actionable tips.
                        -   Each section of the article corresponds to a tip mentioned in the title, ensuring coherence and relevance.
                        -   Specific excerpts: "Tip 1: Prioritize Your Tasks" aligns with the title's promise of effective time management strategies.
                        -   The relevance score is high due to the direct alignment of content with the title.""",
                    ),
                    (
                        "system",
                        """
                        Instructions:
                        1.  Use the steps provided to qualitatively evaluate the relevance of the article title.
                        2.  Write a brief report based on your findings, including specific examples.
                        3.  Do NOT make any title suggestions or recommendations. Focus solely on the critique instead.
                        4.  Casual tone or style in the title is acceptable and should not be a point of critique. Focus on the title relevance to the content.
                        5.  The title MUST NOT only feature the name/ synonym/ abbreviation/ common name of the disease.
                            -   "Avian Influenza H5N1 (Bird Flu)" should be considered as only featuring the disease name.
                        """,
                    ),
                    (
                        "human",
                        "Evaluate the following title:\n{title}\n\nUsing the following article:\n{article}",
                    ),
                ]
                return title_evaluation_prompt
            case _:
                title_evaluation_prompt = [
                    (
                        "system",
                        """
                        Objective: Assess the relevance of the article title by qualitatively comparing it with the content of the article, ensuring a detailed and contextual analysis.

                        Steps to Follow -
                        1.  Identify the Title:
                        -   What is the title of the article?

                        2.  Analyze the Title:
                        -   What main topic or benefit does the title convey?
                        -   Is the title specific and clear in its message?

                        3.  Review the Content:
                        -   Read the entire article carefully.
                        -   Summarize the main points and key themes of the article.
                        -   Note any specific sections or statements that align with or diverge from the title's promise.

                        4.  Compare Title and Content:
                        -   Does the content directly address the main topic or benefit stated in the title?
                        -   Are the main themes and messages of the article consistent with the expectations set by the title?
                        -   Identify any significant information in the article that is not reflected in the title and vice versa.

                        5.  Evaluate Relevance:
                        -   Provide a detailed explanation of how well the title reflects the content.
                        -   Use specific examples or excerpts from the article to support your evaluation.
                        -   Highlight any discrepancies or misalignment between the title and the content.

                        Your assessment should emphasize the relevance of the article and explain why the title is irrelevant as and when needed.
                        """,
                    ),
                    ("human", """ Title: "10 Tips for Effective Time Management" """),
                    (
                        "assistant",
                        """
                        Content Summary:
                        -   The article introduces the importance of time management, discusses ten detailed tips, provides examples for each tip, and concludes with the benefits of good time management.

                        Comparison and Evaluation:
                        -   The title promises "10 Tips for Effective Time Management," and the article delivers on this promise by providing ten actionable tips.
                        -   Each section of the article corresponds to a tip mentioned in the title, ensuring coherence and relevance.
                        -   Specific excerpts: "Tip 1: Prioritize Your Tasks" aligns with the title's promise of effective time management strategies.
                        -   The relevance score is high due to the direct alignment of content with the title.""",
                    ),
                    (
                        "system",
                        """
                        Instructions:
                        1.  Use the steps provided to qualitatively evaluate the relevance of the article title.
                        2.  Write a brief report based on your findings, including specific examples.
                        3.  Do NOT make any title suggestions or recommendations. Focus solely on the critique instead.
                        4.  Casual tone or style in the title is acceptable and should not be a point of critique. Focus on the title relevance to the content.
                        """,
                    ),
                    (
                        "human",
                        "Evaluate the following title:\n{title}\n\nUsing the following article:\n{article}",
                    ),
                ]
                return title_evaluation_prompt

    @staticmethod
    def return_meta_desc_evaluation_prompt() -> list[tuple[str, str]]:
        """
        Returns the meta description evaluation prompt where the chain output will be a string

        Returns:
            list[tuple[str, str]]: a list containing the meta description evaluation prompt. {meta} and {article} are the inputs required to invoke the prompt.
        """

        meta_desc_evaluation_prompt = [
            (
                "system",
                """
                Objective: Assess the relevance of the article's meta description by comparing it with the content of the article.

                Steps to Follow:
                1.  Identify the Meta Description:
                -   What is the meta description of the article?

                2.  Analyze the Meta Description:
                -   What main topic or benefit does the meta description convey?
                -   Is the meta description clear, concise, and engaging?

                3.  Review the Content:
                -   Read the entire article carefully.
                -   Summarize the main points and key themes of the article.
                -   Note any specific sections or statements that align with or diverge from the meta description.

                4.  Compare Meta Description and Content:
                -   Does the content directly address the main topic or benefit stated in the meta description?
                -   Are the main themes and messages of the article consistent with the expectations set by the meta description?
                -   Identify any significant information in the article that is not reflected in the meta description and vice versa.

                5.  Evaluate Relevance:
                -   Provide a detailed explanation of how well the meta description reflects the content.
                -   Use specific examples or excerpts from the article to support your evaluation.
                -   Highlight any discrepancies or misalignment between the meta description and the content.

                Your assessment should emphasize the relevance of the article and explain why the meta description is irrelevant as and when needed.
                """,
            ),
            (
                "human",
                """ Meta Description: "Learn 10 effective time management tips to boost your productivity and achieve your goals." """,
            ),
            (
                "assistant",
                """
                Content Summary:
                -   The article introduces the importance of time management, discusses ten detailed tips, provides examples for each tip, and concludes with the benefits of good time management.

                Comparison and Evaluation:
                -   The meta description promises "10 effective time management tips to boost your productivity and achieve your goals," and the article delivers on this promise by providing ten actionable tips.
                -   Each section of the article corresponds to a tip mentioned in the meta description, ensuring coherence and relevance.
                -   Specific excerpts: "Tip 1: Prioritize Your Tasks" aligns with the meta description's promise of effective time management strategies.
                -   The relevance score is high due to the direct alignment of content with the meta description.
                """,
            ),
            (
                "system",
                """
                Instructions:
                1.  Use the steps provided to evaluate the relevance of the article's meta description.
                2.  Write a brief report based on your findings, including specific examples.
                3.  Do NOT make any meta description suggestions or recommendations. Focus solely on the critique instead.
                """,
            ),
            (
                "human",
                """
                Evaluate the following Meta Description:
                {meta}

                Use the following article:
                {article}
                """,
            ),
        ]

        return meta_desc_evaluation_prompt

    @staticmethod
    def return_researcher_prompt(step: str) -> list[tuple[str, str]]:
        """
        Returns the specified researcher prompt. There are two possible research prompts, namely:

        1. "generate keypoints": This prompt is used to process the content for a given article and section out irrelevant sentences under an "omitted sentences" section below.
        2. "add additional input": This prompt is used to add any additional input from the User Annotation Excel sheet to the processed keypoints.

        Args:
            step(str): a String indicating the step in which the researcher node is at. It can either be "generate keypoints" or "add additional input"

        Returns:
            list[tuple[str, str]]: a list containing the researcher prompt. {Article} is the only input required to invoke the prompt.
        """

        match step:
            case "generate keypoints":
                generate_keypoints_prompt = [
                    (
                        "system",
                        """You are part of a article combination process. Your main task is to analyze the headers in the article to identify and omit any unnecessary sentences under the header.
                        You will be given a context guideline as well as a set of instructions.
                        You MUST use the Context guidelines given.
                        You MUST strictly follow the instructions given.

                        ### Start of Context guidelines
                            You will be given an article with labelled headers.
                            Each header will have their header type specified at the front of the header title as html tags.
                            If a header is a sub header or sub section to another header, it will be specified in the following sentence along with the header title that it is a sub section to.
                            If a header is a sub header or sub section to another header, you MUST use the title of the parent header along with the title of the sub header to determine if the sentences under the sub section is relevant.
                            Sentences leading to an external link or article SHOULD be omitted.

                            Refer to this example and its explanation:
                                ### Start of header example
                                    h2 Sub Header: Exercises you can do at home  // This is a h2 Sub Header

                                    h3 Sub Section: Wall planks // This is a h3 sub section
                                    Sub section to h2 Sub Header: Exercises you can do at home // This h3 subection is under the h2 sub header "Exercises you can do at home"
                                    # Rest of content
                                ### End of header example

                            Check through each headline with this context step by step.
                        ### End of Context guidelines

                        ### Start of Instructions
                        Do NOT paraphrase sentences from the given article when assigning the sentence, you must use each sentence directly from the given content.
                        Each sentence must appear only ONCE under the header.

                        Do not rename "Article Header" label.
                        Rename all other article header labels to either "Main keypoint" or "Sub keypoint".
                        If a header has no child headers, the header will be labelled as "Main keypoint".
                        If a header has a parent header, the header will be labelled as "Sub keypoint".
                        You may come up with a relevant header for additional content and label it as a "Main keypoint".
                        Not all sentences are relevant to its header. If a sentence is irrelevant to all headers, you can place it under the last header "Omitted sentences" at the end of the article.
                        You should include citations or references under "Omitted sentences".
                        Check through each instruction step by step.
                        ### End of Instructions

                        Refer to the example below to format your answer accordingly:
                        """,
                    ),
                    (
                        "human",
                        """
                        Article Header: Introduction to Parkinson's disease
                        Content: Parkinson's is a neurodegenerative disease. It is a progressive disorder that affects the nervous system and other parts of the body. There are approximately 90,000 new patients diagnosed with PD annually in the US.

                        Buy these essential oils to recover from Parkinson's Disease!

                        h2 Sub Header: Symptoms of Parkinson's disease

                        h3 Sub Header: Tremor in hands, arms, legs, jaw, or head
                        Sub Section to h2 Sub Header: Symptoms of Parkinson's disease
                        Content: Patient's of PD may suffer from tremors in their limbs that may worsen over time. For example, people may feel mild tremors or have difficulty getting out of a chair. They may also notice that they speak too softly, or that their handwriting is slow and looks cramped or small.

                        h3 Sub Header: Muscle stiffness
                        Sub Section to h2 Sub Header: Symptoms of Parkinson's disease
                        Content: Patient's of PD may also suffer from muscle stiffness and lose their mobility as their conditions worsen over time. During early stages of Parkinson's, family members and close friends will begin to notice that the person may lack facial expression and animation as well.

                        h3 Sub Header: Impaired balance and coordination
                        Sub Section to h2 Sub Header: Symptoms of Parkinson's disease
                        Content: Individuals with Parkinson's disease often experience significant challenges with balance and coordination. These impairments can lead to an increased risk of falls and a decreased ability to perform everyday activities.

                        Read more: Western medicine vs Alternative healing

                        Related: Newest breakthroughs in the field of neuroscience

                        h2 Sub Header: Additional content to add
                        Content: Joining a Parkinson's support group can provide emotional support and valuable insights from others who are experiencing similar challenges. These groups offer a sense of community and shared understanding.

                        """,
                    ),
                    (
                        "assistant",
                        """
                        Main keypoint: Introduction to Parkinson's disease
                        Content: Parkinson's is a neurodegenerative disease. It is a progressive disorder that affects the nervous system and other parts of the body. There are approximately 90,000 new patients diagnosed with PD annually in the US.

                        Main keypoint: Symptoms of Parkinson's disease

                        Sub keypoint: Tremor in hands, arms, legs, jaw, or head
                        Content: Patient's of PD may suffer from tremors in their limbs that may worsen over time. For example, people may feel mild tremors or have difficulty getting out of a chair. They may also notice that they speak too softly, or that their handwriting is slow and looks cramped or small.

                        Sub keypoint: Muscle stiffness
                        Content: Patient's of PD may also suffer from muscle stiffness and lose their mobility as their conditions worsen over time. During early stages of Parkinson's, family members and close friends will begin to notice that the person may lack facial expression and animation as well.

                        Sub keypoint: Impaired balance and coordination
                        Content: Individuals with Parkinson's disease often experience significant challenges with balance and coordination. These impairments can lead to an increased risk of falls and a decreased ability to perform everyday activities.

                        Main keypoint: Joining a support group
                        Content: Joining a Parkinson's support group can provide emotional support and valuable insights from others who are experiencing similar challenges. These groups offer a sense of community and shared understanding.

                        Omitted Sentences:
                        Buy these essential oils to recover from Parkinson's Disease!
                        Read more: Western medicine vs Alternative healing
                        Related: Newest breakthroughs in the field of neuroscience

                        """,
                    ),
                    (
                        "human",
                        "Sort the key points below based on the instructions and examples you have received:\n{Article}",
                    ),
                ]
                return generate_keypoints_prompt

            case "add additional input":
                additional_content_prompt = [
                    (
                        "system",
                        """ Your task is to seamlessly add in additional keypoints into content given to you.

                You will be given a series of processed keypoints and additional content to add in. You are to add in the additional content as a new keypoint.

                You can write a relevant header for the additional content if no header is given.
                Add a "Main keypoint" in front of the header for additional content.
                """,
                    ),
                    (
                        "human",
                        """
                Add this additional content to the given keypoints:
                Additional content to add
                Content: Joining a Parkinson's support group can provide emotional support and valuable insights from others who are experiencing similar challenges. These groups offer a sense of community and shared understanding.

                Keypoints:
                Main keypoint: Introduction to Parkinson's disease
                Content: Parkinson's is a neurodegenerative disease. It is a progressive disorder that affects the nervous system and other parts of the body. There are approximately 90,000 new patients diagnosed with PD annually in the US.

                Main keypoint: Symptoms of Parkinson's disease

                Sub keypoint: Tremor in hands, arms, legs, jaw, or head
                Content: Patient's of PD may suffer from tremors in their limbs that may worsen over time. For example, people may feel mild tremors or have difficulty getting out of a chair. They may also notice that they speak too softly, or that their handwriting is slow and looks cramped or small.

                Sub keypoint: Muscle stiffness
                Content: Patient's of PD may also suffer from muscle stiffness and lose their mobility as their conditions worsen over time. During early stages of Parkinson's, family members and close friends will begin to notice that the person may lack facial expression and animation as well.

                Sub keypoint: Impaired balance and coordination
                Content: Individuals with Parkinson's disease often experience significant challenges with balance and coordination. These impairments can lead to an increased risk of falls and a decreased ability to perform everyday activities.

                Omitted Sentences:
                Buy these essential oils to recover from Parkinson's Disease!
                Read more: Western medicine vs Alternative healing
                Related: Newest breakthroughs in the field of neuroscience
                """,
                    ),
                    (
                        "assistant",
                        """
                Main keypoint: Introduction to Parkinson's disease
                Content: Parkinson's is a neurodegenerative disease. It is a progressive disorder that affects the nervous system and other parts of the body. There are approximately 90,000 new patients diagnosed with PD annually in the US.

                Main keypoint: Symptoms of Parkinson's disease

                Sub keypoint: Tremor in hands, arms, legs, jaw, or head
                Content: Patient's of PD may suffer from tremors in their limbs that may worsen over time. For example, people may feel mild tremors or have difficulty getting out of a chair. They may also notice that they speak too softly, or that their handwriting is slow and looks cramped or small.

                Sub keypoint: Muscle stiffness
                Content: Patient's of PD may also suffer from muscle stiffness and lose their mobility as their conditions worsen over time. During early stages of Parkinson's, family members and close friends will begin to notice that the person may lack facial expression and animation as well.

                Sub keypoint: Impaired balance and coordination
                Content: Individuals with Parkinson's disease often experience significant challenges with balance and coordination. These impairments can lead to an increased risk of falls and a decreased ability to perform everyday activities.

                Main keypoint: Joining a support group // A header was written for the additional content
                Content: Joining a Parkinson's support group can provide emotional support and valuable insights from others who are experiencing similar challenges. These groups offer a sense of community and shared understanding.

                Omitted Sentences:
                Buy these essential oils to recover from Parkinson's Disease!
                Read more: Western medicine vs Alternative healing
                Related: Newest breakthroughs in the field of neuroscience

                """,
                    ),
                    (
                        "human",
                        """Add this additional content to the given keypoints:
                {additional_content}

                Keypoints:
                {content}
                """,
                    ),
                ]
        return additional_content_prompt

    @staticmethod
    def return_compiler_prompt() -> list[tuple[str, str]]:
        """
        Returns the compiler prompt which compiles keypoints from multiple articles.

        Returns:
            list[tuple[str, str]]: a list containing the prompt for a Compiler LLM. {Keypoints} is the only input required to invoke the prompt.
        """

        compiler_prompt = [
            (
                "system",
                """
                Your task is to compare and merge the keypoints and their content given to you.
                Your final answer be a final compilation of all the keypoints from the two articles, with no loss in information and no duplicated sentences.
                You are NOT supposed to summarise the content.
                You will be given a context guideline as well as a set of instructions.
                You MUST use the Context guidelines given.
                You MUST strictly follow the instructions given.

                ### Start of Context guidelines
                    You will be given a text with keypoints for multiple articles on a particular health condition.
                    The keypoints can either be labelled as a "Main keypoint" or "Sub keypoint".
                    You may assume that a Sub keypoint is under the most recent Main keypoint.
                    The start and end of each article's keypoints will be clearly labelled.
                ### End of Context guidelines

                ### Start of Instructions
                1. Focus on the content of each keypoint, not just the headers. Similar content should be merged even if the headers are different.
                2. Analyze the content of each keypoint thoroughly, looking for thematic similarities with other keypoints.
                3. If you identify two or more keypoints with similar themes or information, regardless of their headers:
                    a. Combine their content to form a new, comprehensive keypoint.
                    b. Choose the most appropriate header for the combined content, or create a new header that accurately represents the merged information.
                    c. Remove any redundant sentences, but ensure all unique information is retained.
                4. Do NOT summarise the content. Your main task is to improve the position of the keypoints and remove duplication information, not to summarise the information.
                5. Your final answer be a compilation of all the keypoints from the two articles, with minimal to no loss in information when compared to the original keypoints individually.
                6. RETAIN ALL specific details, especially information pertaining to quantities, percentages, specific names, and technical terms.
                7. You MUST check your final answer with each keypoint in the original articles to ensure that all information has been captured in your final answer.
                8. Do NOT paraphrase and strictly only add or remove sentences.
                9. You may use bullet points, but do NOT paraphrase the sentences
                10. Remove ALL sentences under the "Omitted Sentences" section when compiling the information.
                11. You may add conjunctions and connectors between sentences if it improves the flow of the sentences.
                12. You MUST retain ALL key information, especially information pertaining to specific disease names and medications.
                13. When in doubt about whether to include a piece of information, always choose to include it in the final compilation.

                IMPORTANT: The goal is to create a comprehensive, non-redundant compilation of all information from the original keypoints. Err on the side of inclusion rather than omission when in doubt.
                ### End of Instructions

                Use the example below as an idea on how compiling the keypoints should be:
                """,
            ),
            (
                "user",
                """
                ### Start of Article 1 Keypoints ###
                Article Header: Introduction to Parkinson's disease
                Content: Parkinson's disease is a neuro-degenerative disease.

                Main keypoint: Symptoms of Parkinson's disease
                Content: Some common symptoms of PD include:
                    - Muscle rigidity, where muscle remains contracted for a long time
                    - Tremouring in hands
                    - Impaired balance and coordination, sometimes leading to falls.

                Main keypoint: Remedies to Parkinson's disease
                Content: You may take Levodopa prescribed by your doctor to alleviate the symptoms.
                ### End of Article 1 Keypoints ###

                ### Start of Article 2 Keypoints ###
                Article Header: What is Parkinson's disease? Recognise the early symptoms.

                Main keypoint: History of Parkinson's disease
                Content: Parkinson's disease was discovered by James Parkinson in 1817. It is a neurodegenerative disease.

                Main Keypoint: Recognise the symptoms of Parkinson's disease!
                Content: Symptoms of PD include: Barely noticeable tremours in the hands, soft or slurred speech and little to no facial expressions.

                Omitted Sentences:
                Click here for more information.
                ### End of Article 2 Keypoints ###
                """,
            ),
            (
                "assistant",
                """
                Main keypoint: Introduction to Parkinson's disease
                Content: Parkinson's disease is a neuro-degenerative disease. Parkinson's disease was discovered by James Parkinson in 1817.

                Main keypoint: Symptoms of Parkinson's disease  // Headers and parts of the content for Parkinson's Symptoms have been combined to form a single keypoint.
                Content: Symptoms of PD include:
                    - Barely noticeable tremours in the hands
                    - soft or slurred speech and little to no facial expressions
                    - Muscle rigidity, where muscle remains contracted for a long time
                    - Impaired balance and coordination, sometimes leading to falls.

                Main keypoint: Remedies to Parkinson's disease
                Content: You may take Levodopa prescribed by your doctor to alleviate the symptoms.
                """,
            ),
            ("human", "Merge the keypoints below:\n{Keypoints}"),
        ]
        return compiler_prompt

    @staticmethod
    def return_content_prompt(step: str) -> list[tuple[str, str]]:
        """
        Returns the content optimisation prompt. There are 3 different content prompt that can be returned:

        1. "structure health and conditions": This prompt contains a pre-defined structure that all diseases-and-conditions articles will follow, regardless of optimisation or harmonisation.
        2. "optimise health and conditions": This prompt will optimize the content of all diseases-and-conditions articles.
        3. "extract main article structure": This prompt will produce a template based on the article input. This is used as the first step duing harmonisation of live-healthy articles, where it will extract out the structure of the main article.
        4. "optimise live healthy": This prompt will structure the given content based on the extracted article template. This is used as the second step during the harmonisation of live-healthy articles.

        Args:
            step(str): a String indicating which content prompt should be returned.

        Returns:
            list[tuple[str, str]]: a list containing the content optimisation prompt. {Keypoints} is the only input required to invoke the prompt.
        """
        match step:
            case "structure health and conditions":
                sort_health_conditions_prompt = [
                    (
                        "system",
                        """ You are part of an article re-writing process. Your task is to sort the given keypoints into the following structure:

                            ### Overview of the condition

                            ### Causes and Risk Factors of the condition

                            ### Symptoms and Signs

                            ### Complications

                            ### Treatment

                            ### Prevention

                            ### When to see a doctor

                        Your final answer MUST include these sections with the relevant headers in this specific order and follow the instructions provided.

                        Instructions:
                        1. Prioritize using the predefined section headers listed above.
                        2. Use the original keypoint name as the section header name if it's similar enough to the predefined headers.
                        3. If a keypoint doesn't fit perfectly into one of these sections, follow these steps in order:
                            a. First, try to place it as a subsection under the most relevant main section.
                            b. If it truly doesn't fit as a subsection, only then create a new main section.
                        4. Use the following format for subsections:
                        #### [Subsection Title]
                        5. Do NOT modify the content of the keypoints; your task is to sort them into the most appropriate sections or subsections.
                        6. IMPORTANT: ALL keypoints and their COMPLETE contents MUST be present in the final output. Do not omit or summarize any information. The only exception is if a keypoint does not have any content under it.
                        7. Each piece of information should appear ONLY ONCE in the final output.
                        8. If a predefined section has no content, include the section header with no body text.

                        Sorting Process:
                        1. Read through all keypoints carefully.
                        2. For each keypoint:
                            a. Determine if it fits into one of the predefined sections.
                            b. If not, try to create a subsection under the most relevant main section.
                            c. If it doesn't fit as a subsection, only then create a new main section.
                            d. Use the keypoint's title or a summary of its content as the section or subsection title.
                            e. Place the ENTIRE content of the keypoint into the appropriate section or subsection.
                        3. After sorting all keypoints, review your output to ensure:
                            a. ALL keypoints are included.
                            b. The COMPLETE content of each keypoint is present.
                            c. No information has been omitted or summarized.
                            d. No information appears more than once.
                            e. New main sections are created only when absolutely necessary.


                        The following is an example input:
                            "Main Keypoint: Causes of Influenza
                            Content: Influenza, or the flu, is a contagious respiratory illness caused by influenza viruses. It spreads mainly through droplets when an infected person coughs, sneezes, or talks.

                            Main Keypoint: Self-care
                            Content: When you have the flu, prioritize rest, stay hydrated, and manage symptoms with over-the-counter medications as needed."

                            Main Keypoint: Use of MediSave
                            Content: Additionally, MediSave may be used up to $500/$700 per year for Influenza vaccinations for persons with a higher risk of developing influenza-related complications at both CHAS GP clinics and polyclinics.

                        Corresponding output:
                            ### Overview of the condition

                            ### Causes and Risk Factors of Influenza
                            Influenza, or the flu, is a contagious respiratory illness caused by influenza viruses. It spreads mainly through droplets when an infected person coughs, sneezes, or talks.

                            ### Symptoms and Signs

                            ### Complications

                            ### Treatment
                            #### Self-care
                            When you have the flu, prioritize rest, stay hydrated, and manage symptoms with over-the-counter medications as needed.

                            ### Prevention

                            ### When to see a doctor

                            ### Use of Medisave
                            Additionally, MediSave may be used up to $500/$700 per year for Influenza vaccinations for persons with a higher risk of developing influenza-related complications at both CHAS GP clinics and polyclinics.

                            In the above example, the first keypoint is placed under "Causes and Risk Factors" as its content closely relates to the header.
                            The "Self-care" keypoint doesn't match any predefined headers exactly, but it's most closely related to "Treatment". Therefore, it's added as a subsection under "Treatment"
                            The "Use of MediSave" keypoint doesn't fit well under any predefined headers or as a subsection. As a result, a new main section is created using the original keypoint name.


                        Final Reminders:
                        Adhere to the given structure.
                        Prioritize using the predefined structure, only adding new sections when absolutely necessary.
                        Do not remove any of the predefined sections.
                        Always place new sections next to the most closely related predefined sections.
                        Ensure ALL keypoints, except those without content, and their content are included in your final answer. This is crucial.
                        Each keypoint and its content should appear in ONLY ONE section.
                        Check that each section header is unique.
                        Maintain a logical flow of information throughout the article.

                        """,
                    ),
                    (
                        "human",
                        """
                        Sort the following keypoints:
                        {Keypoints}
                        """,
                    ),
                ]
                return sort_health_conditions_prompt
            case "optimise health and conditions":
                optimise_health_conditions_content_prompt = [
                    (
                        "system",
                        """
                        You are part of an article re-writing process.

                        Your task is to phrase the content from the given article content using the following guidelines and examples.
                        If one of the sections, denoted by ###, has no content, you MUST write your own content based on the header. Your writing MUST be relevant to the header and the topic.
                        You will also be given a set of instructions that you MUST follow.

                        ### Start of content requirements
                            When rewriting the content, your writing MUST meet the requirements stated here.
                            Do NOT change the content structure. ALL headers present in the given content should be presented in your final answer.

                                    You must also use the following guidelines and examples to phrase your writing.

                                    1. Elaborate and Insightful
                                        Your writing should expand upon the given key points and write new content aimed at educating readers on the condition.
                                        You MUST state the primary intent, goals, and a glimpse of information in the first paragraph.

                                    2. Carry a positive tone
                                        Do NOT convey negative sentiments in your writing.
                                        You should communicate in a firm but sensitive way, focusing on the positives of a certain medication instead of the potential risks.
                                        Example: We recommend taking the diabetes medicine as prescribed by your doctor or pharmacist. This will help in the medicine’s effectiveness and reduce the risk of side effects.

                                    3. Provide reassurance
                                        Your writing should reassure readers that the situation is not a lost cause.
                                        Example: Type 1 diabetes can develop due to factors beyond your control. However, it can be managed through a combination of lifestyle changes and medication. On the other hand, type 2 diabetes can be prevented by having a healthier diet, increasing physical activity, and losing weight.

                                    You should write your content based on the required sections step by step.
                                    After each section has been rewritten, you must check your writing with each guideline step by step.

                                    Here is an example you should use to structure your writing:
                                        ### Start of example
                                            1. Overview of Influenza
                                            Influenza is a contagious viral disease that can affect anyone. It spreads when a person coughs, sneezes, or speaks. The virus is airborne and infects people when they breathe it in. Influenza, commonly known as the flu, can cause significant discomfort and disruption to daily life. It typically occurs in seasonal outbreaks and can vary in severity from mild to severe.

                                            2. Causes and Risk Factors
                                            Influenza is caused by the flu virus, which is responsible for seasonal outbreaks and epidemics. The flu virus is classified into three main types: A, B, and C. Types A and B are responsible for seasonal flu epidemics, while Type C causes milder respiratory illness. Factors that increase the risk of contracting influenza include close contact with infected individuals, a weakened immune system, and lack of vaccination. Additionally, those living in crowded conditions or traveling frequently may also be at higher risk.

                                            3. Symptoms and Signs
                                            Some symptoms include: High fever, cough, headache, and muscle aches. Other symptoms include sneezing, nasal discharge, and loss of appetite. Influenza symptoms can develop suddenly and may be accompanied by chills, fatigue, and sore throat. Some individuals may also experience gastrointestinal symptoms such as nausea, vomiting, or diarrhoea, although these are more common in children.

                                            4. Complications of Influenza
                                            The following people are at greater risk of influenza-related complications:
                                            - Persons aged 65 years old and above.
                                            - Children aged between 6 months old to 5 years old.
                                            - Persons with chronic disorders of their lungs, such as asthma or chronic obstructive pulmonary disease (COPD).
                                            - Women in the second or third trimester of pregnancy. Complications can include pneumonia, bronchitis, and sinus infections. In severe cases, influenza can lead to hospitalisation or even death, particularly in vulnerable populations.

                                            5. Treatment and Prevention
                                            Here are some ways to battle influenza and to avoid it:
                                            Treatment: You can visit the local pharmacist to procure some flu medicine. Antiviral medications can help reduce the severity and duration of symptoms if taken early. Over-the-counter medications can alleviate symptoms such as fever and body aches.
                                            Prevention: Avoid crowded areas and wear a mask to reduce the risk of transmission. Hand hygiene is crucial; wash your hands frequently with soap and water or use hand sanitizer. Getting an annual flu vaccine is one of the most effective ways to prevent influenza. The vaccine is updated each year to match the circulating strains.
                                            Treatment: Rest at home while avoiding strenuous activities until your symptoms subside. Stay hydrated and maintain a balanced diet to support your immune system. Over-the-counter medications can provide symptomatic relief, but it is important to consult a healthcare provider for appropriate treatment options.

                                            6. When to See a Doctor
                                            You should visit your local doctor if your symptoms persist for more than 3 days, or when you see fit. Seek medical attention if you experience difficulty breathing, chest pain, confusion, severe weakness, or high fever that does not respond to medication. Prompt medical evaluation is crucial for those at higher risk of complications or if symptoms worsen.
                                        ### End of example

                        ### End of content requirements

                        ### Start of instructions
                            You MUST follow these instructions when writing out your content.

                            1. RETENTION OF INFORMATION
                            Ensure ALL information from the original content is reflected in your final answer.
                            Do NOT omit any details, facts, examples, or specific nouns.
                            If unsure how to rewrite a point, retain it in its original form.

                            2. CONTENT STRUCTURE
                            Do NOT change the content structure or the headers.
                            Do NOT leave any sections empty. Ensure that ALL sections have content.

                            3. ACCURACY AND COMPLETENESS
                            After rewriting each section, review the original content to ensure all points are included.
                            Do NOT abridge or summarize the content. Your task is to restructure, not condense.
                            Double-check that all specific details (e.g., names, places, numbers, criteria) are accurately preserved.

                            4. SPECIFICITY PRESERVATION
                            Maintain the level of specificity present in the original content.
                            Do not generalize specific information (e.g., "Singaporean children" should not become just "children").
                            Preserve mentions of specific programs, subsidies, or healthcare systems

                            5. CLARITY AND PRESENTATION
                            Do NOT include any prompt instructions in your response.
                            The reader must NOT be aware of the prompts or instructions you've been given.

                            6. FINAL CHECK
                            Before submitting, compare your rewritten content with the original to ensure no information has been lost.
                            Verify that your response adheres to all the above instructions.


                        ### End of instructions
                        """,
                    ),
                    (
                        "human",
                        """
                        Rewrite the following sorted content:
                        {sorted_content}
                        """,
                    ),
                ]
                return optimise_health_conditions_content_prompt
            case "extract main live healthy article structure":
                extract_healthy_main_article_structure = [
                    (
                        "system",
                        """
                        You are part of an article rewriting flow. Your task is to analyse and write out a template of the given article's structure and flow.

                        The template will be used by subsequent agents to structure their writing.
                        """,
                    ),
                    (
                        "human",
                        """
                        Analyze the following article and create a template of its structure. Follow these guidelines:

                        Use Markdown formatting for headers (e.g., # for main title, ## for major sections, ### for subsections).
                        Capture the hierarchical structure of the article, including main sections and subsections.
                        For each section, provide a brief description of the expected content in square brackets.
                        Do not include specific content from the original article.
                        Omit formatting tags like "Content:" or "h2 Sub Header:".

                        Here's the article to analyze:
                        {article}
                        Please provide the structure template based on the above guidelines.
                        """,
                    ),
                ]
                return extract_healthy_main_article_structure
            case "structure live healthy":
                sort_live_healthy_prompt = [
                    (
                        "system",
                        """
                        You are part of an article re-writing process. Your task is to sort the given keypoints into the provided structure, creating a cohesive article.
                        """,
                    ),
                    (
                        "human",
                        """
                        Sort the following keypoints into the provided structure, following these guidelines:

                        1. Use the provided structure as a template, maintaining the hierarchy of headers.
                        2. Place each keypoint under the most appropriate section based on the description of each section.
                        3. Present the content as a flowing article, with headers followed directly by relevant text.
                        4. IMPORTANT: Ensure that EVERY single keypoint is included in the final article. None should be left out.
                        5. If a keypoint doesn't fit any existing section:
                            a. Try to broaden your interpretation of existing sections first.
                            b. If it still doesn't fit, create a new section with a descriptive yet generalizable title.
                            c. Place new sections next to the most closely related existing sections.
                        6. Ensure all keypoints are included and the article maintains a logical flow.
                        7. Each keypoint should be placed in one section only to avoid redundancy.

                        Structure:
                        {Structure}
                        Keypoints to sort:
                        {Keypoints}
                        Please provide the sorted article based on the above guidelines.
                        """,
                    ),
                ]
                return sort_live_healthy_prompt

    @staticmethod
    def return_writing_prompt() -> list[tuple[str, str]]:
        """
        Returns the writing guidelines optimisation prompt

        Returns:
            list[tuple[str, str]]: a list containing the writing guidelines optimisation prompt. {ontent} is the only input required to invoke the prompt.
        """

        optimise_writing_prompt = [
            (
                "system",
                """ You are part of an article re-writing process. The article content is aimed to educate readers about a health-related topic and motivate them to take charge of their health.

                Your objective is to rewrite the given article to based on the given guidelines and instructions.
                Your writing should carry a professional, friendly and engaging tone. Do NOT write in a formal tone. Do NOT write in a conversational style as well.

                Follow the personality and voice guidelines below and adhere to the specific instructions provided.
                You should use the given examples to form your final answer.

                Guidelines:
                    1. Welcome your readers warmly, understand their needs, and accommodate them. You should also account for diverse needs and health conditions if applicable.
                    Example: “Living with diabetes doesn't mean you can’t travel. With proper planning, you can still make travel plans safely.”

                    2. Ensure your writing is relevant to the visitor's needs and expectations.
                    Example: “Worried about new COVID-19 variants? Hear from our experts on infectious diseases and learn how you can stay safe!”

                    3. Personalize the experience for visitors with relevant content.
                    Example: “Are you a new mum returning to work soon? Here are some tips to help you maintain your milk supply while you work from the office.”

                    4. Use a positive tone to motivate readers to lead a healthier lifestyle and empathize with their struggles.
                    Example: “It’s normal to feel stressed, worried or even sad with the daily demands of daily life. And it’s okay to reach out for help and support when you need it.”

                    5. Your writing should carry a casual and warm tone that is caring, sensitive, warm, and tactful.
                    Example: “It’s never fun to see your little one unwell". Look out for symptoms like diarrhea, throwing up, tummy aches, and possibly a fever.”

                    6. Show concern for the reader’s current health state without judgment.
                    Example: "We admire you for taking care of your loved ones. But have you taken some time for yourself lately? Here are some ways you can practice self-care."

                    7. Be respectful to all visitors, regardless of medical condition, race, religion, gender, age, etc.
                    Example: "Diabetes affects people of all ages, genders, and backgrounds. With the right care and support, people living with diabetes can lead healthy and fulfilling lives."

                    8. Use relatable scenarios related to everyday items and activities.
                    Example: "Encourage plenty of rest. Sometimes a cozy blanket and a favorite movie can do wonders!"

                    9. Your answer should have a catchy introduction written in a warm and engaging tone, aimed at grabbing the reader's attention while outlining the content clearly.

                    10. Your conclusion should outline clearly subsequent steps and call-to-actions for the readers. Use a warm and engaging tone.

                Check through each guideline carefully.

                ### Start of instructions
                    Do not summarise the content and your final answer should have minimal loss in information when compared to the original content.
                    Your answer should still flow like a regular article with appropriate spacing and paragraph structure.

                    Your answer MUST be in British English.
                    Your answer MUST be between 300 to 1500 words.
                    Your answer should also contain a close word count to the original content.
                    You MUST remove ALL instances of "Main keypoint" and "Sub keypoint" from the headers. Your answer must be a final readable article with appropriate headers. Otherwise, keep the original headers.

                    Mandatory Use of Guidelines: Use the writing guidelines above to rewrite the content.
                    You MUST NOT change any part of the article's structure. Your task is to simply rewrite the content, not change the article structure.
                    No Prompt Instructions: Do not include any of these prompt instructions in your response. The reader should not be aware of these prompts.
                ### End of instructions
                """,
            ),
            ("human", "Rewrite the following content:\n{Content}"),
        ]
        return optimise_writing_prompt

    @staticmethod
    def return_hemingway_readability_optimisation_prompt(
        step: str,
    ) -> list[tuple[str, str]]:
        """
        Returns the hemingway_readability_optimisation_prompt. There are 4 possible hemingway_readability_optimisation_prompt:

        1. "shortening sentences": This prompt is used to shorten sentences in a given text.
        2. "simplifying complex terms": This prompt is used to identify complex terms and replace them with simpler synonyms or common phrases.
        3. "breaking into bullet points": This prompt is used to identify long sentences with multiple commas and break them up into bullet points.
        4. "cutting out redundant areas": This prompt is used to shorten the writing by cutting out redundant areas.

        All 4 prompts should be used to improve the hemmingway readability score of an article.

        Args:
            step(str): a String indicating the step in which the readability optimisation node is at.

        Returns:
            list[tuple[str, str]]: a list containing the hemingway_readability_optimisation_prompt. {content} is the only input required to invoke the prompt.

        Note:
            The prompt is solely applicable for Health and Conditions
        """
        match step:
            case "shortening sentences":
                hemingway_readability_optimisation_prompt = [
                    (
                        "system",
                        """You are part of an article rewriting process. Your task is to shorten long sentences by breaking them up into multiple sentences.

                        There should not be any loss of key information when breaking down the long sentences into their shorter counterparts.

                        Your writing should carry a friendly and engaging tone. Do NOT write in a professional and formal tone.

                        Do not change the article structure such as the headers.
                        Do not alter any bullet points.

                        Let's think this step by step

                        Example 1
                        1. Rewrite the following content:
                            "Regular exercise is crucial for maintaining good health. Start with a warm-up to prepare your muscles, and it’s important to stretch properly before any workout, this helps prevent injuries and improves flexibility. Incorporating both cardio and strength training into your routine can help you build endurance and muscle. Don’t forget to cool down afterward to allow your body to recover."

                        2. Start by identifying long sentences. This is a long sentence in the content:

                            "Start with a warm-up to prepare your muscles, and it’s important to stretch properly before any workout, this helps prevent injuries and improves flexibility."

                        3. Break the long sentence into shorter sentences with the same meaning. The other sentences are not long, hence they will not be rewritten.

                        Your final answer:
                            "Regular exercise is crucial for maintaining good health. Start with a warm-up to prepare your muscles. It’s important to stretch properly before any workout as it helps prevent injuries and improves flexibility. Incorporating both cardio and strength training into your routine can help you build endurance and muscle. Don’t forget to cool down afterward to allow your body to recover."

                        """,
                    ),
                    ("human", "Rewrite the following content: \n {content}"),
                ]
                return hemingway_readability_optimisation_prompt

            case "simplifying complex terms":
                hemingway_readability_optimisation_prompt = [
                    (
                        "system",
                        """You are part of an article rewriting process. Your task is to replace complex terms and phrases with simpler synonyms or with a simpler phrase.

                        There should not be any loss of key information when explaining the complex terms simply. The simple phrasing should also be understandable by a grade 9 student.

                        Your writing should carry a friendly and engaging tone. Do NOT write in a professional and formal tone.

                        Do not change the article structure such as use of headers and bullet points structure.

                        Let's think this through step by step.

                        Example 1
                        1. Rewrite the following content:
                            "Before arriving at the hospital, the patient was feeling unwell. The patient exhibited symptoms of dyspnea and tachycardia, necessitating an immediate intervention to stabilize his condition. Thankfully, after treatment, his condition began to improve."

                        2. Start by identifying complex words and phrases. Here are some complex terms not easily understood:

                            "dyspnea", "tachycardia", "necessitating an immediate intervention"

                        3. Replace these words and phrases with synonymous words and phrases that are easily understood by a 9th grade student:

                        Your final answer:
                            "Before arriving at the hospital, the patient was feeling unwell. The patient had trouble breathing and a fast heartbeat, so doctors acted quickly to stabilize him. Thankfully, after treatment, his condition began to improve."

                        Example 2
                        1. Rewrite the following content:
                        "The patient complained of a severe headache. She was also feeling nauseous and dizzy. An MRI was ordered to rule out any intracranial pathology, including a potential subarachnoid hemorrhage."

                        2. Start by identifying complex words and phrases. Here are some complex terms not easily understood:

                            "intracranial pathology", "potential subarachnoid hemorrhage"

                        3. Replace these words and phrases with synonymous words and phrases that are easily understood by a 9th grade student:

                        Your final answer:
                            "The doctor ordered an MRI to check for any problems in the brain, including a possible brain bleed."

                        Example 3
                        1. Rewrite the following content:
                            "The patient was diagnosed with myocardial infarction and was immediately administered thrombolytic therapy."

                        2. Start by identifying complex words and phrases. Here are some complex terms not easily understood:

                            "myocardial infarction", "thrombolytic therapy"

                        3. Replace these words and phrases with synonymous words and phrases that are easily understood by a 9th grade student:

                        Your final answer:
                            "The patient had a heart attack and was quickly given medicine to dissolve the blood clot
                        """,
                    ),
                    ("human", "Rewrite the following content: \n {content}"),
                ]
                return hemingway_readability_optimisation_prompt

            case "breaking into bullet points":
                hemingway_readability_optimisation_prompt = [
                    (
                        "system",
                        """You are part of an article rewriting process. Your task is to break up long sentences with more than 3 commas and items into bullet points. Follow the guide below on how you should approach the content.

                        Let's think step by step.

                        Example 1:

                        1. Rewrite the long sentences in this content.
                            "Taking care of your body and mind is crucial for a long and healthy life. To maintain good health, it's important to eat a balanced diet rich in fruits and vegetables, drink plenty of water, get at least 8 hours of sleep each night, exercise regularly, and avoid harmful habits like smoking and excessive alcohol consumption. Regular check-ups with your doctor are also essential. Don't forget to manage stress effectively, else you risk falling sick frequently."

                        2. Start by analyzing each sentences indvidually. This is a long sentence with more than 3 commas and listing out multiple items:

                            "To maintain good health,
                            it's important to eat a balanced diet rich in fruits and vegetables,
                            drink plenty of water,
                            get at least 8 hours of sleep each night,
                            exercise regularly,
                            and avoid harmful habits like smoking and excessive alcohol consumption."

                        3. We will now break this sentence into bullet points, with each item being a separate bullet point. The rest of the sentences maintains their original structure as they have do not have more than 3 commas and are not identified as long sentences.

                        Your final answer:
                            "Taking care of your body and mind is crucial for a long and healthy life.

                            To maintain good health, it's important to:
                                - eat a balanced diet rich in fruits and vegetables,
                                - drink plenty of water,
                                - get at least 8 hours of sleep each night,
                                - exercise regularly,
                                - avoid harmful habits like smoking and excessive alcohol consumption

                            Regular check-ups with your doctor are also essential. Don't forget to manage stress effectively, else you risk falling sick frequently."

                        Example 2:

                        1. Rewrite the long sentences in this content.
                            "Achieving high productivity requires deliberate effort and effective strategies, you can't be highly productive without a conscious effort. To boost your productivity, it's essential to plan your day ahead, prioritize your tasks, take regular breaks to avoid burnout, stay organized with to-do lists, and minimize distractions like social media and unnecessary meetings. Keep a positive mindset throughout the day. Celebrate small wins to stay motivated."

                        2. Start by analyzing each sentences indvidually. This is a long sentence with more than 3 commas and listing out multiple items:

                            "To boost your productivity,
                            it's essential to plan your day ahead,
                            prioritize your tasks,
                            take regular breaks to avoid burnout,
                            stay organized with to-do lists,
                            and minimize distractions like social media and unnecessary meetings."

                        3. We will now break this sentence into bullet points, with each item being a separate bullet point. The rest of the sentences maintains their original structure as they have do not have more than 3 commas and are not identified as long sentences.

                        Your final answer:
                            "Achieving high productivity requires deliberate effort and effective strategies, you can't be highly productive without a conscious effort.

                            To boost your productivity, you can:
                                - plan your day ahead,
                                - prioritize your tasks,
                                - take regular breaks to avoid burnout,
                                - stay organized with to-do lists,
                                - minimize distractions like social media and unnecessary meetings

                            Keep a positive mindset throughout the day. Celebrate small wins to stay motivated."

                        Evaluate each sentence carefully and only return the rewritten article in your answer.
                            """,
                    ),
                    (
                        "human",
                        """Rewrite the long sentences in this content.\n {content}""",
                    ),
                ]
                return hemingway_readability_optimisation_prompt

            case "cutting out redundant areas":
                hemingway_readability_optimisation_prompt = [
                    (
                        "system",
                        """ You are part of an article rewriting process. Your task is to identify remove redundant writing in the given context while preserving all key information, examples, and specific details.

                        There should not be any loss of key information when removing these redundant information.

                        Your writing should carry a friendly and engaging tone. Do NOT write in a professional and formal tone.

                        Instructions:
                        1. Do not change the article structure such as use of headers.
                        2. Do not alter any bullet points.
                        3. Preserve ALL examples present in the original article.
                        4. Retain ALL nouns, proper names, and specific terms present in the original article.

                        You can use this example to help you identify redundant phrasing and to structure your answer.

                        ### Start of example
                        Original content: "In order to ensure that the project is completed on time, it is absolutely essential that all team members work together in a collaborative manner."

                        Your answer: "To finish the project on time, all team members must work together."
                        ### End of example

                        Final Checks:
                        Before submitting your rewritten content, review it against the original to ensure:
                        1. All examples are preserved.
                        2. Lists of items or types (e.g., patient groups, symptoms) are complete.
                        3. The core meaning and emphasis of each sentence is maintained.
                        4. No key information or details have been lost in the process of removing redundancy.
                        """,
                    ),
                    ("human", "Rewrite the following content {content}"),
                ]

                return hemingway_readability_optimisation_prompt

    @staticmethod
    def return_personality_evaluation_prompt() -> list[tuple[str, str]]:
        """
        Returns the personality evaluation prompt

        Returns:
            list[tuple[str, str]]: a list containing the personality evaluation prompt. {Content} is the only input required to invoke the prompt.
        """

        personality_evaluation_prompt = [
            (
                "system",
                """
                Your task is to evaluate a given content and check if it follows the set of personality and voice guidelines provided below.

                ### Start of guidelines
                    You should check these guidelines with the given content carefully step by step to determine if it follows the personality.

                    1. Approachable
                        Guidelines: You should welcome your reader warmly, understand their needs and accommodate to them wherever possible. You should also account for diverse needs and differing health conditions of all visitors

                    2. Progressive
                        Guidelines: Your writing should be relevant to the visitor's needs and expectations.

                    3. Crafted
                        Guidelines: You should personalize experiences for visitors with relevant content in the article.

                    4. Optimistic
                        Guidelines: Your writing should carry a positive tone to motivate visitors to lead a healthier lifestyle. You should also empathise with the struggles of the readers.

                    5. Personal
                        Guidelines: Your writing should carry a tone that is caring, sensitive, warm and tactful

                    6. Human-centric
                        Guidelines: Your writing should concern for visitors’ current health state, without judgment or prescriptive

                    7. Respectful
                        Guidelines: You should craft your writing to be respectful to visitors regardless of medical condition, race, religion, gender, age, etc.
                ### End of guidelines

                Your final answer MUST either be "True" or "False".
                If the given content does not fit the writing guidelines, your final answer will be "False".
                Otherwise, if you determine that the given content adheres to the writing guidelines, your final answer will be "True".
                """,
            ),
            ("human", "Evaluate the following content:\n{Content}"),
        ]

        return personality_evaluation_prompt

    @staticmethod
    def return_title_prompt(step: str) -> list[tuple[str, str]]:
        """
        Returns the specified title optimisation prompt. There are 2 possible title optimisation prompts, namely:

        1. "optimise title": This prompt is used to instruct the LLM agent to optimise the article title based on several guidelines from the content playbook.
            - Note that this prompt takes in 2 inputs:
                1. {feedback}: The title optimisation feedback extracted from the User Annotation Excel file
                2. {content}: Content for the llm to write the new optimised title.
        2. "shorten title": This prompt is used to shorten the optimised titles to ensure the optimised titles meet the length requirements.

        Args:
            step(str): a String indicating the step in which the title optimisation node is at and which title prompt to return.

        Returns:
            list[tuple[str, str]]: a list containing the title optimisation prompt. {Content} is the only input required to invoke the prompt.
        """
        match step:
            case "optimise title":
                optimise_title_prompt = [
                    (
                        "system",
                        """You are part of an article re-writing process. Your task is to write out 3 new and improved article title using the content given below and the given feedback.

                        Each title MUST be less than 65 characters including spaces.
                        You do not need to justify how your titles addresses the given feedback.
                        You will also be given a set of instructions and a set of guidelines below.
                        You MUST follow the given instructions.
                        You MUST consider the given guidelines and you should use the given examples to create your title.

                        ### Start of guidelines
                            These guidelines are qualities that your title should have and you must consider ALL of the given guidelines.
                            You should check these guidelines carefully step by step.
                            You should use the given examples to craft your title.

                            1. Clear and informative
                                Guideline: Your title should reflect the content while being brief and direct.
                                Example: "Strategies You can Employ for a Healthy Heart"

                            2. Tailored to the audience
                                Guideline: Your title should consider the demographics, interest and audience needs.
                                Example: "How to Balance Work and Caring for a Loved One"

                            3. Highlights the benefit
                                Guideline: Your title should communicate the value or benefit to readers clearly
                                Example: "Energy-boosting Recipes to Fuel Your Every Day"

                            4. Appeals to the reader's emotions
                                Guideline: You should utilize powerful and evocative words to create a stronger connection with your audience
                                Example: "Embracing Inner Healing: Overcoming Anxiety and Cultivating Emotional Resilience"

                            5. Attention grabbing
                                Guideline: Your title should be captivating, using compelling language or call to action to entice readers to click and read. However, you MUST avoid a clickbait title.
                                Example: "Unveiling the Science Behind Shedding Pounds"

                            6.	Use action-oriented language
                                Guideline: Your title should use verbs or phrases that convey action or create a sense of urgency
                                Example: "Discover the Effects of a Skin Care Routine that Works for You"

                            7.  Inspire readers to develop healthy behaviours
                                Guideline: Your title should motivate readers to take action
                                Example: "Prioritise Your Well-being with Regular Health Screenings"

                            Consider the guidelines step by step carefully.
                        ### End of guidelines

                        ### Start of instructions
                            You MUST provide 3 different titles. The reader will choose one title out of the choices available. Use the following example to structure your titles.
                                ### Start of title format example
                                    1. Title 1
                                    2. Title 2
                                    3. Title 3
                                ### End of title format example
                            Check through the length of each title carefully. Each title MUST be less than 65 characters including the spaces.
                            You must write your titles such that they address points in the feedback given.
                            You MUST consider the guidelines and the examples when writing out the title.
                            You must NOT reveal any part of the prompt in your answer.
                            Your answer must strictly only include the titles.
                        ### End of instructions""",
                    ),
                    (
                        "human",
                        """Address the following feedback with your titles:
                        {feedback}

                        Use the following content and write your own titles:
                        {content}
                        """,
                    ),
                ]

                return optimise_title_prompt
            case "shorten title":
                shorten_title = [
                    (
                        "system",
                        """
                        Your task is to ensure that each meta title's length is less than 65 characters.

                        The number of characters in each title includes spaces between the words.

                        Follow these steps carefully.

                        Example 1:

                            1. Check through these titles:

                                "1. Simple Steps to a Healthy Lifestyle: Tips for Everyday Well-Being
                                2. How to Live a Healthier Life: Essential Habits for Long-Term Wellness
                                3. Discover the Secrets to a Healthier Life: Comprehensive Guide to Nutrition, Exercise, and Mental Well-Being"


                            2. Count the number of characters for each title, including the spaces between each word. Identify titles with more than 65 characters.

                                This title has 107 characters with spaces:
                                    "Discover the Secrets to a Healthier Life: Comprehensive Guide to Nutrition, Exercise, and Mental Well-Being"

                            3. Rewrite the identified titles such that they now meet the length requirements.

                                This shortened version has 62 characters with spaces, which meets the length requirements now:
                                    "Living Healthy: Tips to Nutrition, Exercise, and Mental Health"

                            4. Return your rewritten titles as the final answer.

                                Your final answer:
                                "1. Simple Steps to a Healthy Lifestyle: Tips for Everyday Well-Being
                                2. How to Live a Healthier Life: Essential Habits for Long-Term Wellness
                                3. Living Healthy: Tips to Nutrition, Exercise, and Mental Health"

                        Your answer should ONLY include the new titles.
                    """,
                    ),
                    (
                        "human",
                        """Check through these titles:
                        {content}
                        """,
                    ),
                ]

                return shorten_title

    @staticmethod
    def return_meta_desc_prompt(step: str) -> list[tuple[str, str]]:
        """
        Returns the specified meta description optimisation prompt. There are 2 possible meta description optimisation prompts, namely:

        1. "optimise meta desc": This prompt is used to instruct the LLM agent to optimise the meta desc based on several guidelines.
            - Note that this prompt takes in 2 inputs:
                1. {feedback}: The meta description optimisation feedback extracted from the User Annotation Excel file
                2. {content}: Content for the llm to write the new optimised meta descriptions.
        2. "shorten meta desc": This prompt is used to shorten the optimised meta descriptions to ensure the optimised meta descriptions meet the length requirements.

        Args:
            step(str): a String indicating the step in which the meta description optimisation node is at and which meta description prompt to return.

        Returns:
            list[tuple[str, str]]: a list containing the meta description optimisation prompt. {Content} is the only input required to invoke the prompt.
        """
        match step:
            case "optimise meta desc":
                optimise_meta_desc_prompt = [
                    (
                        "system",
                        """ You are part of anarticle re-writing process. Your task is to write new and improved meta descriptions using the content given below and the given feedback.

                        Your answer should be formatted as such:
                            1. Meta description 1
                            2. Meta description 2
                            3. Meta description 3

                        Each meta description you write MUST be MORE than 100 characters and LESS than 130 characters including spaces between words.
                        You do not need to justify how your meta descriptions addresses the given feedback.

                        ### Start of guidelines
                        Meta descriptions are short, relevant and specific description of topic/contents in the article.
                        The meta description you write is used by Search Engines to create interesting snippet to attract readers.
                        You should check these guidelines carefully step by step.

                        1. Use an active voice and make it actionable
                        2. Make sure it matches the content of the page
                        3. Make it unique
                        ### End of guidelines

                        Check through your writing carefully.

                """,
                    ),
                    (
                        "human",
                        """Address the following feedback with your meta descriptions:
                        {feedback}

                        Use the following content to write your meta descriptions:
                        {content}""",
                    ),
                ]

                return optimise_meta_desc_prompt
            case "shorten meta desc":
                shorten_meta_desc_prompt = [
                    (
                        "system",
                        """
                        Your task is to ensure that each meta description's length is between 100 characters and 130 characters, inclusive of both numbers.

                        The number of characters in each meta description includes spaces between the words.

                        Follow these steps carefully

                        Example 1:

                            1. Check through these meta descriptions:

                                "1. Discover how the Healthy Eating Campaign 2023 empowered individuals to embrace nutritious diets with easy, tasty recipes.
                                2. Explore the impact of the Healthy Eating Campaign, where Nestle and Whole Foods encouraged employeeseat health meals daily.
                                3. Learn about the Healthy Eating Campaign 2023, a nationwide initiative that motivated thousands to adopt better eating habits through accessible education, community support, and creative challenges, driving significant improvements in public health."
"
                            2. Check the number of characters for each meta description, including the spaces between each word. Identify meta descriptions with less than 100 characters or more than 130 characters.

                                This meta description has 249 characters with spaces:
                                    "3. Learn about the Healthy Eating Campaign 2023, a nationwide initiative that motivated thousands to adopt better eating habits through accessible education, community support, and creative challenges, driving significant improvements in public health."

                            3. Rewrite the identified meta descriptions such that they now meet the length requirements.

                                This shortened version has 123 characters with spaces, which meets the length requirements now:
                                    "3. Learn how the Healthy Eating Campaign 2023 inspired healthier eating with education, community support, and fun challenges."

                            4. Return your rewritten meta descriptions as the final answer.

                                Your final answer:
                                    "1. Discover how the Healthy Eating Campaign 2023 empowered individuals to embrace nutritious diets with easy, tasty recipes.
                                    2. Explore the impact of the Healthy Eating Campaign, where Nestle and Whole Foods encouraged employeeseat health meals daily.
                                    3. Learn how the Healthy Eating Campaign 2023 inspired healthier eating with education, community support, and fun challenges."

                        Your answer should ONLY include the new meta descriptions.
                    """,
                    ),
                    (
                        "human",
                        """Check through these meta descriptions:
                        {content}
                        """,
                    ),
                ]

                return shorten_meta_desc_prompt

    @staticmethod
    def return_changes_summariser_prompt() -> list[tuple[str, str]]:
        """
        Returns the change summariser prompt

        Returns:
            list[tuple[str, str]]: a list containing the change summariser prompt. {Orignial} and {Optimized} are the only inputs required to invoke the prompt.
        """
        change_summariser_prompt = [
            (
                "system",
                """
                You will be given two versions of an article: the original version and the optimised version after rewriting. Your task is to analyze and summarize the differences between these two versions in 2-3 sentences, with a focus on how the article quality has improved.
                Below is a list of criterias you can focus on while writing the summary:


                Content Changes:

                Highlight any information, sections, or key points that have been added or removed to the optimized version.
                Discuss how these additions or removals enhance or change the article's message, clarity, or effectiveness.


                Structural Changes:

                Note any significant changes in the organization or structure of the content between the two versions.
                Explain how these structural changes might affect the reader's understanding or engagement with the article.


                Language and Style:

                Identify any notable changes in language, tone, or writing style between the original and optimized versions.
                Discuss how these changes might impact the article's readability, engagement, or target audience.


                Overall Impact:

                Provide a brief assessment of whether the changes in the optimized version have improved the article's quality, clarity, or effectiveness compared to the original version.


                Please provide your analysis in a clear and concise manner in 2-3 sentences.
                """,
            ),
            (
                "human",
                """
                Compare the original and optimised articles and come up with a summary of the changes made.

                Original article:
                {Original}

                Optimised article:
                {Optimised}
                """,
            ),
        ]
        return change_summariser_prompt


class LlamaPrompts(LLMPrompt):
    """
    This class contains methods that stores and returns the prompts for Llama3 models.

    This class inherits from the LLMPrompt class

    Refer to https://llama.meta.com/docs/model-cards-and-prompt-formats/meta-llama-3/ for more information.
    """

    @staticmethod
    def return_readability_evaluation_prompt() -> str:
        """
        Returns the readability evaluation prompt where the chain output will be a string

        Returns:
            str : a string containing the readability evaluation prompt. {Article} is the only input required to invoke the prompt.
        """

        readability_evaluation_prompt = """
            <|begin_of_text|><|start_header_id|>system<|end_header_id|>
            I want you to act as an expert in readability analysis. Your task is to evaluate and critique the readability of the provided article. Your analysis should cover the following aspects:

            1. **Sentence Structure**: Assess the complexity of sentences. Identify long, convoluted sentences and suggest ways to simplify them.
            2. **Vocabulary**: Evaluate the complexity of the vocabulary used. Highlight any overly complex words and suggest simpler alternatives where appropriate.
            3. **Coherence and Flow**: Analyze the coherence and logical flow of the text. Point out any abrupt transitions or lack of clarity and provide suggestions for improvement.
            4. **Readability Metrics**: Calculate and provide readability scores using metrics such as Flesch-Kincaid Grade Level, Gunning Fog Index, and any other relevant readability indices.
            5. **Overall Assessment**: Summarize the overall readability of the article, providing specific examples and actionable recommendations for improvement.

            Please provide a detailed analysis and critique following the above criteria.
            <|eot_id|>
            <|start_header_id|>user<|end_header_id|>
            Article:
            {Article}
            <|eot_id|>
            <|start_header_id|>assistant<|end_header_id|>
            Answer:
        """

        return readability_evaluation_prompt

    @staticmethod
    def return_structure_evaluation_prompt() -> str:
        """
        Returns the structure evaluation prompt where the chain output will be a string

        Returns:
            str : a string containing the structure evaluation prompt. {Article} is the only input required to invoke the prompt.
        """

        structure_evaluation_prompt = """
            <|begin_of_text|><|start_header_id|>system<|end_header_id|>
            Objective: Critique the content structure of the article, evaluating its effectiveness and coherence based on the following criteria -

            1. Opening
            Headline
            -   Does the headline grab attention and stay relevant to the content?
            -   Does it clearly convey the main topic or benefit of the article?

            Introduction
            -   Does the introduction hook the reader quickly and effectively?
            -   Is the relevance of the topic established early on?
            -   Does the introduction outline the content of the post clearly?

            2. Content Structure
            Main Body
            -   Are subheadings used effectively to organize content?
            -   Are paragraphs short, focused, and easy to read?
            -   Does the article incorporate lists where appropriate?
            -   Are examples or anecdotes included to illustrate points?

            Overall Structure
            -   Does the article follow a logical flow of ideas?
            -   Do sections build on each other in a cohesive manner?
            -   Are transitions between sections smooth and logical?

            3. Writing Style
            Tone and Language
            -   Is the tone conversational and accessible to the target audience?
            -   Does the article avoid unexplained jargon or overly technical language?
            -   Is the language appropriate for the audience's level of knowledge?

            Engagement
            -   Are questions or prompts used to engage the reader?
            -   Is "you" language used to make the content more relatable and direct?

            4. Closing
            Call-to-Action (CTA)
            -   Are clear next steps for the reader provided?
            -   Is the CTA strategically placed and compelling?

            Conclusion
            -   Are the key points of the article summarized effectively?
            -   Does the conclusion reinforce the main message?
            -   Does it leave the reader with something to think about or a memorable takeaway?

            5. Overall Effectiveness
            Value
            -   Does the article provide practical, actionable information?
            -   Does it fulfill the promise made by the headline and introduction?

            Length
            -   Is the length appropriate for the topic and audience (generally 300-1500 words)?
            -   Is the content thorough without unnecessary padding?

            Instructions:
            1.  Carefully read through the article.
            2.  Use the criteria above to evaluate each section.
            3.  Provide detailed feedback, noting strengths and areas for improvement.
            4.  Suggest specific changes or enhancements where applicable.
            <|eot_id|>
            <|start_header_id|>user<|end_header_id|>
            Article:
            {Article}
            <|eot_id|>
            <|start_header_id|>assistant<|end_header_id|>
            Answer:
        """

        return structure_evaluation_prompt

    @staticmethod
    def return_title_evaluation_prompt() -> str:
        """
        Returns the title evaluation prompt where the chain output will be a string

        Returns:
            str : a string containing the title evaluation prompt. {Title} and {Article} are the inputs required to invoke the prompt.
        """

        title_evaluation_prompt = """
            <|begin_of_text|><|start_header_id|>system<|end_header_id|>
            Objective: Assess the relevance of the article title by qualitatively comparing it with the content of the article, ensuring a detailed and contextual analysis.

            Steps to Follow:
            1.  Identify the Title:
            -   What is the title of the article?

            2.  Analyze the Title:
            -   What main topic or benefit does the title convey?
            -   Is the title specific and clear in its message?

            3.  Review the Content:
            -   Read the entire article carefully.
            -   Summarize the main points and key themes of the article.
            -   Note any specific sections or statements that align with or diverge from the title's promise.

            4.  Compare Title and Content:
            -   Does the content directly address the main topic or benefit stated in the title?
            -   Are the main themes and messages of the article consistent with the expectations set by the title?
            -   Identify any significant information in the article that is not reflected in the title and vice versa.

            5.  Evaluate Relevance:
            -   Provide a detailed explanation of how well the title reflects the content.
            -   Use specific examples or excerpts from the article to support your evaluation.
            -   Highlight any discrepancies or misalignment between the title and the content.

            6.  Suggestions for Improvement:
            -   If the title is not fully relevant, suggest alternative titles that more accurately capture the essence of the article.
            -   Explain why the suggested titles are more appropriate based on the article's content.

            Example Analysis:
            Title: "10 Tips for Effective Time Management"

            Content Summary:
            -   The article introduces the importance of time management, discusses ten detailed tips, provides examples for each tip, and concludes with the benefits of good time management.

            Comparison and Evaluation:
            -   The title promises "10 Tips for Effective Time Management," and the article delivers on this promise by providing ten actionable tips.
            -   Each section of the article corresponds to a tip mentioned in the title, ensuring coherence and relevance.
            -   Specific excerpts: "Tip 1: Prioritize Your Tasks" aligns with the title's promise of effective time management strategies.
            -   The relevance score is high due to the direct alignment of content with the title.

            Suggested Title (if needed):
            -   "Mastering Time Management: 10 Essential Tips for Success" (if the original title needs more emphasis on mastery and success).

            Instructions:
            1.  Use the steps provided to qualitatively evaluate the relevance of the article title.
            2.  Write a brief report based on your findings, including specific examples and any suggested improvements.
            <|eot_id|>
            <|start_header_id|>user<|end_header_id|>
            Title:
            {Title}

            Article:
            {Article}
            <|eot_id|>
            <|start_header_id|>assistant<|end_header_id|>
            Answer:
        """

        return title_evaluation_prompt

    @staticmethod
    def return_meta_desc_evaluation_prompt() -> str:
        """
        Returns the meta description evaluation prompt where the chain output will be a string

        Returns:
            str : a string containing the meta description evaluation prompt. {Meta} and {Article} are the inputs required to invoke the prompt.
        """

        meta_desc_evaluation_prompt = """
            <|begin_of_text|><|start_header_id|>system<|end_header_id|>
            Objective: Assess the relevance of the article's meta description by comparing it with the content of the article.

            Steps to Follow:
            1.  Identify the Meta Description:
            -   What is the meta description of the article?

            2.  Analyze the Meta Description:
            -   What main topic or benefit does the meta description convey?
            -   Is the meta description clear, concise, and engaging?

            3.  Review the Content:
            -   Read the entire article carefully.
            -   Summarize the main points and key themes of the article.
            -   Note any specific sections or statements that align with or diverge from the meta description.

            4.  Compare Meta Description and Content:
            -   Does the content directly address the main topic or benefit stated in the meta description?
            -   Are the main themes and messages of the article consistent with the expectations set by the meta description?
            -   Identify any significant information in the article that is not reflected in the meta description and vice versa.

            5.  Evaluate Relevance:
            -   Provide a detailed explanation of how well the meta description reflects the content.
            -   Use specific examples or excerpts from the article to support your evaluation.
            -   Highlight any discrepancies or misalignment between the meta description and the content.

            6.  Suggestions for Improvement:
            -   If the meta description is not fully relevant, suggest alternative descriptions that more accurately capture the essence of the article.
            -   Explain why the suggested descriptions are more appropriate based on the article's content.

            Example Analysis:
            Meta Description: "Learn 10 effective time management tips to boost your productivity and achieve your goals."

            Content Summary:
            -   The article introduces the importance of time management, discusses ten detailed tips, provides examples for each tip, and concludes with the benefits of good time management.

            Comparison and Evaluation:
            -   The meta description promises "10 effective time management tips to boost your productivity and achieve your goals," and the article delivers on this promise by providing ten actionable tips.
            -   Each section of the article corresponds to a tip mentioned in the meta description, ensuring coherence and relevance.
            -   Specific excerpts: "Tip 1: Prioritize Your Tasks" aligns with the meta description's promise of effective time management strategies.
            -   The relevance score is high due to the direct alignment of content with the meta description.

            Suggested Meta Description (if needed):
            -   "Discover 10 essential time management strategies to enhance productivity and reach your goals."

            Instructions:
            -   Use the steps provided to evaluate the relevance of the article's meta description.
            -   Write a brief report based on your findings, including specific examples and any suggested improvements.
            <|start_header_id|>user<|end_header_id|>
            Meta Description:
            {Meta}

            Article:
            {Article}
            <|eot_id|>
            <|start_header_id|>assistant<|end_header_id|>
            Answer:
        """

        return meta_desc_evaluation_prompt

    @staticmethod
    def return_researcher_prompt() -> str:
        """
        Returns the researcher prompt

        Returns:
            str: a string containing the researcher prompt. {Article} is the only input required to invoke the prompt.
        """

        researcher_prompt = """
            <|begin_of_text|><|start_header_id|>system<|end_header_id|>
            You are part of a article combination process. Your task is to utilize the keypoint in each article and determine if the sentences under each keypoint are relevant to the keypoint.

            Do NOT paraphrase sentences from the given article when assigning the sentence, you must use each sentence directly from the given content.
            Do NOT modify the keypoint headers.
            If no keypoint header is provided, you may come up with your own keypoint header that MUST be relevant to the content provided
            You may rephrase the keypoint title to better suit the context of the content if required.
            ALL sentences in the same keypoint must be joined in a single paragraph.
            Each sentence must appear only once under the keypoint.
            You do NOT need to categorise all sentences. If a sentence is irrelevant to all key points, you can place it under the last keypoint "Omitted sentences"
            Strictly ONLY include the content and the sentences you omitted in your answer.

            Use the following examples to structure your answer:

            ### Start of Example 1
            Keypoint: Introduction to Parkinson's disease
            Parkinson's is a neurodegenerative disease.
            Buy these essential oils to recover from Parkinson's Disease!
            It is a progressive disorder that affects the nervous system and other parts of the body.
            There are approximately 90,000 new patients diagnosed with PD annually in the US.

            Answer:
            Keypoint: Introduction to Parkinson's disease
            Parkinson's is a neurodegenerative disease. It is a progressive disorder that affects the nervous system and other parts of the body. There are approximately 90,000 new patients diagnosed with PD annually in the US.

            Omitted sentences:
            Buy these essential oils to recover from Parkinson's Disease!
            ### End of Example 1

            ### Start of Example 2
            Keypoint: Tips to maintain your weight
            Consume a high protein, low carb diet.
            Exercise for 30 minutes daily.
            Cut down on consumption of saturated fat and sugary food.
            Read these next: Top 10 power foods to eat recommended by a nutritionist

            Answer:
            Keypoint: Introduction to Parkinson's disease
            Consume a high protein, low carb diet. Exercise for 30 minutes daily. Cut down on consumption of saturated fat and sugary food.

            Omitted sentences:
            Read these next: Top 10 power foods to eat recommended by a nutritionist
            ### End of Example 2

            <|eot_id|>
            <|start_header_id|>user<|end_header_id|>
            Article:
            '''{Article}'''
            <|eot_id|>
            <|start_header_id|>assistant<|end_header_id|>
            Answer:
        """

        return researcher_prompt

    @staticmethod
    def return_compiler_prompt() -> str:
        """
        Returns the compiler prompt

        Returns:
            str: a string containing the prompt for a Compiler LLM. {Keypoints} is the only input required to invoke the prompt.
        """

        compiler_prompt = """
            <|begin_of_text|><|start_header_id|>system<|end_header_id|>
            You are part of a article combination process. Your task is to compare and compile the key points given to you.

            Do NOT paraphrase from the sentences in each keypoint.
            You may add conjunctions and connectors if it improves the flow of the sentences.
            If two key points are identical or very similar, combine the points underneath and remove redundant sentences if required. However, do NOT paraphrase and strictly only add or remove sentences.
            All key points must be returned at the end.
            Return the compiled key points at the end.

            Use the following example to form your article:

            "
            Article 1 key points:
            1. Introduction to Parkinson's disease
            Parkinson's disease is a neuro-degenerative disease

            2. Remedies to Parkinson's disease
            You may take Levodopa prescribed by your doctor to alleviate the symptoms

            Article 2 key points:
            1. History of Parkinson's disease
            Parkinson's disease was discovered by James Parkinson in 1817. It is a neurodegenerative disease.

            2. Symptoms of Parkinson's disease
            Symptoms of PD include: Barely noticeable tremors in the hands, soft or slurred speech and little to no facial expressions.

            Answer:
            1. Introduction to Parkinson's disease
            Parkinson's disease is a neuro-degenerative disease. Parkinson's disease was discovered by James Parkinson in 1817.

            2. Symptoms to Parkinson's disease
            Symptoms of PD include: Barely noticeable tremors in the hands, soft or slurred speech and little to no facial expressions.

            3. Remedies to Parkinson's disease
            You may take Levodopa prescribed by your doctor to alleviate the symptoms
            "
            <|eot_id|>
            <|start_header_id|>user<|end_header_id|>
            Compile the key points below:
            {Keypoints}
            <|eot_id|>
            <|start_header_id|>assistant<|end_header_id|>
            Answer:
        """
        return compiler_prompt

    @staticmethod
    def return_content_prompt() -> str:
        """
        Returns the content optimisation prompt

        Returns:
            str: a string containing the content optimisation prompt. {Keypoints} is the only input required to invoke the prompt.

        Note:
            The prompt is solely applicable for Health and Conditions
        """

        optimise_health_conditions_content_prompt = """
            <|begin_of_text|><|start_header_id|>system<|end_header_id|>
            You are part of a article re-writing process. The article content is aimed to educate readers about a particular health condition or disease.

            Your task is to utilize content from the given key points to fill in for the required sections stated below.
            You will also be given a set of instructions that you MUST follow.

            ### Start of content requirements
                When rewriting the content, your writing MUST meet the requirements stated here.
                If the key points do not contain information for missing sections, you may write your own content based on the header. Your writing MUST be relevant to the header.
                You should emulate your writing based on the specific

                Your final writing MUST include these sections in this specific order. Some sections carry specific instructions that you SHOULD follow.
                    1. Overview of the condition
                        - In this section, your writing should be a brief explanation of the disease. You can assume that your readers have no prior knowledge of the condition.
                    2. Causes and Risk Factors
                    3. Symptoms and Signs
                        In this section, you MUST:
                            - You must list out the symptoms and signs in bullet points form.
                            - You should include a brief explanation before the bullet points in this section.
                    4. Complications
                    5. Treatment and Prevention
                    6. When to see a doctor

                You must also use the following guidelines and examples to phrase your writing.

                1. Elaborate and Insightful
                    Your writing should be expand upon the given key points and write new content aimed at educating readers on the condition.
                    Your MUST the primary intent, goals and glimpse of information in the first paragraph.

                2. Carry a positive tone
                    Do NOT convey negative sentiments in your writing.
                    You should communicate in a firm but sensitive way, focusing on the positives of a certain medication instead of the potential risks.
                    Example: We recommend taking the diabetes medicine as prescribed by your doctor or pharmacist. This will help in the medicine’s effectiveness and reduce the risk of side effects.

                3. Provide reassurance
                    Your writing should reassure readers that the situation is not a lost cause
                    Example: Type 1 diabetes can develop due to factors beyond your control. However, it can be managed through a combination of lifestyle changes and medication. On the other hand, type 2 diabetes can be prevented by having a healthier diet, increasing physical activity, and losing weight.

                4. Break up lengthy sentences
                    You should break up long paragraphs into concise sections or bullet points.
                    You should also avoid lengthy, wordy bullet points.
                    Example: Mothers may unintentionally pass infectious diseases to their babies:
                        • The placenta during pregnancy
                        • Germs in the vagina during birth
                        • Breast milk after birth
                        As different viruses spread through different channels, pregnant women should seek their doctor’s advice regarding necessary screening to protect their baby.

                You should out your content based on the required sections step by step.
                After each section has been rewritten, you must check your writing with each guideline step by step.

                Here is an example you should use to structure your writing:
                    ### Start of example
                        1. Overview of Influenza
                        Influenza is a contagious viral disease that can affect anyone. It spreads when a person coughs, sneezes, or speaks. The virus is airborne and infects people when they breathe it in. Influenza, commonly known as the flu, can cause significant discomfort and disruption to daily life. It typically occurs in seasonal outbreaks and can vary in severity from mild to severe.

                        2. Causes and Risk Factors
                        Influenza is caused by the flu virus, which is responsible for seasonal outbreaks and epidemics. The flu virus is classified into three main types: A, B, and C. Types A and B are responsible for seasonal flu epidemics, while Type C causes milder respiratory illness. Factors that increase the risk of contracting influenza include close contact with infected individuals, weakened immune system, and lack of vaccination. Additionally, those living in crowded conditions or traveling frequently may also be at higher risk.

                        3. Symptoms and Signs
                        Some symptoms include: High fever, cough, headache, and muscle aches. Other symptoms include sneezing, nasal discharge, and loss of appetite. Influenza symptoms can develop suddenly and may be accompanied by chills, fatigue, and sore throat. Some individuals may also experience gastrointestinal symptoms such as nausea, vomiting, or diarrhea, although these are more common in children.

                        4. Complications of Influenza
                        The following people are at greater risk of influenza-related complications:
                        - Persons aged 65 years old and above.
                        - Children aged between 6 months old to 5 years old.
                        - Persons with chronic disorders of their lungs, such as asthma or chronic obstructive pulmonary disease (COPD).
                        - Women in the second or third trimester of pregnancy. Complications can include pneumonia, bronchitis, and sinus infections. In severe cases, influenza can lead to hospitalization or even death, particularly in vulnerable populations.

                        5. Treatment and Prevention
                        Here are some ways to battle influenza and to avoid it:
                        Treatment: You can visit the local pharmacist to procure some flu medicine. Antiviral medications can help reduce the severity and duration of symptoms if taken early. Over-the-counter medications can alleviate symptoms such as fever and body aches.
                        Prevention: Avoid crowded areas and wear a mask to reduce the risk of transmission. Hand hygiene is crucial; wash your hands frequently with soap and water or use hand sanitizer. Getting an annual flu vaccine is one of the most effective ways to prevent influenza. The vaccine is updated each year to match the circulating strains.
                        Treatment: Rest at home while avoiding strenuous activities until your symptoms subside. Stay hydrated and maintain a balanced diet to support your immune system. Over-the-counter medications can provide symptomatic relief, but it is important to consult a healthcare provider for appropriate treatment options.

                        6. When to See a Doctor
                        You should visit your local doctor if your symptoms persist for more than 3 days, or when you see fit. Seek medical attention if you experience difficulty breathing, chest pain, confusion, severe weakness, or high fever that does not respond to medication. Prompt medical evaluation is crucial for those at higher risk of complications or if symptoms worsen.
                    ### End of example

            ### End of content requirements

            ### Start of instructions
                You MUST follow these instructions when writing out your content.

                You MUST follow the content requirements.
                You must use the given key points to FILL IN the required sections.
                You should only use bullet points only if it improves the readability of the content.
                You should only use bullet points list SPARINGLY and only <= 2 sections in your writing should contain bullet points.
                Do NOT include any of the prompt instructions inside your response. The reader must NOT know what is inside the prompts
            ### End of instructions

            <|eot_id|>
            <|start_header_id|>user<|end_header_id|>
            Key points to rewrite:
            {Keypoints}
            <|eot_id|>
            <|start_header_id|>assistant<|end_header_id|>
            Answer:
        """

        return optimise_health_conditions_content_prompt

    @staticmethod
    def return_writing_prompt() -> str:
        """
        Returns the writing guidelines optimisation prompt

        Returns:
            str: a string containing the writing guidelines optimisation prompt. {Content} is the only input required to invoke the prompt.

        Note:
            The prompt is solely applicable for Health and Conditions
        """

        optimise_health_conditions_writing_prompt = """
            <|begin_of_text|><|start_header_id|>system<|end_header_id|>
            You are part of a article re-writing process. The article content is aimed to educate readers about a particular health condition or disease.

            Your task is to rewrite the content based on the a set of personality and voice guidelines, which is provided below.
            You will also be given a set of instructions that you MUST follow.

            Rewrite the content based on the guidelines here.
            ### Start of guidelines
                The goal of rewriting the content is to build credibility and confidence in readers. Every point has a set of guidelines you should adopt in your writing along with an example that you should emulate.
                You should check these guidelines with your writing carefully step by step.

                1. Approachable
                    Guidelines: You should welcome your reader warmly, understand their needs and accommodate to them wherever possible. You should also account for diverse needs and differing health conditions of all visitors
                    Example: “Living with diabetes doesn't mean you can’t travel. With proper planning, you can still make travel plans safely.”

                2. Progressive
                    Guidelines: Your writing should be relevant to the visitor's needs and expectations.
                    Example: “Worried about new COVID-19 variants? Hear from our experts on infectious diseases and learn how you can stay safe!”

                3. Crafted
                    Guidelines: You should personalize experiences for visitors with relevant content in the article.
                    Example: “Are you a new mum returning to work soon? Here are some tips to help you maintain your milk supply while you work from the office.”

                4. Optimistic
                    Guidelines: Your writing should carry a positive tone to motivate visitors to lead a healthier lifestyle. You should also empathise with the struggles of the readers.
                    Example: “It’s normal to feel stressed, worried or even sad with the daily demands of daily life. And it’s okay to reach out for help and support when you need it.”

                5. Personal
                    Guidelines: Your writing should carry a tone that is caring, sensitive, warm and tactful
                    Example: “Breast cancer is known to be asymptomatic in the early stages. That’s why regular screenings can provide early detection and timely intervention.”

                6. Human-centric
                    Guidelines: Your writing should concern for visitors’ current health state, without judgment or prescriptive
                    Example: "We admire you for taking care of your loved ones. But have you taken some time for yourself lately? Here are some ways you can practice self-care."

                7. Respectful
                    Guidelines: You should craft your writing to be respectful to visitors regardless of medical condition, race, religion, gender, age, etc.
                    Example: "Diabetes affects people of all ages, genders and backgrounds. With the right care and support, people living with diabetes can lead healthy and fulfilling lives."
            ### End of guidelines

            ### Start of instructions
                You MUST follow these instructions when writing out your content.

                You must ONLY rewrite the content under each content header. Do NOT modify the content headers.
                You MUST use the writing guidelines given above to rewrite the content.
                You should use the examples given under each keypoint to structure your writing.
                Do NOT combine bullet points into sentences if there are more than 5 bullet points in a section.
                Do NOT include any of the prompt instructions inside your response. The reader must NOT know what is inside the prompts
            ### End of instructions

            <|eot_id|>
            <|start_header_id|>user<|end_header_id|>
            Content:
            {Content}
            <|eot_id|>
            <|start_header_id|>assistant<|end_header_id|>
            Answer:
        """

        return optimise_health_conditions_writing_prompt

    @staticmethod
    def return_title_prompt() -> str:
        """
        Returns the title optimisation prompt

        Returns:
            str: a string containing the title optimisation prompt. {Content} is the only input required to invoke the prompt.
        """

        optimise_title_prompt = """
            <|begin_of_text|><|start_header_id|>system<|end_header_id|>
            You are part of a article re-writing process. The article content is aimed to educate readers about a particular health condition or disease.

            Your task is to write a new and improved article title using the content given below.
            You will also be given a set of instructions and a set of guidelines below.
            You MUST follow the given instructions.
            You MUST consider the given guidelines and you should use the given examples to create your title.

            ### Start of guidelines
                These guidelines are qualities that your title should have and you must consider ALL of the given guidelines.
                You should check these guidelines carefully step by step.
                You should use the given examples to craft your title.

                1. Clear and informative
                    Guideline: Your title should reflect the content while being brief and direct.
                    Example: "Strategies You can Employ for a Healthy Heart"

                2. Tailored to the audience
                    Guideline: Your title should consider the demographics, interest and audience needs.
                    Example: "How to Balance Work and Caring for a Loved One"

                3. Highlights the benefit
                    Guideline: Your title should communicate the value or benefit to readers clearly
                    Example: "Energy-boosting Recipes to Fuel Your Every Day"

                4. Appeals to the reader's emotions
                    Guideline: You should utilize powerful and evocative words to create a stronger connection with your audience
                    Example: "Embracing Inner Healing: Overcoming Anxiety and Cultivating Emotional Resilience"

                5. Attention grabbing
                    Guideline: Your title should be captivating, using compelling language or call to action to entice readers to click and read. However, you MUST avoid a clickbait title.
                    Example: "Unveiling the Science Behind Shedding Pounds"

                6.	Use action-oriented language
                    Guideline: Your title should use verbs or phrases that convey action or create a sense of urgency
                    Example: "Discover the Effects of a Skin Care Routine that Works for You"

                7.  Inspire readers to develop healthy behaviours
                    Guideline: Your title should motivate readers to take action
                    Example: "Prioritise Your Well-being with Regular Health Screenings"
            ### End of guidelines

            ### Start of instructions
                Here are a set of instructions that you MUST follow when crafting out your title.

                You MUST provide 8 different titles. The reader will choose one title out of the choices available. Use the following example to structure your titles.
                    ### Start of title format example
                        1. Title 1
                        2. Title 2
                        3. Title 3
                        4. Title 4
                        5. Title 5
                        6. Title 6
                        7. Title 7
                        8. Title 8
                    ### End of title format example
                Each title MUST be less than 71 characters.
                You MUST write out a title using the given content.
                You MUST consider the guidelines and the examples when writing out the title.
                Consider the guidelines step by step carefully.
                You must NOT reveal any part of the prompt in your answer.
                Your answer must strictly only include the titles.
            ### End of instructions

            <|eot_id|>
            <|start_header_id|>user<|end_header_id|>
            Content:
            {Content}
            <|eot_id|>
            <|start_header_id|>assistant<|end_header_id|>
            Answer:
        """

        return optimise_title_prompt

    @staticmethod
    def return_meta_desc_prompt() -> str:
        """
        Returns the meta description optimisation prompt

        Returns:
            str: a string containing the meta description optimisation prompt. {Content} is the only input required to invoke the prompt.
        """

        optimise_meta_desc_prompt = """
            <|begin_of_text|><|start_header_id|>system<|end_header_id|>
            You are part of a article re-writing process. The article content is aimed to educate readers about a particular health condition or disease.

            Your task is to write new and improved meta descriptions using the content given below.
            You will also be given a set of instructions and a set of guidelines below.
            You MUST follow the given instructions.
            You MUST consider the given guidelines to craft your meta descriptions.

            ### Start of guidelines
            Meta descriptions are short, relevant and specific description of topic/contents in the article.
            The meta description you write is used by Search Engines to create interesting snippet to attract readers.
            You should check these guidelines carefully step by step.

            1. Use an active voice and make it actionable
            2. Include a call to action
            3. Show specifications when needed
            4. Make sure it matches the content of the page
            5. Make it unique
            ### End of guidelines

            ### Start of instructions
            These are the set of instructions that you MUST follow in your writing.
            Check your writing with these instructions step by step carefully.

            You MUST come up with 5 different meta descriptions based on the given content. Use the following example to structure your answer.
                ### Start of meta description format example
                        1. Meta description 1
                        2. Meta description 2
                        3. Meta description 3
                        4. Meta description 4
                        5. Meta description 5
                ### End of meta description format example
            Each meta description you write MUST be MORE than 70 characters and LESS than 160 characters.
            Each meta description you provide MUST accurately summarise the content given below.
            You must NOT reveal any part of the prompt in your answer.
            You must consider the guidelines given and write your meta description based on it.
            Your answer must strictly only include the meta descriptions.
            ### End of instructions

            <|eot_id|>
            <|start_header_id|>user<|end_header_id|>
            Content:
            {Content}
            <|eot_id|>
            <|start_header_id|>assistant<|end_header_id|>
            Answer:
        """

        return optimise_meta_desc_prompt


class MistralPrompts(LLMPrompt):
    """
    This class contains methods that stores and returns the prompts for Mistral models.

    This class inherits from the LLMPrompt class

    Refer to https://community.aws/content/2dFNOnLVQRhyrOrMsloofnW0ckZ/how-to-prompt-mistral-ai-models-and-why?lang=en for more information.
    """

    @staticmethod
    def return_readability_evaluation_prompt() -> str:
        """
        Returns the readability evaluation prompt where the chain output will be a string

        Returns:
            str : a string containing the readability evaluation prompt. {Article} is the only input required to invoke the prompt.
        """

        readability_evaluation_prompt = """
            <s> [INST]
            I want you to act as an expert in readability analysis. Your task is to evaluate and critique the readability of the provided article. Your analysis should cover the following aspects:

            1. **Sentence Structure**: Assess the complexity of sentences. Identify long, convoluted sentences and suggest ways to simplify them.
            2. **Vocabulary**: Evaluate the complexity of the vocabulary used. Highlight any overly complex words and suggest simpler alternatives where appropriate.
            3. **Coherence and Flow**: Analyze the coherence and logical flow of the text. Point out any abrupt transitions or lack of clarity and provide suggestions for improvement.
            4. **Readability Metrics**: Calculate and provide readability scores using metrics such as Flesch-Kincaid Grade Level, Gunning Fog Index, and any other relevant readability indices.
            5. **Overall Assessment**: Summarize the overall readability of the article, providing specific examples and actionable recommendations for improvement.

            Please provide a detailed analysis and critique following the above criteria.

            Article:
            {Article}

            [/INST]
            Answer:
            </s>
        """

        return readability_evaluation_prompt

    @staticmethod
    def return_structure_evaluation_prompt() -> str:
        """
        Returns the structure evaluation prompt where the chain output will be a string

        Returns:
            str : a string containing the structure evaluation prompt. {Article} is the only input required to invoke the prompt.
        """

        structure_evaluation_prompt = """
            <s> [INST]
            Objective: Critique the content structure of the article, evaluating its effectiveness and coherence based on the following criteria -

            1. Opening
            Headline
            -   Does the headline grab attention and stay relevant to the content?
            -   Does it clearly convey the main topic or benefit of the article?

            Introduction
            -   Does the introduction hook the reader quickly and effectively?
            -   Is the relevance of the topic established early on?
            -   Does the introduction outline the content of the post clearly?

            2. Content Structure
            Main Body
            -   Are subheadings used effectively to organize content?
            -   Are paragraphs short, focused, and easy to read?
            -   Does the article incorporate lists where appropriate?
            -   Are examples or anecdotes included to illustrate points?

            Overall Structure
            -   Does the article follow a logical flow of ideas?
            -   Do sections build on each other in a cohesive manner?
            -   Are transitions between sections smooth and logical?

            3. Writing Style
            Tone and Language
            -   Is the tone conversational and accessible to the target audience?
            -   Does the article avoid unexplained jargon or overly technical language?
            -   Is the language appropriate for the audience's level of knowledge?

            Engagement
            -   Are questions or prompts used to engage the reader?
            -   Is "you" language used to make the content more relatable and direct?

            4. Closing
            Call-to-Action (CTA)
            -   Are clear next steps for the reader provided?
            -   Is the CTA strategically placed and compelling?

            Conclusion
            -   Are the key points of the article summarized effectively?
            -   Does the conclusion reinforce the main message?
            -   Does it leave the reader with something to think about or a memorable takeaway?

            5. Overall Effectiveness
            Value
            -   Does the article provide practical, actionable information?
            -   Does it fulfill the promise made by the headline and introduction?

            Length
            -   Is the length appropriate for the topic and audience (generally 300-1500 words)?
            -   Is the content thorough without unnecessary padding?

            Instructions:
            1.  Carefully read through the article.
            2.  Use the criteria above to evaluate each section.
            3.  Provide detailed feedback, noting strengths and areas for improvement.
            4.  Suggest specific changes or enhancements where applicable.

            Article:
            {Article}

            [/INST]
            Answer:
            </s>
        """

        return structure_evaluation_prompt

    @staticmethod
    def return_title_evaluation_prompt() -> str:
        """
        Returns the title evaluation prompt where the chain output will be a string

        Returns:
            str : a string containing the title evaluation prompt. {Title} and {Article} are the inputs required to invoke the prompt.
        """

        title_evaluation_prompt = """
            <s> [INST]
            Objective: Assess the relevance of the article title by qualitatively comparing it with the content of the article, ensuring a detailed and contextual analysis.

            Steps to Follow:
            1.  Identify the Title:
            -   What is the title of the article?

            2.  Analyze the Title:
            -   What main topic or benefit does the title convey?
            -   Is the title specific and clear in its message?

            3.  Review the Content:
            -   Read the entire article carefully.
            -   Summarize the main points and key themes of the article.
            -   Note any specific sections or statements that align with or diverge from the title's promise.

            4.  Compare Title and Content:
            -   Does the content directly address the main topic or benefit stated in the title?
            -   Are the main themes and messages of the article consistent with the expectations set by the title?
            -   Identify any significant information in the article that is not reflected in the title and vice versa.

            5.  Evaluate Relevance:
            -   Provide a detailed explanation of how well the title reflects the content.
            -   Use specific examples or excerpts from the article to support your evaluation.
            -   Highlight any discrepancies or misalignment between the title and the content.

            6.  Suggestions for Improvement:
            -   If the title is not fully relevant, suggest alternative titles that more accurately capture the essence of the article.
            -   Explain why the suggested titles are more appropriate based on the article's content.

            Example Analysis:
            Title: "10 Tips for Effective Time Management"

            Content Summary:
            -   The article introduces the importance of time management, discusses ten detailed tips, provides examples for each tip, and concludes with the benefits of good time management.

            Comparison and Evaluation:
            -   The title promises "10 Tips for Effective Time Management," and the article delivers on this promise by providing ten actionable tips.
            -   Each section of the article corresponds to a tip mentioned in the title, ensuring coherence and relevance.
            -   Specific excerpts: "Tip 1: Prioritize Your Tasks" aligns with the title's promise of effective time management strategies.
            -   The relevance score is high due to the direct alignment of content with the title.

            Suggested Title (if needed):
            -   "Mastering Time Management: 10 Essential Tips for Success" (if the original title needs more emphasis on mastery and success).

            Instructions:
            1.  Use the steps provided to qualitatively evaluate the relevance of the article title.
            2.  Write a brief report based on your findings, including specific examples and any suggested improvements.

            Title:
            {Title}

            Article:
            {Article}

            [/INST]
            Answer:
            </s>
        """

        return title_evaluation_prompt

    @staticmethod
    def return_meta_desc_evaluation_prompt() -> str:
        """
        Returns the meta description evaluation prompt where the chain output will be a string

        Returns:
            str : a string containing the meta description evaluation prompt. {Meta} and {Article} are the inputs required to invoke the prompt.
        """

        meta_desc_evaluation_prompt = """
            <s> [INST]
            Objective: Assess the relevance of the article's meta description by comparing it with the content of the article.

            Steps to Follow:
            1.  Identify the Meta Description:
            -   What is the meta description of the article?

            2.  Analyze the Meta Description:
            -   What main topic or benefit does the meta description convey?
            -   Is the meta description clear, concise, and engaging?

            3.  Review the Content:
            -   Read the entire article carefully.
            -   Summarize the main points and key themes of the article.
            -   Note any specific sections or statements that align with or diverge from the meta description.

            4.  Compare Meta Description and Content:
            -   Does the content directly address the main topic or benefit stated in the meta description?
            -   Are the main themes and messages of the article consistent with the expectations set by the meta description?
            -   Identify any significant information in the article that is not reflected in the meta description and vice versa.

            5.  Evaluate Relevance:
            -   Provide a detailed explanation of how well the meta description reflects the content.
            -   Use specific examples or excerpts from the article to support your evaluation.
            -   Highlight any discrepancies or misalignment between the meta description and the content.

            6.  Suggestions for Improvement:
            -   If the meta description is not fully relevant, suggest alternative descriptions that more accurately capture the essence of the article.
            -   Explain why the suggested descriptions are more appropriate based on the article's content.

            Example Analysis:
            Meta Description: "Learn 10 effective time management tips to boost your productivity and achieve your goals."

            Content Summary:
            -   The article introduces the importance of time management, discusses ten detailed tips, provides examples for each tip, and concludes with the benefits of good time management.

            Comparison and Evaluation:
            -   The meta description promises "10 effective time management tips to boost your productivity and achieve your goals," and the article delivers on this promise by providing ten actionable tips.
            -   Each section of the article corresponds to a tip mentioned in the meta description, ensuring coherence and relevance.
            -   Specific excerpts: "Tip 1: Prioritize Your Tasks" aligns with the meta description's promise of effective time management strategies.
            -   The relevance score is high due to the direct alignment of content with the meta description.

            Suggested Meta Description (if needed):
            -   "Discover 10 essential time management strategies to enhance productivity and reach your goals."

            Instructions:
            -   Use the steps provided to evaluate the relevance of the article's meta description.
            -   Write a brief report based on your findings, including specific examples and any suggested improvements.

            Meta Description:
            {Meta}

            Article:
            {Article}

            [/INST]
            Answer:
            </s>
        """

        return meta_desc_evaluation_prompt

    @staticmethod
    def return_researcher_prompt() -> str:
        """
        Returns the researcher prompt

        Returns:
            str: a string containing the researcher prompt. {Article} is the only input required to invoke the prompt.
        """

        researcher_prompt = """
            <s> [INST]
            You are part of a article combination process. Your task is to identify the key points in the article and categorise each sentence into their respective key points.

            Each keypoint must start with a brief explanation as its title, followed by the respective sentences.
            Do NOT paraphrase sentences from the given article when assigning the sentence, you must use each sentence directly from the given article.
            ALL sentences in the same keypoint must joined be in a single paragraph.
            Each sentence must appear only once under each keypoint.
            You do NOT need to categorise all sentences. If a sentence is irrelevant to all key points, you can place it under the last keypoint "Omitted sentences"

            Strictly ONLY include the key points you have identified and the sentences you omitted in your answer.

            Please respond with "No key points found" if there are no key points identified.

            Use this template to structure your answer:

            "
            Article: Parkinson's is a neurodegenerative disease. It is a progressive disorder that affects the nervous system and other parts of the body. Buy these essential oils! You can support your friends and family members suffering from Parkinson's through constant encouragement. Remind them that having parkinson's is not the end of the road.

            Answer:
            1. Introduction to Parkinson's disease
            Parkinson's is a neurodegenerative disease. It is a progressive disorder that affects the nervous system and other parts of the body.

            2. Supporting a patient with Parkinson's disease
            You can support your friends and family members suffering from Parkinson's through constant encouragement. Remind them that having parkinson's is not the end of the road.

            Omitted sentences
            Buy these essential oils!
            "

            Article:
            {Article}

            [/INST]
            Answer:
            </s>
        """

        return researcher_prompt

    @staticmethod
    def return_compiler_prompt() -> str:
        """
        Returns the compiler prompt

        Returns:
            str: a string containing the prompt for a Compiler LLM. {Keypoints} is the only input required to invoke the prompt.
        """

        compiler_prompt = """
            <s> [INST]
            You are part of a article combination process. Your task is to compile the key points given to you.

            There are multiple articles with their respective key points that you must compile.
            You MUST compile ALL key points from ALL articles given.
            Do NOT paraphrase from the sentences in each keypoint.
            If two key points are identical or very similar, combine the points underneath and remove redundant sentences if required. However, do NOT paraphrase and strictly only add or remove sentences.
            Return the compilation of key points at the end.
            Do NOT return the compiled key points in bullet points.
            Do NOT include key points under omitted sentences in your compilation.

            Use the following example to form your compilation:

            "
            Article 1 key points:
            1. Introduction to Parkinson's disease
            Parkinson's disease is a neuro-degenerative disease

            2. Remedies to Parkinson's disease
            You may take Levodopa prescribed by your doctor to alleviate the symptoms

            Article 2 key points:
            1. History of Parkinson's disease
            Parkinson's disease was discovered by James Parkinson in 1817. It is a neurodegenerative disease.

            2. Symptoms of Parkinson's disease
            Symptoms of PD include: Barely noticeable tremors in the hands, soft or slurred speech and little to no facial expressions.

            Answer:
            1. Introduction to Parkinson's disease
            Parkinson's disease is a neuro-degenerative disease. Parkinson's disease was discovered by James Parkinson in 1817.

            2. Symptoms to Parkinson's disease
            Symptoms of PD include: Barely noticeable tremors in the hands, soft or slurred speech and little to no facial expressions.

            3. Remedies to Parkinson's disease
            You may take Levodopa prescribed by your doctor to alleviate the symptoms
            "

            Below are the key points you will need to compile:
            {Keypoints}

            [/INST]

            Answer:
            </s>
        """

        return compiler_prompt

    @staticmethod
    def return_content_prompt() -> str:
        """
        Returns the content optimisation prompt

        Returns:
            str: a string containing the content optimisation prompt. {Keypoints} is the only input required to invoke the prompt.

        Note:
            The prompt is solely applicable for Health and Conditions
        """

        optimise_health_conditions_content_prompt = """
            <s> [INST]
            You are part of a article re-writing process. The article content is aimed to educate readers about a particular health condition or disease.

            Your task is to compare the given key points with the given requirements below and write your own content to fill in missing sections if necessary.
            You will also be given a set of instructions that you MUST follow.

            ### Start of content requirements
            When rewriting the content, your writing MUST meet the requirements stated here.
            If the key points do not contain information for missing sections, you may write your own content based on the header. Your writing MUST be relevant to the header.
            You should emulate your writing based on the specific

            Your final writing MUST include these sections in this specific order. Some sections carry specific instructions that you SHOULD follow.
                1. Overview of the condition
                    - In this section, your writing should be a brief explanation of the disease. You can assume that your readers have no prior knowledge of the condition.
                2. Causes and Risk Factors
                3. Symptoms and Signs
                    In this section, you must:
                        - You must list out the symptoms and signs in bullet points form.
                        - You should include a brief explanation before the bullet points in this section.
                4. Complications
                5. Treatment and Prevention
                6. When to see a doctor

            You must also use the following guidelines and examples to phrase your writing.
            1. Carry a positive tone
                Do NOT convey negative sentiments in your writing.
                You should communicate in a firm but sensitive way, focusing on the positives of a certain medication instead of the potential risks.
                Example: We recommend taking the diabetes medicine as prescribed by your doctor or pharmacist. This will help in the medicine’s effectiveness and reduce the risk of side effects.

            2. Provide reassurance
                Your writing should reassure readers that the situation is not a lost cause
                Example: Type 1 diabetes can develop due to factors beyond your control. However, it can be managed through a combination of lifestyle changes and medication. On the other hand, type 2 diabetes can be prevented by having a healthier diet, increasing physical activity, and losing weight.

            3. Break up lengthy sentences
                You should break up long paragraphs into concise sections.
                Example: Mothers may unintentionally pass infectious diseases to their babies:
                    • The placenta during pregnancy
                    • Germs in the vagina during birth
                    • Breast milk after birth
                As different viruses spread through different channels, pregnant women should seek their doctor’s advice regarding necessary screening to protect their baby.

            You should out your content based on the required sections step by step.
            After each section has been rewritten, you must check your writing with each guideline step by step.
            ### End of content requirements

            ### Start of instructions
            You MUST follow these instructions when writing out your content.

            You MUST follow the content requirements.
            You must use the given key points to FILL IN the required sections.
            Each sentence should start in a new line, only sentences in bullet points are exempted.
            You should only use bullet points only if it improves the readability of the content.
            You should only use bullet points SPARINGLY and only <= 2 sections in your writing should contain bullet points.
            Do NOT include any of the prompt instructions inside your response. The reader must NOT know what is inside the prompts
            ### End of instructions

            Key points:
            {Keypoints}

            [/INST]
            Answer:
            </s>
        """

        return optimise_health_conditions_content_prompt

    @staticmethod
    def return_writing_prompt() -> str:
        """
        Returns the writing guidelines optimisation prompt

        Returns:
            str: a string containing the writing guidelines optimisation prompt. {Content} is the only input required to invoke the prompt.

        Note:
            The prompt is solely applicable for Health and Conditions
        """

        optimise_health_conditions_writing_prompt = """
            <s> [INST]
            You are part of a article re-writing process. The article content is aimed to educate readers about a particular health condition or disease.

            Your task is to rewrite the content based on the a set of personality and voice guidelines, which is provided below.
            You will also be given a set of instructions that you MUST follow.

            Rewrite the content based on the guidelines here.
            ### Start of guidelines
            The goal of rewriting the content is to build credibility and confidence in readers. Every point has a set of guidelines you should adopt in your writing along with an example that you should emulate.
            You should check these guidelines step by step.

            1. Approachable
                Guidelines: You should welcome your reader warmly, understand their needs and accommodate to them wherever possible. You should also account for diverse needs and differing health conditions of all visitors
                Example: “Living with diabetes doesn't mean you can’t travel. With proper planning, you can still make travel plans safely.”

            2. Progressive
                Guidelines: Your writing should be relevant to the visitor's needs and expectations.
                Example: “Worried about new COVID-19 variants? Hear from our experts on infectious diseases and learn how you can stay safe!”

            3. Crafted
                Guidelines: You should personalize experiences for visitors with relevant content in the article.
                Example: “Are you a new mum returning to work soon? Here are some tips to help you maintain your milk supply while you work from the office.”

            4. Optimistic
                Guidelines: Your writing should carry a positive tone to motivate visitors to lead a healthier lifestyle. You should also empathise with the struggles of the readers.
                Example: “It’s normal to feel stressed, worried or even sad with the daily demands of daily life. And it’s okay to reach out for help and support when you need it.”

            5. Personal
                Guidelines: Your writing should carry a tone that is caring, sensitive, warm and tactful
                Example: “Breast cancer is known to be asymptomatic in the early stages. That’s why regular screenings can provide early detection and timely intervention.”

            6. Human-centric
                Guidelines: Your writing should concern for visitors’ current health state, without judgment or prescriptive
                Example: "We admire you for taking care of your loved ones. But have you taken some time for yourself lately? Here are some ways you can practice self-care."

            7. Respectful
                Guidelines: You should craft your writing to be respectful to visitors regardless of medical condition, race, religion, gender, age, etc.
                Example: "Diabetes affects people of all ages, genders and backgrounds. With the right care and support, people living with diabetes can lead healthy and fulfilling lives."
            ### End of guidelines

            ### Start of instructions
            You MUST follow these instructions when writing out your content.

            You must ONLY rewrite the content under each content header. Do NOT modify the content headers.
            You MUST use the writing guidelines given above to rewrite the content.
            You should use the examples given under each keypoint to structure your writing.
            If the content is given in bullet points, you are to maintain the same structure of the bullet points.
            Do NOT include any of the prompt instructions inside your response. The reader must NOT know what is inside the prompts
            ### End of instructions

            Content:
            {Content}

            [/INST]
            Answer:
            </s>
        """

        return optimise_health_conditions_writing_prompt

    @staticmethod
    def return_title_prompt() -> str:
        """
        Returns the title optimisation prompt

        Returns:
            str: a string containing the title optimisation prompt. {Content} is the only input required to invoke the prompt.
        """

        optimise_title_prompt = """
            <s> [INST]
            You are part of a article re-writing process. The article content is aimed to educate readers about a particular health condition or disease.

            Your task is to write a new and improved article title using the content given below.
            You will also be given a set of instructions and a set of guidelines below.
            You MUST follow the given instructions.
            You MUST consider the given guidelines and you should use the given examples to create your title.

            ### Start of guidelines
                These guidelines are qualities that your title should have and you must consider ALL of the given guidelines.
                You should check these guidelines carefully step by step.
                You should use the given examples to craft your title.

                1. Clear and informative
                    Guideline: Your title should reflect the content while being brief and direct.
                    Example: "Strategies You can Employ for a Healthy Heart"

                2. Tailored to the audience
                    Guideline: Your title should consider the demographics, interest and audience needs.
                    Example: "How to Balance Work and Caring for a Loved One"

                3. Highlights the benefit
                    Guideline: Your title should communicate the value or benefit to readers clearly
                    Example: "Energy-boosting Recipes to Fuel Your Every Day"

                4. Appeals to the reader's emotions
                    Guideline: You should utilize powerful and evocative words to create a stronger connection with your audience
                    Example: "Embracing Inner Healing: Overcoming Anxiety and Cultivating Emotional Resilience"

                5. Attention grabbing
                    Guideline: Your title should be captivating, using compelling language or call to action to entice readers to click and read. However, you MUST avoid a clickbait title.
                    Example: "Unveiling the Science Behind Shedding Pounds"

                6.	Use action-oriented language
                    Guideline: Your title should use verbs or phrases that convey action or create a sense of urgency
                    Example: "Discover the Effects of a Skin Care Routine that Works for You"

                7.  Inspire readers to develop healthy behaviours
                    Guideline: Your title should motivate readers to take action
                    Example: "Prioritise Your Well-being with Regular Health Screenings"
            ### End of guidelines

            ### Start of instructions
                Here are a set of instructions that you MUST follow when crafting out your title.

                You MUST provide 8 different titles. The reader will choose one title out of the choices available. Use the following example to structure your titles.
                    ### Start of title format example
                        1. Title 1
                        2. Title 2
                        3. Title 3
                        4. Title 4
                        5. Title 5
                        6. Title 6
                        7. Title 7
                        8. Title 8
                    ### End of title format example
                Each title MUST be less than 71 characters.
                You MUST write out a title using the given content.
                You MUST consider the guidelines and the examples when writing out the title.
                Consider the guidelines step by step carefully.
                You must NOT reveal any part of the prompt in your answer.
                Your answer must strictly only include the titles.
            ### End of instructions

            Content:
            {Content}

            [/INST]
            Answer:
            </s>
        """

        return optimise_title_prompt

    @staticmethod
    def return_meta_desc_prompt() -> str:
        """
        Returns the meta description optimisation prompt

        Returns:
            str: a string containing the meta description optimisation prompt. {Content} is the only input required to invoke the prompt.
        """

        optimise_meta_desc_prompt = """
            <s> [INST]
            You are part of a article re-writing process. The article content is aimed to educate readers about a particular health condition or disease.

            Your task is to write new and improved meta descriptions using the content given below.
            You will also be given a set of instructions and a set of guidelines below.
            You MUST follow the given instructions.
            You MUST consider the given guidelines to craft your meta descriptions.

            ### Start of guidelines
                Meta descriptions are short, relevant and specific description of topic/contents in the article.
                The meta description you write is used by Search Engines to create interesting snippet to attract readers.
                You should check these guidelines carefully step by step.

                1. Use an active voice and make it actionable
                2. Include a call to action
                3. Show specifications when needed
                4. Make sure it matches the content of the page
                5. Make it unique
            ### End of guidelines

            ### Start of instructions
                These are the set of instructions that you MUST follow in your writing.
                Check your writing with these instructions step by step carefully.

                You MUST come up with 5 different meta descriptions based on the given content. Use the following example to structure your answer.
                    ### Start of meta description format example
                        1. Meta description 1
                        2. Meta description 2
                        3. Meta description 3
                        4. Meta description 4
                        5. Meta description 5
                    ### End of meta description format example
                Each meta description you write MUST be MORE than 70 characters and LESS than 160 characters.
                Each meta description you provide MUST accurately summarise the content given below.
                You must NOT reveal any part of the prompt in your answer.
                You must consider the guidelines given and write your meta description based on it.
                Your answer must strictly only include the meta descriptions.
            ### End of instructions

            Content:
            {Content}

            [/INST]
            Answer:
            </s>
        """

        return optimise_meta_desc_prompt


def num_tokens_from_string(string: str, encoding_name: str = "cl100k_base") -> int:
    """
    Returns the number of tokens in a given string

    Args:
        string (str): the string to tokenize
        encoding_name (str, optional): the encoding name, must be available in OpenAI's tiktoken package. Defaults to "cl100k_base".

    Returns:
        int: the number of tokens
    """

    # Get the encoding from the tiktoken package
    encoding = tiktoken.get_encoding(encoding_name)
    # Count the number of tokens in the list
    num_tokens = len(encoding.encode(string))

    return num_tokens


if __name__ == "__main__":
    prompter = prompt_tool("azure")

    # Save the prompt as a .txt file
    prompt_msgs = prompter.return_meta_desc_evaluation_prompt()
    prompt = ""
    for msg in prompt_msgs:
        prompt += msg[1] + "\n"
    print(prompt_msgs)
    prompt = re.sub(r" +", " ", prompt)
    with open("../docs/meta_desc_evaluation_prompt.txt", "w") as f:
        f.write(prompt)
