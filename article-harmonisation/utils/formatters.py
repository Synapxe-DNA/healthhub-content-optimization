import re
from pathlib import Path

import pyarrow.parquet as pq

from .paths import get_root_dir

ROOT_DIR = get_root_dir()
MERGED_DATA_DIRECTORY = f"{ROOT_DIR}/article-harmonisation/data/merged_data.parquet"

CONTENT_BODY = "extracted_content_body"
EXTRACTED_HEADERS = "extracted_headers"
ARTICLE_TITLE = "title"
META_DESC = "category_description"
CONTENT_CATEGORY = "content_category"
SUBCATEGORIES = "article_category_names"
ARTICLE_ID = "id"
ARTICLE_URL = "full_url"

MERGED_DF = pq.read_table(MERGED_DATA_DIRECTORY)

# TODO: Clean up formatters.py to be more presentable and structured


def get_article_list_indexes(article_ids: list, setting: str = "ids") -> list:
    """
    Get indexes of articles in the MERGED_DF based on ids or filename.

    Args:
        article_ids (list): List of article ids to search for.
        setting (str, optional): Setting to determine search method.
            Can be "ids" or "filename". Defaults to "ids".

    Returns:
        list: List of indexes in MERGED_DF where the articles were found.

    Raises:
        ValueError: If setting is not "ids" or "filename".
    """
    article_list_idx = []
    if setting == "ids":
        # Extract article indexes based on "ids" column from MERGED_DF
        extracted_ids = list(MERGED_DF[ARTICLE_ID])
        for article_id in extracted_ids:
            if article_id.as_py() in article_ids:
                idx = extracted_ids.index(article_id)
                article_list_idx.append(idx)
    elif setting == "filename":
        # Extract article indexes based on "id" column from MERGED_DF
        # Note: The filename will contain the article ID which is delimited by the "_" symbol
        extracted_ids = list(MERGED_DF[ARTICLE_ID])
        for article in article_ids:
            # Extract article ID from filename
            article_id = int(article.split("/")[-1].split(".")[0].split("_")[-1])
            for row_id in extracted_ids:
                if row_id.as_py() == article_id:
                    idx = extracted_ids.index(row_id)
                    article_list_idx.append(idx)
    else:
        raise ValueError("Setting must be either 'title' or 'filename'")

    return article_list_idx


def get_article_titles(article_idxs: list) -> list[str]:
    """
    Retrieve article titles from MERGED_DF based on provided indexes.

    Args:
        article_idxs (list): List of indexes corresponding to articles in MERGED_DF.

    Returns:
        list: List of article titles as strings.
    """

    article_titles = []
    for idx in article_idxs:
        # Extract title from MERGED_DF and convert to string
        title = str(MERGED_DF[ARTICLE_TITLE][idx])
        article_titles.append(title)
    return article_titles


def extract_content_for_evaluation(
    articles: list, setting: str = "title"
) -> list[dict]:
    """
    Extract article content, title, meta descriptions, and category for given articles.

    Args:
        articles (list[dict]): List of article titles or filenames to extract content from.
        setting (str, optional): Setting to determine search method.
            Can be "title" or "filename". Defaults to "title".

    Returns:
        list: List of dictionaries, each containing details of an article:
            - ARTICLE_TITLE: The title of the article.
            - META_DESC: The meta description of the article.
            - CONTENT_BODY: The main content of the article.
            - CONTENT_CATEGORY: The category of the article.

    Note:
        This function relies on the MERGED_DF global variable and the get_article_list_indexes function.
    """
    article_details = []

    # Get indexes of articles in MERGED_DF
    article_list_idx = get_article_list_indexes(articles, setting)
    for idx in article_list_idx:
        # Extract article information from MERGED_DF
        article_content = str(MERGED_DF[CONTENT_BODY][idx])
        article_title = str(MERGED_DF[ARTICLE_TITLE][idx])
        meta_desc = str(MERGED_DF[META_DESC][idx])
        content_category = str(MERGED_DF[CONTENT_CATEGORY][idx])

        # Set default value if meta description is None
        meta_desc = meta_desc if meta_desc is not None else "No meta description"

        # Append article details to the list
        article_details.append(
            {
                ARTICLE_TITLE: article_title,
                META_DESC: meta_desc,
                CONTENT_BODY: article_content,
                CONTENT_CATEGORY: content_category,
            }
        )

    return article_details


