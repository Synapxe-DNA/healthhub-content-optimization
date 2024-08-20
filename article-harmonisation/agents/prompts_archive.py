class Llama_archived_prompts:
    def return_researcher_prompt_ver(version):
        """This function returns the previous] version of the researcher prompt

        Version 1: This researcher prompt which does not preserve the original headers, instead it instructs the llm to sort the sentences into keypoints determined by itself.

        Args:
            version: an integer where the user will state the version to be retrieved

        Returns:
            researcher_prompt: The desired version of the researcher prompt
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

    def return_content_prompt_ver(version, topic):
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


class Azure_archived_prompts:
    def return_researcher_prompt_ver(version) -> list:
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
