import numpy as np
import pandas as pd
from agents.enums import ROLES
from agents.models import start_llm
from config import settings
from harmonisation import build_graph
from utils.excel_extractor import return_optimisation_flags, store_optimised_outputs
from utils.formatters import concat_headers_to_content
from utils.graphs import execute_graph

# Declaring model to use
MODEL = settings.MODEL_NAME

# File path to user annotation Excel file
USER_ANNOTATION_FILE = "Stage 1 user annotation for HPB_sample.xlsx"
USER_ANNOTATION = f"article-harmonisation/data/article_rewriting/{USER_ANNOTATION_FILE}"

USER_ANNOTATION_OUTPUT = "Stage 2 user annotation for HPB.xlsx"
USER_ANNOTATION_OUTPUT_PATH = f"article-harmonisation/data/article_rewriting/{USER_ANNOTATION_OUTPUT}"

# Declaring the respective sheet names for optimisation and harmonisation
OPTIMISATION_SHEET_OUTPUT = "User Annotation (Optimised)"
HARMONISATION_SHEET_OUTPUT = "User Annotation (Harmonised)"
OPTIMISATION_SHEET_INPUT = "User Annotation (to optimise)"
HARMONISATION_SHEET_INPUT = "User Annotation (to combine)"


def optimise_articles(app):
    """Runs the article optimisation flow.

    Details of the articles are extracted from the merged_data.parquet file obtained from the kedro pipeline and from the User Annotation Excel File.

    Optimised outputs are stored in the User Annotation Excel File

    Args:
        - app: GraphState object of the optimisation graph
    """
    # Opening the excel contents
    optimization_check = pd.ExcelFile(USER_ANNOTATION)

    # Setting df to the User Annotation sheets for article optimisation
    # df = optimization_check.parse('User Annotation (to optimise)')
    df = optimization_check.parse(OPTIMISATION_SHEET_INPUT)

    # Removing all articles not requiring any type of optimisation. This includes all empty fields and "No action".
    df = df[
        (df["Action"] != "No action") & (~df["Action"].apply(isinstance, args=(float,)))
    ]

    print("Num of articles to optimise: ", len(df))
    num_of_articles_in_df = len(df)

    for article_idx in range(num_of_articles_in_df):
        # Extracting article contents
        article = df.iloc[article_idx]

        # Extracting article title for original_article_inputs
        article_id = [
            article["article_id"]
        ]  # Note that article_id needs to be in a list
        article_title = [
            article["title"]
        ]  # Note that article_title needs to be in a list
        article_content = concat_headers_to_content(article_id)
        article_url = article["url"]
        article_content_category = article["content category"]
        article_category_names = article["article category names"]
        article_page_views = article["page views"]
        article_additional_input = article[
            "Optional: additional content to add for optimisation"
        ]

        # Extracting all reasons
        reasons_for_irrelevant_title = article["reason for irrelevant title"]
        reasons_for_irrelevant_meta_desc = article[
            "reason for irrelevant meta description"
        ]
        reasons_for_poor_readability = article["reason for poor readability"]
        
        # Extracting title flags from User Annotation Excel File
        overall_title_flag = article["overall title flags"]
        long_title = article["long title"]
        irrelevant_title = article["irrelevant title"]

        # Extracting meta desc flags from User Annotation Excel File
        overall_meta_desc_flag = article["overall meta description flags"]
        meta_desc_length = article["meta description not within 70 and 160 characters"]
        irrelevant_meta_desc = article["irrelevant meta description"]

        # Extracting content flags from User Annotation Excel File
        overall_content_flag = article["overall content flags"]
        poor_readability = article["poor readability"]
        insufficient_content = article["insufficient content"]

        article_flags = return_optimisation_flags(article, "optimisation")

        # Dictionary with the various input keys and items
        inputs = {
            "article_rewriting_tries": 0,
            "original_article_inputs": {
                "article_id": article_id,
                "article_content": article_content,
                "article_title": article_title,
                "article_url": article_url,
                "content_category": article_content_category,
                "article_category_names": article_category_names,
                "page_views": article_page_views,
                "additional_input": article_additional_input,
            },
            "article_evaluation": {
                "reasons_for_irrelevant_title": reasons_for_irrelevant_title,
                "reasons_for_irrelevant_meta_desc": reasons_for_irrelevant_meta_desc,
                "reasons_for_poor_readability": reasons_for_poor_readability,
            },
            "optimised_article_output": {
                "researcher_keypoints": [],
            },
            "user_flags": return_optimisation_flags(article, "optimisation"),
            "llm_agents": {
                "researcher_agent": researcher_agent,
                "compiler_agent": compiler_agent,
                "content_optimisation_agent": content_optimisation_agent,
                "writing_optimisation_agent": writing_optimisation_agent,
                "title_optimisation_agent": title_optimisation_agent,
                "meta_desc_optimisation_agent": meta_desc_optimisation_agent,
                "readability_optimisation_agent": readability_optimisation_agent,
                "personality_evaluation_agent": personality_evaluation_agent,
            },
        }

        # Running the article harmonisation process
        result = execute_graph(app, inputs)

        article_inputs = [
            article_id.pop(),  # article_id. article_id.pop() is used as openpyxl cannot handle list inputs
            article_url,  # url
            # Article title optimisation
            str(overall_title_flag),  # Overall title flag
            str(long_title), # long title
            str(irrelevant_title), # irrelevant title
            reasons_for_irrelevant_title,  # Reasons for irrelevant title from evaluation step
            (
                result["optimised_article_output"]["optimised_article_title"][0]
                if article_flags["flag_for_title_optimisation"]
                else None
            ),  # Optimised title 1
            (
                result["optimised_article_output"]["optimised_article_title"][1]
                if article_flags["flag_for_title_optimisation"]
                else None
            ),  # Optimised title 2
            (
                result["optimised_article_output"]["optimised_article_title"][2]
                if article_flags["flag_for_title_optimisation"]
                else None
            ),  # Optimised title 3
            None,  # Title chosen (user to choose 1 from: Title 1, Title 2, Title 3 or ‘Write your own’)
            None,  # Optional: Title written by user (free text for user to add only if ‘Write your own’ is chosen)
            # Article meta desc optimisation
            str(overall_meta_desc_flag),  # Overall meta desc flag
            str(meta_desc_length), # Meta desc length not within 70 and 160 characters
            str(irrelevant_meta_desc), # irrelevant meta description
            reasons_for_irrelevant_meta_desc,  # Reasons for irrelevant meta desc from evaluation step
            (
                result["optimised_article_output"]["optimised_meta_desc"][0]
                if article_flags["flag_for_meta_desc_optimisation"]
                else None
            ),  # Optimised meta desc 1
            (
                result["optimised_article_output"]["optimised_meta_desc"][1]
                if article_flags["flag_for_meta_desc_optimisation"]
                else None
            ),  # Optimised meta desc 2
            (
                result["optimised_article_output"]["optimised_meta_desc"][2]
                if article_flags["flag_for_meta_desc_optimisation"]
                else None
            ),  # Optimised meta desc 3
            None,  # Meta Description chosen (user to choose 1 from: Meta Description 1, Meta Description 2, Meta Description 3 or ‘Write your own’)
            None,  # Optional: meta description written by user (free text for user to add only if ‘Write your own’ is chosen)
            # Article writing optimisation
            str(overall_content_flag),  # Overall content flag
            str(poor_readability), # poor readability
            reasons_for_poor_readability, # reasons for poor readability
            str(insufficient_content), # insufficient content
            (
                result["optimised_article_output"]["optimised_writing"]
                if article_flags["flag_for_writing_optimisation"]
                else None
            ),  # Rewritten article content (should be a link)
            None,  # Article optimisation evaluation summary
            None,  # User approval of optimised article
            None,  # Optional: User attached updated article (Y)
            None # Content Edit Status (if any)
            # Note that reasons_for_poor_readability and reasons_for_improving_writing_style are not included as it complicates the llm prompt, leading to poorer performance.
        ]

        # Storing the optimised outputs into the User Annotation Excel File
        store_optimised_outputs(
            USER_ANNOTATION_OUTPUT_PATH, OPTIMISATION_SHEET_OUTPUT, article_inputs
        )