def concat_headers_to_content(article_id: list) -> list[str]:
    """
    Concatenate headers to content for given articles.

    This function extracts headers and content from MERGED_DF, organizes them hierarchically, and creates a formatted
    string for each article.

    Args:
        articles (list): List of article titles to process.

    Returns:
        list[str]: List of formatted strings, each representing an article with its headers and content organized hierarchically.

    Note:
        This function relies on the MERGED_DF global variable and the get_article_list_indexes function.
    """
    final_configured_articles = []
    article_list_idx = get_article_list_indexes(article_id)
    for num in range(len(article_id)):
        idx = article_list_idx[num]
        article_headers = list(MERGED_DF[EXTRACTED_HEADERS][idx])
        article_content = str(MERGED_DF[CONTENT_BODY][idx])
        article_title = str(MERGED_DF[ARTICLE_TITLE][idx])

        # this list will store all the headers + content as elements
        split_content = []

        # Stores headers based on their heading type, h1 - h6
        header_dictionary = {}

        if len(article_headers) > 0:
            for header_details in article_headers:
                header_title = header_details[0].as_py()
                # Some header_titles are just empty strings, which cannot run .split(). This if statement checks if the header_title is an empty string first.
                if len(header_title.strip()) == 0:
                    header_type = header_details[1].as_py()

                    # checks if the specific header type exists as a key in header_dictionary
                    header_list = header_dictionary.get(header_type, [])

                    # adding the header to the respective item in header_dictionary
                    header_list.append(header_title)
                    header_dictionary[header_type] = header_list

                    # TODO: Explain what exactly is going on here. Otherwise, abstract it as a separate function for better clarity
                    match header_type:
                        case "h1":
                            header = f"h1 Main Header: {header_title}"
                        case "h2":
                            header = f"h2 Sub Header: {header_title}"
                            if "h1" in header_dictionary.keys():
                                header += f"\nSub Header to h1 Main Header: {header_dictionary['h1'][-1]}"
                        case "h3":
                            header = f"h3 Sub Section: {header_title}"
                            if "h2" in header_dictionary.keys():
                                header += f"\nSub Section to h2 Sub Header: {header_dictionary['h2'][-1]}"
                        case "h4":
                            header = f"h4 Sub Section: {header_title}"
                            if "h3" in header_dictionary.keys():
                                header += f"\nSub Section to h3 Sub Section: {header_dictionary['h3'][-1]}"
                        case "h5":
                            header = f"h5 Sub Section: {header_title}"
                            if "h4" in header_dictionary.keys():
                                header += f"\nSub Section to h4 Sub Section: {header_dictionary['h4'][-1]}"
                        case "h6":
                            header = f"h6 Sub Section: {header_title}"
                            if "h5" in header_dictionary.keys():
                                header += f"\nSub Section to h5 Sub Section: {header_dictionary['h5'][-1]}"

                    # Split content and add formatted header
                    if not split_content:
                        split_content.extend(article_content.split(header_title, 1))
                    else:
                        last_content = split_content.pop()
                        split_content.extend(last_content.split(header_title, 1))

                    split_content[-1] = header + "\n" + split_content[-1][1:]

        else:
            split_content.append(article_content)

        # concatenate all into this string. The title is used as the main header.
        final_labelled_article = f"Article Header: {article_title}\n"

        for new_content in split_content:
            # checking if there are empty strings in split_content and empty headers
            if len(new_content.strip()) > 0:
                final_labelled_article += new_content + "\n"

        final_configured_articles.append(final_labelled_article)

    return final_configured_articles


def extract_article_details(articles: list) -> tuple[list[int], list[str]]:
    """Extract article IDs and URLs for given articles.

    Args:
        articles (list): List of article titles to extract details for.

    Returns:
        tuple[list[int], list[str]]: A tuple containing two lists:
            - list[int]: List of article IDs.
            - list[str]: List of article URLs.

    Note:
        This function relies on the MERGED_DF global variable and the get_article_list_indexes function.
    """

    article_ids = []
    urls = []

    # Get indexes of articles in MERGED_DF
    article_indexes = get_article_list_indexes(articles)

    for idx in article_indexes:
        # Extract and append article ID
        article_ids.append(int(MERGED_DF[ARTICLE_ID][idx]))
        # Extract and append article URL
        urls.append(str(MERGED_DF[ARTICLE_URL][idx]))

    return article_ids, urls


