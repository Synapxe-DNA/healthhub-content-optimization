import os

import pyarrow.parquet as pq

ROOT = os.getcwd()
MERGED_DATA_DIRECTORY = f"./data/merged_data.parquet"

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
