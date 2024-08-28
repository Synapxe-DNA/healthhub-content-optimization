class LlamaArchivedPrompts:
    @staticmethod
    def return_researcher_prompt_ver(version: int):
        """
        Returns a specific version of the researcher prompt.

        This function retrieves a previous version of the researcher prompt based on the provided version number. Currently, only version 1 is available.

        Version 1: This prompt instructs the LLM to sort sentences into keypoints determined by itself, without preserving the original headers.

        Args:
            version (int): An integer specifying the version to be retrieved.

        Returns:
            str: The desired version of the researcher prompt as a string.

        Raises:
            ValueError: If an invalid version number is provided.
        """
        match version:
            case 1:
                researcher_prompt = """
                    <|begin_of_text|><|start_header_id|>system<|end_header_id|>
                    You are part of a article combination process. Your task is to identify the keypoints in the article and categorise each sentence into their respective keypoints.

                    Each keypoint must start with a brief explanation as its title, followed by the respective sentences.
                    Do NOT paraphrase sentences from the given article when assigning the sentence, you must use each sentence directly from the given article.
                    ALL sentences in the same keypoint must joined be in a single paragraph.
                    Each sentence must appear only once under each keypoint.
                    You do NOT need to categorise all sentences. If a sentence is irrelevant to all keypoints, you can place it under the last keypoint "Omitted sentences"

                    Strictly ONLY include the keypoints you have identified and the sentences you omitted in your answer.

                    Please respond with "No keypoints found" if there are no keypoints identified.

                    Use this template to structure your answer:

                    "
                    Article: Parkinson's is a neurodegenerative disease. It is a progressive disorder that affects the nervous system and other parts of the body. Buy these essential oils! You can support your friends and family members suffering from Parkinson's through constant encouragement. Remind them that having parkinsons's is not the end of the road.

                    Answer:
                    1. Introduction to Parkinson's disease
                    Parkinson's is a neurodegenerative disease. It is a progressive disorder that affects the nervous system and other parts of the body.

                    2. Supporting a patient with Parkinson's disease
                    You can support your friends and family members suffering from Parkinson's through constant encouragement. Remind them that having parkinsons's is not the end of the road.

                    Omitted sentences
                    Buy these essential oils!
                    "
                    <|eot_id|>
                    <|start_header_id|>user<|end_header_id|>

                    Article: {Article}
                    <|eot_id|>

                    <|start_header_id|>assistant<|end_header_id|>
                    Answer:
                """
                return researcher_prompt

            case _:
                raise ValueError(f"Invalid version number: {version}")

    @staticmethod
    def return_content_prompt_ver(version: int, topic: str):
        """
        Returns a specific version of the content prompt for a given topic.

        This method retrieves a content prompt based on the provided version number and topic. Currently, it only supports
        the "health conditions" topic and version 1.

        Args:
            version (int): An integer specifying the version of the prompt to retrieve.
            topic (str): A string specifying the topic for which to retrieve the prompt.

        Returns:
            str: The desired version of the content prompt as a string.

        Raises:
            ValueError: If an invalid topic or version number is provided.
        """
        match topic.lower():
            case "health conditions":
                match version:
                    case 1:
                        optimise_health_conditions_content_prompt = """
                        <|begin_of_text|><|start_header_id|>system<|end_header_id|>
                        You are part of a article re-writing process. The article content is aimed to educate readers about a particular health condition or disease.

                        Your task is to compare the given keypoints with the requirements below and write your own content to fill in missing sections if necessary.

                        Your final answer must include these sections: Overview of the condition, Causes and Risk Factors, Symptoms and Signs, Complications, Treatment and Prevention, When to see a doctor

                        You must use the given keypoints to FILL IN these sections.
                        If the keypoints do not contain information for missing sections, you may write your own content based on the header. Your writing MUST be relevant to the header.
                        Each sentence should start in a new line, only sentences in bullet points are exempted.
                        You should avoid conveying negative sentiments, communicating in a firm but sensitive way, focusing on the positives of a certain medication instead of the potential risks.
                        You should reassure readers when a situation is not a lost cause.
                        Your answer for each section should be sufficiently elaborate.
                        You should only use bullet points only if it improves the readability of the content, but have less than 2 sections with bullet points.

                        Use the following example on Influenza to structure your answer. Your answer should contain more content and further elaboration on each points.
                        Your answer must maintain the same structure given in the example.

                        ### Start of example
                        1. Overview of Influenza
                        Influenza is a contagious viral disease that can affect anyone. It spreads when a person coughs, sneezes, or speaks.
                        The virus is airborne and infects people when they breathe it in. Influenza, commonly known as the flu, can cause significant discomfort and disruption to daily life.
                        It typically occurs in seasonal outbreaks and can vary in severity from mild to severe.

                        2. Causes and Risk Factors
                        Influenza is caused by the flu virus, which is responsible for seasonal outbreaks and epidemics.
                        The flu virus is classified into three main types: A, B, and C.
                        Types A and B are responsible for seasonal flu epidemics, while Type C causes milder respiratory illness.
                        Factors that increase the risk of contracting influenza include close contact with infected individuals, weakened immune system, and lack of vaccination.
                        Additionally, those living in crowded conditions or traveling frequently may also be at higher risk.

                        3. Symptoms and Signs
                        Some symptoms include: High fever, cough, headache, and muscle aches.
                        Other symptoms include sneezing, nasal discharge, and loss of appetite.
                        Influenza symptoms can develop suddenly and may be accompanied by chills, fatigue, and sore throat.
                        Some individuals may also experience gastrointestinal symptoms such as nausea, vomiting, or diarrhea, although these are more common in children.

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
                        You should visit your local doctor if your symptoms persist for more than 3 days, or when you see fit.
                        Seek medical attention if you experience difficulty breathing, chest pain, confusion, severe weakness, or high fever that does not respond to medication.
                        Prompt medical evaluation is crucial for those at higher risk of complications or if symptoms worsen.
                        ### End of example

                        <|eot_id|>
                        <|start_header_id|>user<|end_header_id|>
                        Keypoints:
                        {Keypoints}
                        <|eot_id|>
                        <|start_header_id|>assistant<|end_header_id|>
                        Answer:
                        """
                        return optimise_health_conditions_content_prompt

                    case _:
                        raise ValueError(
                            f"Invalid version number for health conditions: {version}"
                        )
            case _:
                raise ValueError(f"Invalid topic: {topic}")