def split_into_list(optimised_items: str, num_of_items: int):
    """This function takes an input where

    Args:
        optimised_items: String containing the optimised titles/meta desc. They should be in the order:
            1. Title 1 / Meta desc 1
            2. Title 2 / Meta desc 2
            3. Title 3 / Meta desc 3
        num_of_items: a int variable determining the number of titles/meta desc being generated by the llm.

    Returns:
        item_list: a list with each optimised title/meta desc as an individual item.
    """
    # item_list is used to store the split titles
    item_list = []

    for idx in range(1, num_of_items + 1):

        # if item_list is empty, it will split from optimised_items
        if not item_list:
            split_items = optimised_items.split(str(idx) + ".")
        else:
            # if item_list is not empty, it will take the last item in the list and split from there
            split_items = item_list.pop().split(str(idx) + ".")

        # adding the split items into item_list
        item_list.extend(split_items)

    # stores the indexes of the items due to be removed, such as empty strings
    idx_to_remove = []
    for item_idx in range(len(item_list)):
        item = item_list[item_idx]

        # checks if the item is an empty string
        if len(item.strip()) == 0:
            idx_to_remove.append(item_idx)

        # regex to remove ", \\n, \\ from each item
        title = re.sub(r'("|\\n|\\)', "", item)

        # stripping all leading and trailing white spaces
        title = title.strip()

        # replacing the old title with the newly processed title
        item_list[item_idx] = title

    # removing all items with their indexes flagged to be removed in idx_to_remove
    for idx in idx_to_remove:
        item_list.pop(idx)

    # returning the item_list with the processed titles
    return item_list


def print_checks(result: dict, model: str) -> None:
    """
    Prints and saves the key outputs from the harmonisation process for various stages of article optimization.

    This function generates a report containing the following information:
    1. Researcher LLM outputs: Prints out the sentences in their respective categories, including sentences omitted by the LLM.
    2. Compiler LLM outputs: Prints out the compiled keypoints.
    3. Content optimization LLM outputs: Prints out the optimized article content.
    4. Title optimization LLM outputs: Prints out the optimized title.
    5. Meta description optimization LLM outputs: Prints out the optimized meta description.

    The results are saved to a text file specific to the provided model.

    Args:
        result (dict): A dictionary containing the final outputs from the graph.
        model (str): The name of the model, used for naming the output file.

    Note:
        The function writes the output to a text file in the 'article-harmonisation/docs/txt_outputs' directory.
    """

    # Determine the number of articles undergoing the harmonisation process
    num_of_articles = len(result.get("original_article_inputs")["article_content"])

    # Create the directory for storing output text files if it doesn't exist
    Path(f"{ROOT_DIR}/article-harmonisation/docs/txt_outputs").mkdir(
        parents=True, exist_ok=True
    )

    # Open the file for writing the output
    with open(
        f"{ROOT_DIR}/article-harmonisation/docs/txt_outputs/{model}_compiled_keypoints_check.txt",
        "w",
    ) as f:

        # Iterate through each article content and write to the file
        for content_index in range(num_of_articles):
            if content_index > 0:
                f.write(" \n ----------------- \n")
            f.write(f"Original Article {content_index+1} content \n")
            article = result.get("original_article_inputs")["article_content"][
                content_index
            ]
            for keypoint in article:
                f.write(keypoint + "\n")
        f.write(" \n -----------------")

        # Printing each keypoint produced by Researcher LLM
        print("\nRESEARCHER LLM CHECKS\n -----------------", file=f)
        for i in range(0, num_of_articles):
            print(f"These are the keypoints for article {i+1}\n".upper(), file=f)
            print(
                result.get("optimised_article_output")["researcher_keypoints"][i],
                file=f,
            )
            print(" \n -----------------", file=f)

        # Printing compiled keypoints produced by Compiler LLM
        if "compiled_keypoints" in result["optimised_article_output"].keys():
            print("COMPILER LLM CHECKS \n ----------------- ", file=f)
            print(
                str(result.get("optimised_article_output")["compiled_keypoints"]),
                file=f,
            )
            print(" \n -----------------", file=f)

        # Checking for optimised content produced by the content optimisation flow
        flags = {"optimised_content", "optimised_writing", "article_title", "meta_desc"}
        keys = result.get("optimised_article_output").keys()
        print("CONTENT OPTIMISATION CHECKS\n ----------------- \n", file=f)
        for flag in flags:
            if flag in keys:
                print(f"These is the optimised {flag.upper()}", file=f)
                print(result.get("optimised_article_output")[flag], file=f)
                print(" \n ----------------- \n", file=f)
            else:
                print(f"{flag.upper()} has not been flagged for optimisation.", file=f)
                print(" \n ----------------- \n", file=f)


