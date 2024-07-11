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
    if model == "Mistral":
        prompter = MistralLLMPrompts()
        return prompter
    elif model == "Llama3":
        prompter = LlamaLLMPrompts()
        return prompter
    else:
        raise ValueError(f"You entered {model}, which is not a support model type")

class LLMPrompt(ABC):
    """Abstract class for all LLM prompt classes. All models will have a prompt class, which must inherit from this class, hence they must all include the following methods.

    This class inherits from ABC class.
    """
    @abstractmethod
    def return_researcher_prompt(self):
        """ 
        Abstract method for returning a researcher prompt
        """
        pass

    @abstractmethod
    def return_compiler_prompt(self):
        """ 
        Abstract method for returning a compiler prompt
        """
        pass

class LlamaLLMPrompts(LLMPrompt):
    """ This class contains methods that stores and returns the prompts for Llama3 models.

    This class inherits from the LLMPrompt class
    """
    def return_researcher_prompt(self):
        """ returns the researcher prompt for Llama3
        Args: 
            
        Returns:
            researcher_prompt: this is a string containing the prompt for a researcher llm. {Article} is the only input required to invoke the prompt.
        """

        researcher_prompt = """
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

                Answer:
                """
        return researcher_prompt
    
    def return_compiler_prompt(self):
        """ returns the compiler prompt for Llama3
        Args: 
            
        Returns:
            compiler_prompt: this is a string containing the prompt for a compiler llm. {Keypoints} is the only input required to invoke the prompt.
        """

        compiler_prompt = """
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

                {Keypoints}

                Answer:
                """
        return compiler_prompt
        
class MistralLLMPrompts(LLMPrompt):
    def return_researcher_prompt(self):
        """ returns the researcher prompt for Mistral 7b
        Args: 
            
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
        """ returns the compiler prompt for Mistral 7b
        Args: 
            
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
    