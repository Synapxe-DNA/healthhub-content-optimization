from abc import ABC, abstractmethod

import tiktoken


def prompt_tool(model: str):
    """Returns a LLMPrompt object based on the string input

    Args:
        model: a String input stating the model used

    Returns:
        a LLMPrompt object for the respective model type

    Raises:
        ValueError: if the input model is not supported, yet
    """
    match model.lower():
        case "mistral":
            prompter = MistralPrompts()
            return prompter

        case "llama3":
            prompter = LlamaPrompts()
            return prompter

        case "internlm":
            prompter = InternLMPrompts()
            return prompter

        case _:
            raise ValueError(f"You entered {model}, which is not a support model type")


class LLMPrompt(ABC):
    """
    Abstract class for all LLM prompt classes.
    All models will have a prompt class, which must inherit from this class, hence they must all include the following methods.

    This class inherits from ABC class.
    """

    @abstractmethod
    def return_readability_evaluation_prompt(self) -> str:
        """
        Abstract method for returning a readability evaluation prompt.
        """
        pass

    @abstractmethod
    def return_structure_evaluation_prompt(self) -> str:
        """
        Abstract method for returning a content structure evaluation prompt.
        """
        pass

    @abstractmethod
    def return_title_evaluation_prompt(self) -> str:
        """
        Abstract method for returning a title evaluation prompt.
        """
        pass

    @abstractmethod
    def return_meta_desc_evaluation_prompt(self) -> str:
        """
        Abstract method for returning a meta description evaluation prompt.
        """
        pass

    @abstractmethod
    def return_researcher_prompt(self) -> str:
        """
        Abstract method for returning a researcher prompt
        """
        pass

    @abstractmethod
    def return_compiler_prompt(self) -> str:
        """
        Abstract method for returning a compiler prompt
        """
        pass

    @abstractmethod
    def return_content_prompt(self) -> str:
        """
        Abstract method for returning a content optimisation prompt
        """
        pass

    @abstractmethod
    def return_writing_prompt(self) -> str:
        """
        Abstract method for returning a writing optimisation prompt
        """
        pass


class LlamaPrompts(LLMPrompt):
    """
    This class contains methods that stores and returns the prompts for Llama3 models.

    This class inherits from the LLMPrompt class

    Refer to https://llama.meta.com/docs/model-cards-and-prompt-formats/meta-llama-3/ for more information.
    """

    def return_readability_evaluation_prompt(self):

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

    def return_structure_evaluation_prompt(self):

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

    def return_title_evaluation_prompt(self):

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
            -   Highlight any discrepancies or misalignments between the title and the content.
            
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

    def return_meta_desc_evaluation_prompt(self):

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
        -   Highlight any discrepancies or misalignments between the meta description and the content.
        
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

    def return_researcher_prompt(self):
        """
        Returns the researcher prompt for Llama3

        Returns:
            researcher_prompt (string): this is a string containing the prompt for a researcher llm. {Article} is the only input required to invoke the prompt.
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
            You do NOT need to categorise all sentences. If a sentence is irrelevant to all keypoints, you can place it under the last keypoint "Omitted sentences"
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
            {Article}
            <|eot_id|>

            <|start_header_id|>assistant<|end_header_id|>
            Answer:
        """

        return researcher_prompt

    def return_compiler_prompt(self) -> str:
        """
        Returns the compiler prompt for Llama3

        Returns:
            compiler_prompt (string): this is a string containing the prompt for a compiler llm. {Keypoints} is the only input required to invoke the prompt.
        """

        compiler_prompt = """
            <|begin_of_text|><|start_header_id|>system<|end_header_id|>
            You are part of a article combination process. Your task is to compare and compile the keypoints given to you.

            Do NOT paraphrase from the sentences in each keypoint.
            You may add conjuctions and connectors if it improves the flow of the sentences.
            If two keypoints are identical or very similar, combine the points underneath and remove redundant sentences if required. However, do NOT paraphrase and strictly only add or remove sentences.
            All keypoints must be returned at the end.
            Return the compiled keypoints at the end.

            Use the following example to form your article:

            "
            Article 1 keypoints:
            1. Introduction to Parkinson's disease
            Parkinson's disease is a neuro-degenerative disease

            2. Remedies to Parkinson's disease
            You may take Levodopa prescribed by your doctor to alleviate the symptoms

            Article 2 keypoints:
            1. History of Parkinson's disease
            Parkinson's disease was discovered by James Parkinson in 1817. It is a neurodegenerative disease.

            2. Symptoms of Parkinson's disease
            Symptoms of PD include: Barely noticeable tremours in the hands, soft or slurred speech and little to no facial expressions.

            Answer:
            1. Introduction to Parkinson's disease
            Parkinson's disease is a neuro-degenerative disease. Parkinson's disease was discovered by James Parkinson in 1817.

            2. Symptoms to Parkinson's disease
            Symptoms of PD include: Barely noticeable tremours in the hands, soft or slurred speech and little to no facial expressions.

            3. Remedies to Parkinson's disease
            You may take Levodopa prescribed by your doctor to alleviate the symptoms
            "
            <|eot_id|>
            <|start_header_id|>user<|end_header_id|>
            Keypoints: 
            {Keypoints}
            <|eot_id|>

            <|start_header_id|>assistant<|end_header_id|>
            Answer:
        """
        return compiler_prompt
    
    def return_content_prompt(self) -> str:
        optimise_health_conditions_content_prompt = """
            <|begin_of_text|><|start_header_id|>system<|end_header_id|>
            You are part of a article re-writing process. The article content is aimed to educate readers about a particular health condition or disease.
            
            Your task is to compare the given keypoints with the given requirements below and write your own content to fill in missing sections if necessary.  
            You will also be given a set of instructions that you MUST follow.

            ### Start of content requirements
            When rewriting the content, your writing MUST meet the requirements stated here. 
            If the keypoints do not contain information for missing sections, you may write your own content based on the header. Your writing MUST be relevant to the header.
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
                You should also avoid lengthy, wordy bullet points.
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
            You must use the given keypoints to FILL IN the required sections. 
            Each sentence should start in a new line, only sentences in bullet points are exempted.
            You should only use bullet points only if it improves the readability of the content.
            You should only use bullet points SPARINGLY and only <= 2 sections in your writing should contain bullet points.
            Do NOT include any of the prompt instructions inside your response. The reader must NOT know what is inside the prompts
            ### End of instructions

            <|eot_id|>
            <|start_header_id|>user<|end_header_id|>
            Keypoints: 
            {Keypoints}
            <|eot_id|>
            <|start_header_id|>assistant<|end_header_id|>
            Answer:
            """
        return optimise_health_conditions_content_prompt
    
    def return_writing_prompt(self) -> str:
        optimise_health_conditions_writing_prompt = """
            <|begin_of_text|><|start_header_id|>system<|end_header_id|>
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

            <|eot_id|>
            <|start_header_id|>user<|end_header_id|>
            Content:
            {Content}
            <|eot_id|>
            <|start_header_id|>assistant<|end_header_id|>
            Answer:
            """
        return optimise_health_conditions_writing_prompt
    