def parse_string_to_boolean(string_to_check: str) -> bool:
    """
    Converts a string representation of a boolean ("true" or "false") to its corresponding boolean value.

    This function takes a string as input and returns `True` if the string is "true" (case-insensitive),
    `False` if the string is "false" (case-insensitive), and `None` for any other input.

    Args:
        string_to_check (str): The string to be converted to a boolean.

    Returns:
        bool: The boolean value corresponding to the input string, or `None` if the input is not "true" or "false".
    """

    # Check if the input is a string
    if isinstance(string_to_check, str):
        # Convert the string to lowercase to handle case-insensitivity
        string_to_check = string_to_check.lower()

        # Return True if the string is "true"
        if string_to_check == "true":
            res = True
        # Return False if the string is "false"
        elif string_to_check == "false":
            res = False
        # Return None for any other string
        else:
            res = None
    # Return None if the input is not a string
    else:
        res = None

    return res


def format_checks_outputs(checks: dict) -> dict:
    """
    Formats the output of various content checks into a structured dictionary.

    This function processes the input dictionary `checks` containing results from multiple content checks (such as flags
    and decisions based on rule-based and LLM-based assessments) and formats these into a comprehensive output dictionary.

    Args:
        checks (dict): A dictionary containing the results from content checks, including article inputs, content flags,
            title flags, and meta description flags.

    Returns:
        dict: A formatted dictionary summarizing the content check results, including flags for content quality, title relevance,
            and meta description compliance.
    """

    result = {}

    # Extracting Article Inputs from the checks dictionary
    article_inputs = checks.get("article_inputs")
    article_id = int(article_inputs.get("article_id"))
    title = article_inputs.get("article_title")
    url = article_inputs.get("article_url")
    content_category = article_inputs.get("content_category")
    article_category_names = article_inputs.get("article_category_names")
    page_views = int(article_inputs.get("page_views"))

    # Extracting Content flags (Rule-based) from the checks dictionary
    content_flags = checks.get("content_flags")
    poor_readability = bool(content_flags.get("is_unreadable"))
    insufficient_content = bool(content_flags.get("low_word_count"))

    # Extracting Content flags (LLM-based) from the checks dictionary
    content_judge = checks.get("content_judge")
    # Readability explanation is dependent on poor_readability flag - it can be None
    readability_explanation = content_judge.get("readability", {}).get(
        "explanation", None
    )
    structure_decision = bool(content_judge.get("structure").get("decision"))
    structure_explanation = content_judge.get("structure").get("explanation", None)

    # Extracting Title flags (Rule-based) from the checks dictionary
    title_flags = checks.get("title_flags")
    long_title = bool(title_flags.get("long_title"))

    # Extracting Title flags (LLM-based) from the checks dictionary
    title_judge = checks.get("title_judge")
    irrelevant_title_decision = bool(title_judge.get("title").get("decision"))
    irrelevant_title_explanation = title_judge.get("title").get("explanation", None)

    # Extracting Meta description flags (Rule-based) from the checks dictionary
    meta_flags = checks.get("meta_flags")
    meta_not_within_char_count = bool(meta_flags.get("not_within_char_count"))

    # Extracting Meta description flags (LLM-based) from the checks dictionary
    meta_judge = checks.get("meta_judge")
    irrelevant_meta_desc_decision = bool(meta_judge.get("meta_desc").get("decision"))
    irrelevant_meta_desc_explanation = meta_judge.get("meta_desc").get(
        "explanation", None
    )

    # Populating the result dictionary with formatted data
    result["article_id"] = article_id
    result["title"] = title
    result["url"] = url
    result["content category"] = content_category
    result["article category names"] = article_category_names
    result["page views"] = page_views

    # Overall flags based on content, title, and meta description checks
    result["overall flags"] = (
        poor_readability
        | insufficient_content
        | structure_decision
        | long_title
        | irrelevant_title_decision
        | meta_not_within_char_count
        | irrelevant_meta_desc_decision
    )

    # Title-related flags and explanations
    result["overall title flags"] = long_title | irrelevant_title_decision
    result["long title"] = long_title
    result["irrelevant title"] = irrelevant_title_decision
    result["reason for irrelevant title"] = irrelevant_title_explanation

    # Meta description-related flags and explanations
    result["overall meta description flags"] = (
        meta_not_within_char_count | irrelevant_meta_desc_decision
    )
    result["meta description not within 70 and 160 characters"] = (
        meta_not_within_char_count
    )
    result["irrelevant meta description"] = irrelevant_meta_desc_decision
    result["reason for irrelevant meta description"] = irrelevant_meta_desc_explanation

    # Content-related flags and explanations
    result["overall content flags"] = (
        poor_readability | insufficient_content | structure_decision
    )
    result["poor readability"] = poor_readability
    result["reason for poor readability"] = readability_explanation
    result["insufficient content"] = insufficient_content
    result["writing style needs improvement"] = structure_decision
    result["reason for improving writing style"] = structure_explanation

    # Placeholder fields for further actions and additional content
    result["Action"] = ""
    result["Additional Content"] = ""

    return result
