import math
import re
import string
from functools import reduce
from typing import Any
import textdescriptives as td
from readability import Readability


def calculate_readability(text: str, choice: str = "hemmingway") -> Any:
    """
    Calculates the readability score of a given text.

    Args:
        text (str): The text to analyze.
        choice (str, optional): Select the metric to calculate. Defaults to "hemmingway".

    Returns:
          Any: Returns the readability metric

    Raises:
        ValueError: If the choice given is not supported
    """

    match choice.lower():
        case "py-readability":
            metrics = Readability(text)

            print(metrics.flesch_kincaid())
            print(metrics.coleman_liau())
            print(metrics.dale_chall())
            print(metrics.ari())
            print(metrics.linsear_write())
            print(metrics.gunning_fog())
            print(metrics.flesch())
            print(metrics.smog(all_sentences=True))
            print(metrics.spache())

        case "textdescriptives":
            print(td.get_valid_metrics())
            metrics = td.extract_metrics(text, lang="en", metrics=None)

        case "hemmingway":
            metrics = hemmingway_score(text)

        case _:
            raise ValueError(f"{choice} not supported")

    return metrics


def hemmingway_score(text: str) -> tuple[int, str]:
    """
    Calculates the hemmingway score of the given text.

    Args:
        text (str): The text to be scored.

    Returns:
        tuple(int, str): Returns a tuple containing the hemmingway score and difficulty of the text
    """
    sentences = []
    words = []

    # Compile regex to detect punctuations
    regex = re.compile("[%s]" % re.escape(string.punctuation))

    # Remove all hyperlinks
    filtered_text = re.sub(r"https?:\/\/[^\s]+", "", text)

    # Split the extracted text by the newline delimiter
    lines = filtered_text.split("\n")
    # Track the sentences in the text
    for line in lines:
        partial_sentences = re.split(r"[.!?]", line)
        for sentence in partial_sentences:
            sentences.append(sentence.strip())

    # Track the words in the text
    for sentence in sentences:
        sentence_words = sentence.split(" ")
        for word in sentence_words:
            word = regex.sub("", word.strip())
            words.append(word)

    # Filter for empty strings
    filtered_sentences = list(filter(lambda x: len(x) > 0, sentences))
    filtered_words = list(filter(lambda x: len(x) > 0, words))

    # Count the number of sentences, words and letters
    num_sentences = len(filtered_sentences)
    num_words = len(filtered_words)
    num_letters = reduce(lambda x, y: x + y, map(len, words))

    # Calculate the Hemmingway Score
    score = math.ceil(
        4.71 * (num_letters / num_words) + 0.5 * (num_words / num_sentences) - 21.43
    )

    # Get the reading level of the text based on the calculated score
    if score < 10:
        level = "normal"
    elif 10 <= score < 14:
        level = "hard"
    else:
        level = "very hard"

    return score, level


if __name__ == "__main__":
    text = """
    Myth 1: E-cigarettes are Harmless
    E-cigarettes (also known as vapourisers) are battery-operated devices that release nicotine by heating up e-liquids in a cartridge and turning them into vapour, which users then inhale. The main difference between e-cigarettes and regular cigarettes is the absence of tobacco leaves.
    E-cigarette makers have touted them as the healthier alternative to regular cigarettes but the World Health Organisation has declared that e-cigarettes are undoubtedly harmful to health and that they are not safer alternatives to regular cigarettes. In addition, there is evidence that vaporisers can be a gateway for non-smokers to start using traditional cigarettes. [1].

    Myth 2: Low-yield Cigarettes are Safer
    Some of us think smoking low-yield cigarettes ("lights") are safer than regular cigarettes because they have enhancements such as filters claimed to trap tar, or ventilation holes in the filter tip that promises to dilute smoke with air, or simply promise lower nicotine content.
    However, given that smokers crave nicotine, they may inhale more deeply when smoking low-yield cigarettes, or block the filter vents with their hands or lips. The actual levels of tar, nicotine and other harmful chemicals may be the same as, or possibly more than normal-yield cigarettes.
    Studies show that low yield cigarettes have little to no benefits in reducing the risk of smoking related diseases [2].

    Myth 3: Roll-your-own Cigarettes are Safer
    Smokers may choose to roll their own cigarettes (sometimes called ang hoon) as a cheaper alternative to buying regular cigarettes.
    Since many of the harmful chemicals found in regular cigarettes are also found in the loose tobacco used for roll-your-own cigarettes, smokers of ang hoon face the same risks of smoking-related diseases.

    Myth 4: Shisha (Waterpipe) Smoking is Harmless
    A shisha is a waterpipe, inside which flavoured tobacco is partially burned. The smoke passes through water held in the waterpipe before being inhaled by smokers through tubes attached to the pipe. Shisha is seen as a popular social activity, especially among youths. The import, distribution and sale of shisha tobacco is prohibited by law in Singapore.
    Shisha smoking is dangerous and studies have shown that the shisha smoke contains the same harmful components found in cigarette smoke, such as nicotine, tar and heavy metals. Also, the water in the shisha pipe does not absorb harmful substances in the smoke.
    Because shisha users tend to take more and deeper puffs from the waterpipe, users may absorb more toxic substances in a single shisha session compared to a single cigarette. In fact, during a 1-hour shisha session, users will inhale 100 to 200 times the amount of smoke, up to 9 times the carbon monoxide and 1.7 times the nicotine produced by a single cigarette [3].

    Myth 5: Oral Tobacco is Safer since it's not Smoked
    Oral smokeless tobacco is chewed or sucked in the mouth. These include chewing tobacco leaves and finely ground powdered tobacco (also known as "snuff"). Chewing tobacco is prohibited by law in Singapore.
    Smokeless tobacco is not a safe substitute for cigarette smoking. Oral tobacco is a major form of tobacco addiction and is linked to serious health risks such as cancer of the mouth, throat, oesophagus, and pancreas [4].

    Not A Myth: Tobacco in Any Form Hurts our Health
    Consumption of tobacco, in any form, increases your risks of contracting serious health problems like diabetes and cancer. The best way to keep you safe from the harmful effects of tobacco is to stay away entirely.

    Resources for Quitting
    Join the I Quit Programme
    and remain smoke free for 28 days and you are 5 times more likely to quit smoking. You can nominate your loved ones as a supporter when you sign up for the programme. Validate your smoke-free status and redeem a HPB eVoucher* worth $50 at the 28th day milestone. Keep going and you'll also receive eVouchers* worth $30 and $20 at the 3rd month and 6th month milestone respectively!
    *Terms and conditions apply. Return to Diabetes Hub
    """

    print(calculate_readability(text, choice="hemmingway"))
