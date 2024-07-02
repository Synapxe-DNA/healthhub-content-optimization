class LLMPrompts:
    def __init__(self) -> None:
        pass

    def return_researcher_prompt(self):
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