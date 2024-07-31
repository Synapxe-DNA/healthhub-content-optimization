from pathlib import Path

import pyarrow.parquet as pq

from .paths import get_root_dir

ROOT_DIR = get_root_dir()
MERGED_DATA_DIRECTORY = f"{ROOT_DIR}/article-harmonisation/data/merged_data.parquet"

CONTENT_BODY = "extracted_content_body"
EXTRACTED_HEADERS = "extracted_headers"
ARTICLE_TITLE = "title"
KEY_PARQUET_INFO = [
    ARTICLE_TITLE,
    "article_category_names",
    EXTRACTED_HEADERS,
    CONTENT_BODY,
]
TO_REMOVE = ["", " "]

table = pq.read_table(MERGED_DATA_DIRECTORY)
EXTRACTED_ARTICLE_TITLES = list(table[ARTICLE_TITLE])


def concat_headers_to_content(articles: list):
    final_configured_articles = []
    # for loop iterating through each
    for article_title in EXTRACTED_ARTICLE_TITLES:
        if article_title.as_py() in articles:
            idx = EXTRACTED_ARTICLE_TITLES.index(article_title)
            article_headers = list(table[EXTRACTED_HEADERS][idx])
            article_content = str(table[CONTENT_BODY][idx])
            split_content = []

            # Stores strings where Keypoint: + header for easy checks afterwards
            header_store = []

            for header_details in article_headers:
                header = header_details[0].as_py()
                if not split_content:
                    split_content.extend(article_content.split(header))
                else:
                    last_content = split_content.pop()
                    split_content.extend(last_content.split(header))
                split_content[-1] = "Keypoint: " + header + "\n" + split_content[-1][1:]
                header_store.append("Keypoint: " + header)
            for new_content in split_content:
                # checking if there are empty strings in split_content
                if new_content in TO_REMOVE or new_content.strip() in header_store:
                    print("yep")
                    split_content.pop(split_content.index(new_content))
            final_configured_articles.append(split_content)

    return final_configured_articles


def print_checks(result, model):
    """Prints out the various key outputs in graph. Namely, it will help you check for
        1. Researcher LLM outputs -> keypoints: prints out the sentences in their respective categories, including sentences omitted by the llm
        2. Compiler LLM outputs -> compiled_keypoints: prints out the compiled keypoints
        3. Content optimisation LLM outputs -> optimised_content: prints out the optimised article content after optimisation by content and writing guideline LLM
        4. Title optimisation LLM outputs -> article_title: prints out the optimised title
        5. Meta description optimisation LLM outputs -> meta_desc: prints out the optimised meta description

    Args:
        result: a AddableValuesDict object containing the final outputs from the graph
        model: a string containing the name of the model
    """

    # determines the number of articles undergoing the harmonisation process
    num_of_articles = len(result["original_article_content"]["article_content"])

    Path(f"{ROOT_DIR}/article-harmonisation/docs/txt_outputs").mkdir(
        parents=True, exist_ok=True
    )
    f = open(
        f"{ROOT_DIR}/article-harmonisation/docs/txt_outputs/{model}_compiled_keypoints_check.txt",
        "w",
    )

    for content_index in range(num_of_articles):
        if content_index > 0:
            f.write(" \n ----------------- \n")
        f.write(f"Original Article {content_index+1} content \n")
        article = result["original_article_content"]["article_content"][content_index]
        for keypoint in article:
            f.write(keypoint + "\n")
    f.write(" \n -----------------")

    # printing each keypoint produced by researcher LLM
    print("\nRESEARCHER LLM CHECKS\n -----------------", file=f)
    for i in range(0, num_of_articles):
        print(f"These are the keypoints for article {i+1}\n".upper(), file=f)
        print(result["optimised_article_output"]["researcher_keypoints"][i], file=f)
        print(" \n -----------------", file=f)

    # printing compiled keypoints produced by compiler LLM

    if "compiled_keypoints" in result["optimised_article_output"].keys():
        print("COMPILER LLM CHECKS \n ----------------- ", file=f)
        print(str(result["optimised_article_output"]["compiled_keypoints"]), file=f)
        print(" \n -----------------", file=f)

    # checking for optimised content produced by content optimisation flow
    flags = {"optimised_content", "optimised_writing", "article_title", "meta_desc"}
    keys = result["optimised_article_output"].keys()
    print("CONTENT OPTIMISATION CHECKS\n ----------------- \n", file=f)
    for flag in flags:
        if flag in keys:
            print(f"These is the optimised {flag.upper()}", file=f)
            print(result["optimised_article_output"][flag], file=f)
            print(" \n ----------------- \n", file=f)
        else:
            print(f"{flag.upper()} has not been flagged for optimisation.", file=f)
            print(" \n ----------------- \n", file=f)
    f.close()
