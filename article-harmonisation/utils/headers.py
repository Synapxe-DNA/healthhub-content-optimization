import os

import pyarrow.parquet as pq

ROOT = os.getcwd()
MERGED_DATA_DIRECTORY = f"{ROOT}/article-harmonisation/data/merged_data.parquet"

CONTENT_BODY = "extracted_content_body"
EXTRACTED_HEADERS = "extracted_headers"
KEY_PARQUET_INFO = ["title", "article_category_names", EXTRACTED_HEADERS, CONTENT_BODY]
TO_REMOVE = ["", " "]

table = pq.read_table(MERGED_DATA_DIRECTORY)
EXTRACTED_ARTICLE_CONTENT = list(table["extracted_content_body"])


def concat_headers_to_content(article_list):
    final_configured_articles = []
    # for loop iterating through each
    for content in EXTRACTED_ARTICLE_CONTENT:
        for article_content in article_list:
            if article_content in str(content):
                idx = EXTRACTED_ARTICLE_CONTENT.index(content)
                str_content = content.as_py()
                article_headers = list(table[EXTRACTED_HEADERS][idx])
                split_content = []
                for header_details in article_headers:
                    header = header_details[0].as_py()
                    if not split_content:
                        split_content.extend(str_content.split(header))
                    else:
                        last_content = split_content.pop()
                        split_content.extend(last_content.split(header))
                    split_content[-1] = (
                        "Keypoint: " + header + "\n" + split_content[-1][1:]
                    )
                for new_content in split_content:
                    if new_content in TO_REMOVE:
                        split_content.pop(split_content.index(new_content))
                final_configured_articles.append(split_content)

    return final_configured_articles