def harmonise_articles(app):
    """Runs the article harmonisation flow.

    Details of the articles are extracted from the merged_data.parquet file obtained from the kedro pipeline and from the User Annotation Excel File.

    Optimised outputs are stored in the User Annotation Excel File

    Args:
        - app: GraphState object of the harmonisation graph
    """
    # Opening the excel contents
    optimization_check = pd.ExcelFile(USER_ANNOTATION)

    # Setting df to the User Annotation sheets for article harmonisation
    # df = optimization_check.parse('User Annotation (to combine)')
    df = optimization_check.parse(HARMONISATION_SHEET_INPUT)

    # Removing all articles not flagged for combination
    df = df[df["Action"] == "Combine"]

    # Determining all unique group numbers
    group_numbers = df["group_number"].unique()

    # Determining the number of unique groups
    unique_group_num = len(group_numbers)
    print("Num of groups to harmonise: ", unique_group_num)

    # For loop iterating through each unique group flagged for harmonisation
    for group_num in group_numbers:
        # Defining articles of specific group
        grouped_articles_to_harmonise = df[df["group_number"] == group_num]

        # Determining if number of unique sub-groups
        sub_group_numbers = grouped_articles_to_harmonise["Subgroup"].unique()
        sub_group_numbers = sub_group_numbers[~np.isnan(sub_group_numbers)]
        print(f"Sub groups in group {group_num}: {sub_group_numbers}")

        # For loop iterating through each sub group in a specific group flagged for harmonisation
        for sub_group_num in sub_group_numbers:
            print(f"Harmonising subgroup {int(sub_group_num)}")
            # Extracting all rows in df in this subgroup
            subgrouped_articles = grouped_articles_to_harmonise[
                grouped_articles_to_harmonise["Subgroup"] == sub_group_num
            ]

            # Number of rows in subgroup
            num_of_articles_in_sub_grp = len(subgrouped_articles)

            # Extracting group contents for Excel
            article_group_number = group_num
            article_sub_group = sub_group_num
            article_group_description = subgrouped_articles.iloc[0]["group_description"]
            article_sub_group_ids = []
            article_sub_group_urls = []

            # Extracting additional group contents for the graph
            article_group_content_category = subgrouped_articles.iloc[0][
                "content category"
            ]
            article_group_category_names = subgrouped_articles.iloc[0][
                "article_category_names"
            ]
            article_sub_group_page_views = []
            article_sub_group_additional_inputs = ""
            article_sub_group_titles = []

            # For loop iterating through each article in the sub group
            for article_idx in range(num_of_articles_in_sub_grp):
                # Extracting article row
                article = subgrouped_articles.iloc[article_idx]

                # Extracting article details
                article_id = article["article_id"]
                article_url = article["url"]
                article_page_views = article["page_views"]
                main_article = article[
                    "Main Article Structure? (Y)"
                ]  # checks if the article is the main article for the sub group harmonisation. 

                # If additional input cell in the Excel sheet is empty, it returns nan, which is of float type. Hence, if it's a float type, we set it to "".
                if isinstance(
                    article["Optional: additional content to add for harmonisation"], float
                ):
                    article_additional_inputs = ""
                else:
                    article_additional_inputs = article[
                        "Optional: additional content to add for harmonisation"
                    ]
                article_title = article["title"]

                # Appending article id to article_sub_group_ids
                article_sub_group_ids.append(article_id)

                # Appending article url to article_sub_group_urls
                article_sub_group_urls.append(article_url)

                # Appending article page views to article_sub_group_page_views
                article_sub_group_page_views.append(article_page_views)

                # Appending article title to article_sub_group_titles
                article_sub_group_titles.append(article_title)

                # Concatenating additional inputs to article_sub_group_additional_inputs
                if article_sub_group_additional_inputs == "":
                    article_sub_group_additional_inputs += article_additional_inputs
                else:
                    article_sub_group_additional_inputs += (
                        f"\n\n{article_additional_inputs}"
                    )

                # If statement checking if the article is the main article for the sub group harmonisation
                if main_article == "Y" and article_group_content_category != "diseases-and-condition":
                    main_article_content = concat_headers_to_content([article_id]).pop()
                else:
                    main_article_content = ''

            inputs = {
                "article_rewriting_tries": 0,
                "original_article_inputs": {
                    "article_id": article_sub_group_ids,
                    "article_title": article_sub_group_titles,
                    "article_content": concat_headers_to_content(article_sub_group_ids),
                    "article_url": article_sub_group_urls,
                    "content_category": article_group_content_category,
                    "article_category_names": article_group_category_names,
                    "page_views": article_sub_group_page_views,
                    "additional_input": article_sub_group_additional_inputs,
                    "main_article_content": main_article_content,
                },
                "optimised_article_output": {
                    "researcher_keypoints": [],
                },
                "user_flags": return_optimisation_flags(article, "harmonisation"),
                "llm_agents": {
                    "researcher_agent": researcher_agent,
                    "compiler_agent": compiler_agent,
                    "content_optimisation_agent": content_optimisation_agent,
                    "writing_optimisation_agent": writing_optimisation_agent,
                    "title_optimisation_agent": title_optimisation_agent,
                    "meta_desc_optimisation_agent": meta_desc_optimisation_agent,
                    "readability_optimisation_agent": readability_optimisation_agent,
                    "personality_evaluation_agent": personality_evaluation_agent,
                },
            }

            # Running the article harmonisation process
            result = execute_graph(app, inputs)

            article_inputs = [
                article_group_number,  # Group Number
                article_sub_group,  # Subgroup
                str(article_sub_group_urls),  # urls
                article_group_description,  # Group Description
                str(article_sub_group_ids),  # Article ids
                # Article title optimisation
                result["optimised_article_output"]["optimised_article_title"][
                    0
                ],  # Title Option 1
                result["optimised_article_output"]["optimised_article_title"][
                    1
                ],  # Title Option 2
                result["optimised_article_output"]["optimised_article_title"][
                    2
                ],  # Title Option 3
                None,  # Title Chosen
                None,  # Optional: Title written by user
                # Article meta desc optimisation
                result["optimised_article_output"]["optimised_meta_desc"][
                    0
                ],  # Meta Description 1
                result["optimised_article_output"]["optimised_meta_desc"][
                    1
                ],  # Meta Description 2
                result["optimised_article_output"]["optimised_meta_desc"][
                    2
                ],  # Meta Description 3
                None,  # Meta Description Chosen
                None,  # Optional: Meta Description written by user
                # Article writing optimisation
                result["optimised_article_output"][
                    "optimised_writing"
                ],  # Optimised article content (should be a link)
                None,  # Article optimisation evaluation summary (could be nil)
                None,  # User approval of optimised article
                None,  # User attached updated article
                None,  # Content Edit Status (if any)
            ]

            # Storing the optimised outputs into the User Annotation Excel File
            store_optimised_outputs(
                USER_ANNOTATION_OUTPUT_PATH, HARMONISATION_SHEET_OUTPUT, article_inputs
            )


if __name__ == "__main__":
    # starting up the respective llm agents
    researcher_agent = start_llm(MODEL, ROLES.RESEARCHER)
    compiler_agent = start_llm(MODEL, ROLES.COMPILER)
    meta_desc_optimisation_agent = start_llm(MODEL, ROLES.META_DESC, temperature=0.1)
    title_optimisation_agent = start_llm(MODEL, ROLES.TITLE, temperature=0.5)
    content_optimisation_agent = start_llm(MODEL, ROLES.CONTENT_OPTIMISATION)
    writing_optimisation_agent = start_llm(
        MODEL, ROLES.WRITING_OPTIMISATION, temperature=0.6
    )
    personality_evaluation_agent = start_llm(MODEL, ROLES.PERSONALITY_EVALUATION)
    readability_optimisation_agent = start_llm(
        MODEL, ROLES.READABILITY_OPTIMISATION, temperature=0.5
    )

    # Obtaining the GraphState
    app = build_graph()

    # Running the appropriate process
    harmonise_articles(app)
    optimise_articles(app)