class MistralPrompts(LLMPrompt):
    """
    This class contains methods that stores and returns the prompts for Mistral models.

    This class inherits from the LLMPrompt class

    Refer to https://community.aws/content/2dFNOnLVQRhyrOrMsloofnW0ckZ/how-to-prompt-mistral-ai-models-and-why?lang=en for more information.
    """

    def return_researcher_prompt(self):
        """
        Returns the researcher prompt for Mistral 7b

        Returns:
            researcher_prompt: this is a string containing the prompt for a researcher llm. {Article} is the only input required to invoke the prompt.
        """

        researcher_prompt = """
            <s> [INST]
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

            Ommitted sentences
            Buy these essential oils!
            "

            Article: {Article}
            [/INST]

            Answer:
            </s>
        """

        return researcher_prompt

    def return_compiler_prompt(self):
        """
        Returns the compiler prompt for Mistral 7b

        Returns:
            compiler_prompt: this is a string containing the prompt for a compiler llm. {Keypoints} is the only input required to invoke the prompt.
        """

        compiler_prompt = """
            <s> [INST]
            You are part of a article combination process. Your task is to compile the keypoints given to you.

            There are multiple articles with their respective keypoints that you must compile.
            You MUST compile ALL keypoints from ALL articles given.
            Do NOT paraphrase from the sentences in each keypoint.
            If two keypoints are identical or very similar, combine the points underneath and remove redundant sentences if required. However, do NOT paraphrase and strictly only add or remove sentences.
            Return the compilation of keypoints at the end.
            Do NOT return the compiled keypoints in bullet points.
            Do NOT include keypoints under omitted sentences in your compilation.

            Use the following example to form your compilation:

            "
            Article 1 keypoints:
            1. Introduction to Parkinson's disease
            Parkinson's disease is a neuro-degenerative disease

            2. Remedies to Parkinson's disease
            You may take Levodopa prescribed by your doctor to alleviate the symptoms

            Article 2 keypoints:
            1. History of Parkinson's disease
            Parkinson's disease was discovered by James Parkinson in 1817. It is a neurodegenerative disease.

            2. Symptoms of Parkinson's disease
            Symptoms of PD include: Barely noticeable tremours in the hands, soft or slurred speech and little to no facial expressions.

            Answer:
            1. Introduction to Parkinson's disease
            Parkinson's disease is a neuro-degenerative disease. Parkinson's disease was discovered by James Parkinson in 1817.

            2. Symptoms to Parkinson's disease
            Symptoms of PD include: Barely noticeable tremours in the hands, soft or slurred speech and little to no facial expressions.

            3. Remedies to Parkinson's disease
            You may take Levodopa prescribed by your doctor to alleviate the symptoms
            "

            Below are the keypoints you will need to compile:

            {Keypoints}
            [/INST]

            Answer:
            </s>
        """
        return compiler_prompt