class AzureArchivedPrompts:

    @staticmethod
    def return_summarization_prompt_ver(version: int) -> list[tuple[str, str]]:
        """
        Returns a specific version of the summarization prompt.

        This method retrieves a summarization prompt based on the provided version number.
        Currently, only version 1 is available.

        Args:
            version (int): An integer specifying the version of the prompt to retrieve.

        Returns:
            A list of tuples containing the summarization prompt instructions.
            Each tuple contains two strings: the role ("system" or "human") and the prompt text.

        Raises:
            ValueError: If an invalid version number is provided.
        """

        match version:
            case 1:
                evaluation_summary_prompt = [
                    (
                        "system",
                        """
                        Summarize the following text into 3 to 5 sentences. Ensure the summary is concise, succinct, and direct, focusing only on the most essential points.
                        You must maintain the goal and context of providing the critique and recommendation to the individual.
                        """,
                    ),
                    ("human", "Evaluate the following text:\n{text}"),
                ]
                return evaluation_summary_prompt

            case _:
                raise ValueError(f"Invalid version number: {version}")

    @staticmethod
    def return_readability_evaluation_prompt_ver(version: int) -> list[tuple[str, str]]:
        """
        Returns a specific version of the readability evaluation prompt.

        This method retrieves a readability evaluation prompt based on the provided version number.
        Currently, only version 1 is available.

        Args:
            version: An integer specifying the version of the prompt to retrieve.

        Returns:
            A list of tuples containing the readability evaluation prompt instructions.
            Each tuple contains two strings: the role ("system" or "human") and the prompt text.

        Raises:
            ValueError: If an invalid version number is provided.
        """

        match version:
            case 1:
                readability_evaluation_prompt = [
                    (
                        "system",
                        """ I want you to act as an expert in readability analysis.
                        Your task is to evaluate and critique the readability of the provided article. Your analysis should cover the following aspects:

                        1. **Sentence Structure**: Assess the complexity of sentences. Identify long, convoluted sentences and suggest ways to simplify them.
                        2. **Vocabulary**: Evaluate the complexity of the vocabulary used. Highlight any overly complex words and suggest simpler alternatives where appropriate.
                        3. **Coherence and Flow**: Analyze the coherence and logical flow of the text. Point out any abrupt transitions or lack of clarity and provide suggestions for improvement.
                        4. **Readability Metrics**: Calculate and provide readability scores using metrics such as Flesch-Kincaid Grade Level, Gunning Fog Index, and any other relevant readability indices.
                        5. **Overall Assessment**: Summarize the overall readability of the article, providing specific examples and actionable recommendations for improvement.

                        Please provide a detailed analysis and critique following the above criteria.""",
                    ),
                    ("human", "Evaluate the following article:\n {article}"),
                ]
                return readability_evaluation_prompt

            case _:
                raise ValueError(f"Invalid version number: {version}")

    @staticmethod
    def return_structure_evaluation_prompt_ver(version: int) -> list[tuple[str, str]]:
        """
        Returns a specific version of the structure evaluation prompt.

        This method retrieves a structure evaluation prompt based on the provided version number.
        Currently, only version 1 is available.

        Args:
            version: An integer specifying the version of the prompt to retrieve.

        Returns:
            A list of tuples containing the structure evaluation prompt instructions.
            Each tuple contains two strings: the role ("system" or "human") and the prompt text.

        Raises:
            ValueError: If an invalid version number is provided.
        """

        match version:
            case 1:
                structure_evaluation_prompt = [
                    (
                        "system",
                        """
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
                        """,
                    ),
                    ("human", "Evaluate the following article:\n{article}"),
                ]
                return structure_evaluation_prompt

            case _:
                raise ValueError(f"Invalid version number: {version}")

    @staticmethod
    def return_title_evaluation_prompt_ver(version: int) -> list[tuple[str, str]]:
        """
        Returns a specific version of the title evaluation prompt.

        This method retrieves a title evaluation prompt based on the provided version number.
        Currently, only version 1 is available.

        Args:
            version: An integer specifying the version of the prompt to retrieve.

        Returns:
            A list of tuples containing the title evaluation prompt instructions.
            Each tuple contains two strings: the role ("system" or "human") and the prompt text.

        Raises:
            ValueError: If an invalid version number is provided.
        """

        match version:
            case 1:
                title_evaluation_prompt = [
                    (
                        "system",
                        """
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
                        """,
                    ),
                    ("human", """ Title: "10 Tips for Effective Time Management" """),
                    (
                        "assistant",
                        """ Content Summary:
                        -   The article introduces the importance of time management, discusses ten detailed tips, provides examples for each tip, and concludes with the benefits of good time management.

                        Comparison and Evaluation:
                        -   The title promises "10 Tips for Effective Time Management," and the article delivers on this promise by providing ten actionable tips.
                        -   Each section of the article corresponds to a tip mentioned in the title, ensuring coherence and relevance.
                        -   Specific excerpts: "Tip 1: Prioritize Your Tasks" aligns with the title's promise of effective time management strategies.
                        -   The relevance score is high due to the direct alignment of content with the title.

                        Suggested Title (if needed):
                        -   "Mastering Time Management: 10 Essential Tips for Success" (if the original title needs more emphasis on mastery and success). """,
                    ),
                    (
                        "system",
                        """ Instructions:
                        1.  Use the steps provided to qualitatively evaluate the relevance of the article title.
                        2.  Write a brief report based on your findings, including specific examples and any suggested improvements. """,
                    ),
                    (
                        "human",
                        "Evaluate the following title:\n{title} \nUsing the following article:\n{article}",
                    ),
                ]
                return title_evaluation_prompt

            case _:
                raise ValueError(f"Invalid version number: {version}")

    @staticmethod
    def return_meta_desc_evaluation_prompt_ver(version) -> list[tuple[str, str]]:
        """
        Returns a specific version of the meta description evaluation prompt.

        This method retrieves a meta description evaluation prompt based on the provided version number.
        Currently, only version 1 is available.

        Args:
            version: An integer specifying the version of the prompt to retrieve.

        Returns:
            A list of tuples containing the meta description evaluation prompt instructions.
            Each tuple contains two strings: the role ("system", "human" or "assistant") and the prompt text.

        Raises:
            ValueError: If an invalid version number is provided.
        """

        match version:
            case 1:
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

                        6.  Suggestions for Improvement:
                        -   If the meta description is not fully relevant, suggest alternative descriptions that more accurately capture the essence of the article.
                        -   Explain why the suggested descriptions are more appropriate based on the article's content.
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

                        Suggested Meta Description (if needed):
                        -   "Discover 10 essential time management strategies to enhance productivity and reach your goals."
                        """,
                    ),
                    (
                        "system",
                        """ Instructions:
                        -   Use the steps provided to evaluate the relevance of the article's meta description.
                        -   Write a brief report based on your findings, including specific examples and any suggested improvements.
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

            case _:
                raise ValueError(f"Invalid version number: {version}")

    @staticmethod
    def return_researcher_prompt_ver(version) -> list[tuple[str, str]]:
        """
        Returns a specific version of the researcher prompt.

        This method retrieves a researcher prompt based on the provided version number.
        Currently, only version 1 is available.

        Args:
            version: An integer specifying the version of the prompt to retrieve.

        Returns:
            A list of tuples containing the researcher prompt instructions.
            Each tuple contains two strings: the role ("system", "human" or "assistant") and the prompt text.

        Raises:
            ValueError: If an invalid version number is provided.
        """

        match version:
            case 1:
                researcher_prompt = [
                    (
                        "system",
                        """You are part of a article combination process. Your task is to utilize the keypoint in each article and determine if the sentences under each keypoint are relevant to the keypoint.

                        Do NOT paraphrase sentences from the given article when assigning the sentence, you must use each sentence directly from the given content.
                        Do NOT modify the keypoint headers.
                        If no keypoint header is provided, you may come up with your own keypoint header that MUST be relevant to the content provided
                        ALL sentences in the same keypoint must be joined in a single paragraph.
                        Each sentence must appear only ONCE under the keypoint.
                        Not all sentences are relevant to the keypoint header. If a sentence is irrelevant to all keypoints, you can place it under the last keypoint "Omitted sentences".
                        Strictly ONLY include the content and the sentences you omitted in your answer.""",
                    ),
                    (
                        "human",
                        """h2 Sub Header: Introduction to Parkinson's disease
                        Parkinson's is a neurodegenerative disease.
                        Buy these essential oils to recover from Parkinson's Disease!
                        It is a progressive disorder that affects the nervous system and other parts of the body.
                        There are approximately 90,000 new patients diagnosed with PD annually in the US.""",
                    ),
                    (
                        "assistant",
                        """ Keypoint: Introduction to Parkinson's disease
                        Parkinson's is a neurodegenerative disease. It is a progressive disorder that affects the nervous system and other parts of the body. There are approximately 90,000 new patients diagnosed with PD annually in the US.

                        Omitted sentences:
                        Buy these essential oils to recover from Parkinson's Disease!""",
                    ),
                    (
                        "human",
                        """ Keypoint: Tips to maintain your weight
                        Consume a high protein, low carb diet.
                        Exercise for 30 minutes daily.
                        Cut down on consumption of saturated fat and sugary food.
                        Read these next: Top 10 power foods to eat recommended by a nutritionist""",
                    ),
                    (
                        "assistant",
                        """
                        Answer:
                        Keypoint: Introduction to Parkinson's disease
                        Consume a high protein, low carb diet. Exercise for 30 minutes daily. Cut down on consumption of saturated fat and sugary food.

                        Omitted sentences:
                        Read these next: Top 10 power foods to eat recommended by a nutritionist
                        """,
                    ),
                    (
                        "human",
                        "Sort the keypoints below based on the instructions and examples you have received:\n{Article}",
                    ),
                ]
                return researcher_prompt
            case _:
                raise ValueError(f"Invalid version number: {version}")

    def return_content_prompt(version) -> list:
        match version:
            case 1:
                optimise_health_conditions_content_prompt = [
                    (
                        "system",
                        """ You are part of an article re-writing process. Your task is to sort the given keypoints into the following structure:

                                ### Overview

                                ### Causes and Risk Factors

                                ### Symptoms and Signs

                                ### Complications

                                ### Treatment and Prevention

                                ### When to see a doctor


                            Your final answer MUST include these sections with the relevant headers in this specific order.
                            Do not add, modify or remove any of the sections.

                            Each paragraph in the given content have to be sorted into an appropriate section.
                            ALL keypoints MUST be sorted and returned at the end.
                            Do NOT modify the keypoints, you only need to sort the keypoints into the most appropriate header.

                            Let's think step by step:

                            1. Sort the following keypoints:

                                "Main Keypoint: Influenza
                                Content: Influenza, or the flu, is a contagious respiratory illness caused by influenza viruses. It spreads mainly through droplets when an infected person coughs, sneezes, or talks. The virus can also spread by touching contaminated surfaces and then touching your face. The flu is most contagious in the first few days of illness. High-risk groups, like the elderly and young children, should get vaccinated yearly to reduce the risk of severe complications.

                                Main Keypoint: Influenza self-care
                                Content: Get plenty of rest to help your body recover from influenza. Stay hydrated by drinking water and clear fluids. Use over-the-counter meds like acetaminophen for fever and aches, but don't give aspirin to children. A humidifier or warm salt water gargle can soothe a sore throat. Seek medical help if you have trouble breathing, chest pain, high fever, or if symptoms worsen.
                                "

                            2. There are 2 keypoints the given text. We start by determining which section the first keypoint falls under and sort it accordingly. The information in the first keypoint is relevant to the final section "Causes and Risk Factors" and will be sorted in accordingly.

                                Your answer:
                                "### Overview

                                ### Causes and Risk Factors
                                Influenza, or the flu, is a contagious respiratory illness caused by influenza viruses. It spreads mainly through droplets when an infected person coughs, sneezes, or talks. The virus can also spread by touching contaminated surfaces and then touching your face. The flu is most contagious in the first few days of illness. High-risk groups, like the elderly and young children, should get vaccinated yearly to reduce the risk of severe complications.

                                ### Symptoms and Signs

                                ### Complications

                                ### Treatment and Prevention

                                ### When to see a doctor"

                            3. Next, we determine that the information in the second keypoint is relevant to "Treatment and Prevention" as self-care is related to treatment.

                                Your final answer:
                                "### Overview

                                ### Causes and Risk Factors
                                Influenza, or the flu, is a contagious respiratory illness caused by influenza viruses. It spreads mainly through droplets when an infected person coughs, sneezes, or talks. The virus can also spread by touching contaminated surfaces and then touching your face. The flu is most contagious in the first few days of illness. High-risk groups, like the elderly and young children, should get vaccinated yearly to reduce the risk of severe complications.

                                ### Symptoms and Signs

                                ### Complications

                                ### Treatment and Prevention
                                    Get plenty of rest to help your body recover from influenza. Stay hydrated by drinking water and clear fluids. Use over-the-counter meds like acetaminophen for fever and aches, but don't give aspirin to children. A humidifier or warm salt water gargle can soothe a sore throat. Seek medical help if you have trouble breathing, chest pain, high fever, or if symptoms worsen.

                                ### When to see a doctor"


                            4. Check through each step carefully with until you have sorted all the paragraphs into an appropriate section.
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
                return optimise_health_conditions_content_prompt
