from abc import ABC, abstractmethod


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


class LlamaPrompts(LLMPrompt):
    """
    This class contains methods that stores and returns the prompts for Llama3 models.

    This class inherits from the LLMPrompt class

    Refer to https://llama.meta.com/docs/model-cards-and-prompt-formats/meta-llama-3/ for more information.
    """

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
            Read these next: Top 10 power foods to eat recommended by a nutrionist

            Answer:
            Keypoint: Introduction to Parkinson's disease
            Consume a high protein, low carb diet. Exercise for 30 minutes daily. Cut down on consumption of saturated fat and sugary food.

            Omitted sentences:
            Read these next: Top 10 power foods to eat recommended by a nutrionist
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

            Keypoints: {Keypoints}
            <|eot_id|>

            <|start_header_id|>assistant<|end_header_id|>
            Answer:
        """
        return compiler_prompt
    
    def return_content_prompt(self) -> str:
        optimise_health_conditions_content_prompt = """
            <|begin_of_text|><|start_header_id|>system<|end_header_id|>
            You are part of a article re-writing process. The article content is aimed to educate readers about a particular health condition or disease.
            
            Your task is to compare the given keypoints with the requirements below and write your own content to fill in missing sections if necessary.  

            Your final answer must include these sections: Overview of the condition, Causes and Risk Factors, Symptoms and Signs, Complications, Treatment and Prevention, When to see a doctor
            
            You must use the given keypoints to FILL IN these sections. 
            If the keypoints do not contain information for missing sections, you may write your own content based on the header. Your writing MUST be relevant to the header.
            Please put "[A]" at the end of each sentence written by you.
            Do not have more than 2 sections with bullet points.
            You should avoid conveying negative sentiments, communicating in a firm but sensitive way, focusing on the positives of a certain medication instead of the potential risks.
            You should reassure readers when a situation is not a lost cause.
            Your answer for each section should be sufficiently elaborate. 

            Use the following example on Influenza to structure your answer. Your answer should contain more content and further elaboration on each points. 
            Your answer must maintain the same structure given in the example.

            ### Start of example
            1. What it is
            Influenza is a contagious viral disease that can affect anyone. It spreads when a person coughs, sneezes or speaks. The virus is airborne and infect people when they breathe it in.

            2. Causes and Risk Factors
            Influenza is caused by the flu virus, which is responsible for seasonal outbreaks and epidemics.

            3. Symptoms and signs
            Some symtpoms include: High fever, cough, headache, muscle aches. Other symptoms include sneezing, nasal discharge, loss of appetite.

            4. Complications of influenza
            The following people are at greater risk of influenza-related complications. 
            - Persons aged 65 years old and above. 
            - Children aged between 6 months old to 5 years old. 
            - Persons with chronic disorders of their lungs.
            - Women in the second or third trimester of pregnancy. [A]

            5. Treatment and Prevention 
            Here are some ways to battle influenza and to avoid it.
            Treatment: You can visit the local pharmacist to procure some flu medicine. 
            Prevention: Avoid crowded areas and wear a mask to reduce the risk of transmission.
            Treatment: Rest at home while avoiding strenuous activites until your symptoms subside.

            6. When to see a doctor
            You should visit your local doctor your symptoms persists for more than 3 days, or when you see fit. [A]
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
    
    def return_writing_prompt(self) -> str:
        optimise_writing_prompt = """
                                """
        return optimise_writing_prompt
    

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