class InternLMPrompts(LLMPrompt):
    """
    This class contains methods that stores and returns the prompts for InternLM models.

    This class inherits from the LLMPrompt class

    Refer to https://github.com/InternLM/InternLM/blob/main/chat/chat_format.md for more information.
    """

    def return_researcher_prompt(self):
        """
        Returns the researcher prompt for Mistral 7b

        Returns:
            researcher_prompt: this is a string containing the prompt for a researcher llm. {Article} is the only input required to invoke the prompt.
        """
        researcher_prompt = """
            <|im_start|>system
            You are part of a article combination process. Your task is to compile the keypoints given to you.

            There are multiple articles with their respective keypoints that you must compile.
            You MUST compile ALL keypoints from ALL articles given.
            Do NOT paraphrase from the sentences in each keypoint.
            If two keypoints are identical or very similar, combine the points underneath and remove redundant sentences if required. However, do NOT paraphrase and strictly only add or remove sentences.
            Return the compilation of keypoints at the end.
            Do NOT return the compiled keypoints in bullet points.
            Do NOT include keypoints under omitted sentences in your compilation.

            Use the following example to form your compilation:

            "
            Article 1 keypoints:
            1. Introduction to Parkinson's disease
            Parkinson's disease is a neuro-degenerative disease

            2. Remedies to Parkinson's disease
            You may take Levodopa prescribed by your doctor to alleviate the symptoms

            Article 2 keypoints:
            1. History of Parkinson's disease
            Parkinson's disease was discovered by James Parkinson in 1817. It is a neurodegenerative disease.

            2. Symptoms of Parkinson's disease
            Symptoms of PD include: Barely noticeable tremours in the hands, soft or slurred speech and little to no facial expressions.

            Answer:
            1. Introduction to Parkinson's disease
            Parkinson's disease is a neuro-degenerative disease. Parkinson's disease was discovered by James Parkinson in 1817.

            2. Symptoms to Parkinson's disease
            Symptoms of PD include: Barely noticeable tremours in the hands, soft or slurred speech and little to no facial expressions.

            3. Remedies to Parkinson's disease
            You may take Levodopa prescribed by your doctor to alleviate the symptoms
            "
            <|im_end|>
            <|im_start|>user
            Below are the keypoints you will need to compile: {Keypoints}
            <|im_end|>
            <|im_start|>assistant
            Answer:
        """
        return researcher_prompt

    def return_compiler_prompt(self):
        """
        Returns the compiler prompt for Mistral 7b

        Returns:
            compiler_prompt: this is a string containing the prompt for a compiler llm. {Keypoints} is the only input required to invoke the prompt.
        """
        compiler_prompt = """
        <|im_start|>system
            You are part of a article combination process. Your task is to compile the keypoints given to you.

            There are multiple articles with their respective keypoints that you must compile.
            You MUST compile ALL keypoints from ALL articles given.
            Do NOT paraphrase from the sentences in each keypoint.
            If two keypoints are identical or very similar, combine the points underneath and remove redundant sentences if required. However, do NOT paraphrase and strictly only add or remove sentences.
            Return the compilation of keypoints at the end.
            Do NOT return the compiled keypoints in bullet points.
            Do NOT include keypoints under omitted sentences in your compilation.

            Use the following example to form your compilation:

            "
            Article 1 keypoints:
            1. Introduction to Parkinson's disease
            Parkinson's disease is a neuro-degenerative disease

            2. Remedies to Parkinson's disease
            You may take Levodopa prescribed by your doctor to alleviate the symptoms

            Article 2 keypoints:
            1. History of Parkinson's disease
            Parkinson's disease was discovered by James Parkinson in 1817. It is a neurodegenerative disease.

            2. Symptoms of Parkinson's disease
            Symptoms of PD include: Barely noticeable tremours in the hands, soft or slurred speech and little to no facial expressions.

            Answer:
            1. Introduction to Parkinson's disease
            Parkinson's disease is a neuro-degenerative disease. Parkinson's disease was discovered by James Parkinson in 1817.

            2. Symptoms to Parkinson's disease
            Symptoms of PD include: Barely noticeable tremours in the hands, soft or slurred speech and little to no facial expressions.

            3. Remedies to Parkinson's disease
            You may take Levodopa prescribed by your doctor to alleviate the symptoms
            "
            <|im_end|>
            <|im_start|>user
            Below are the keypoints you will need to compile: {Keypoints}
            <|im_end|>
            <|im_start|>assistant
            Answer:
        """
        return compiler_prompt


def num_tokens_from_string(string: str, encoding_name: str = "cl100k_base") -> int:
    """Return the number of tokens in a string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


if __name__ == "__main__":
    prompter = prompt_tool("mistral")
    prompt = prompter.return_researcher_prompt()
    print(num_tokens_from_string(prompt))
