# Content Optimization

## Overview <a id="kedro-pipeline"></a>

> This Kedro project with Kedro-Viz setup was generated using `kedro 0.19.6`.

This visualization shows the current (latest) Kedro pipeline. This will be updated as the pipeline progresses.

<img src="docs/images/kedro-pipeline.png" height="1000">

## Rules and Guidelines

- Don't remove any lines from the `.gitignore` file provided (although you may modify or add to it)
- Make sure any results can be reproduced by following a [data engineering convention](https://docs.kedro.org/en/stable/faq/faq.html#what-is-data-engineering-convention)
- Don't commit data to the repository
- Don't commit any credentials or local configuration to the repository. Keep all credentials and local configuration in [`conf/local/`](conf/local)

## Install Dependencies

<a id="note"></a>

> [!NOTE]
> This assumes that you have already created and activated your virtual environment. For more information on how to get set up, refer [here](../README.md#installation). From this section onwards, do also take note that you are in the `content-optimization` directory. Simply check by running `pwd` in your terminal and `cd content-optimization` if you're not already there.

### Anaconda (Recommended)

Declare any dependencies in `requirements.txt` for `pip` installation. To install them, run:

```bash
pip install -r requirements.txt
```

### Poetry

If you're using Poetry instead, run:

```bash
cat requirements.txt | xargs poetry add
```

## File Structure

- [`conf/`](conf): contains all configurations for the project

    * [`base/`](conf/base): contains all configurations for the parameters used in the pipelines

    * [`local/`](conf/local): contains all local configurations for the project like secrets and credentials (not to be checked into version control)

> [!IMPORTANT]
> If you find any discrepancies in the extracted or merged data, please [open an issue](https://github.com/Wilsven/healthhub-content-optimization/issues).

- [`data/`](data): contains all data for the project at every stages; there are many sub-directories but here are the notable ones (will be updated as the pipeline progresses)

    * [`01_raw/all_contents/`](data/01_raw/all_contents): contains all raw data

    * [`02_intermediate/`](data/02_intermediate): contains all intermediate data

        * [`all_contents_standardized/`](data/02_intermediate/all_contents_standardized): contains all standardized data; kept only relevant columns and renamed the columns across all content categories to the same columns names

        * [`all_contents_extracted/`](data/02_intermediate/all_contents_extracted): contains all extracted data; stored in columns named `related_sections`, `extracted_content_body`, `extracted_links` and `extracted_headers`; below is a brief description what each column represents:

            * `related_sections`: related sections from the HTML content body; includes both "Related" as well as "Read these next"
            * `extracted_content_body`: extracted content body from the HTML content body
            * `extracted_links`: extracted links from the HTML content body; for example, links from the "Related" and "Read these next" sections
            * `extracted_headers`: extracted headers from the HTML content body; headers include all `<h>` tags

        * [`all_extracted_text/`](data/02_intermediate/all_extracted_text): contains all the extracted HTML content body; saved as `.txt` files; for validation and sanity checks

    * [`03_primary`](data/03_primary): contains the primary data; all processes (i.e. modeling) after data processing should only ingest the primary data

        * [`merged_data.parquet`](data/03_primary/merged_data.parquet): contains the merged data across all content categories

- [`notebooks/`](notebooks): contains all notebooks for the project; for preliminary and exploratory analysis; code to be refactored into nodes and pipelines

> [!TIP]
> It is a good to do some exploratory work in this directory to understand how the data flows and get transformed through the pipeline. Simply run `catalog.list()` to see all available data and parameters. Simply run `catalog.load("<DATA_NAME | PARAMETER>")` to load the data or parameter. For more information, simply refer to one of the existing notebooks. Happy exploring!

- [`src/content_optimization/`](src/content_optimization): contains all code for the project; contains the code for respective pipelines

## Run the Kedro Project

Similarly, ensure you're in the correct directory. Refer [here](#note) for more information. You can simply run the Kedro project with:

```bash
kedro run
```

This will run the entire project for all pipelines.

## Run Pipelines

### Data Processing

> [!IMPORTANT]
> Before running the `data_processing` [pipeline](src/content_optimization/pipelines/data_processing/pipeline.py)), ensure that you have the raw data in the [`data/01_raw/all_contents`](../content-optimization/data/01_raw/all_contents) directory.

You can run the entire `data_processing` pipeline by running:

```bash
kedro run --pipeline=data_processing
```

If for any reason, you would like to run specific nodes in the `data_processing` pipeline, you can run:

```bash
# Running only the `standardize_columns_node`
kedro run --nodes="standardize_columns_node"
```

The pipeline is a [Directed Acyclic Graph (DAG)](https://en.wikipedia.org/wiki/Directed_acyclic_graph). You can view the visualization [here](#kedro-pipeline). This means that if it's your first time running the pipeline, you should ensure that the nodes are ran in order.

> [!NOTE]
> For example in the `data_processing` pipeline, you should run the `standardize_columns_node` first, followed by the `extract_data_node` then `merge_data_node`. After this, you may run the nodes in any order for subsequent runs. This is because there may be intermediate outputs that are required in subsequent nodes.

### Data Science


## Dataset

<details>
<summary>Information Sheet - HealthHub Articles</summary>

### General Information

- **Dataset Name:** `merged_data.parquet`
- **Location**: `content-optimization/data/03_primary`
- **Dataset Description:** Merged collection of HealthHub articles across different content categories
- **Version**: v1
- **Date of Creation:** June 28, 2024
- **Last Updated:** June 28, 2024

### File Information

- **File Format:** Apache Parquet
- **Number of Files:** 1
- **Total Size:** 13.5MB

### Data Schema

- **Number of Rows:** 2613
- **Number of Columns:** 33
- **Subject Area/Domain:** HealthHub Articles
- **Column Details:**

    <details>
        <summary>id</summary>

    - Data Type: `integer`
    - Description:
        - Corresponds to the Article ID
    - Example Values:
        - 1464154
    - Null Values Allowed: No
    - Primary Key: Yes
    - Foreign Key: No
    </details>

    <details>
        <summary>content_name</summary>

    - Data Type: `string`
    - Description:
        - Name of the article stored as metadata
    - Example Values:
        - Zopiclone
    - Null Values Allowed: No
    - Primary Key: No
    - Foreign Key: No
    </details>

    <details>
        <summary>title</summary>

    - Data Type: `string`
    - Description:
        - Title of the article
    - Example Values:
        - deLIGHTS for Diabetic Patients
    - Null Values Allowed: No
    - Primary Key: No
    - Foreign Key: No
    </details>

    <details>
        <summary>article_category_names</summary>

    - Data Type: `string`
    - Description:
        - Categories that articles can belong to
    - Example Values:
        - Food & Nutrition, Exercise and Fitness
    - Null Values Allowed: Yes
    - Primary Key: No
    - Foreign Key: No
    </details>

    <details>
        <summary>cover_image_url</summary>

    - Data Type: `string`
    - Description:
        - URL of the cover image of the article
    - Null Values Allowed: Yes
    - Primary Key: No
    - Foreign Key: No
    </details>

    <details>
        <summary>full_url</summary>

    - Data Type: `string`
    - Description:
        - URL of the article
    - Null Values Allowed: No
    - Primary Key: No
    - Foreign Key: No
    </details>

    <details>
        <summary>full_url2</summary>

    - Data Type: `string`
    - Description:
        - URL of the article (backup)
    - Null Values Allowed: No
    - Primary Key: No
    - Foreign Key: No
    </details>

    <details>
        <summary>friendly_url</summary>

    - Data Type: `string`
    - Description:
        - File path with reference from content category for redirection
    - Example Values:
        - dont-forget-your-form
    - Null Values Allowed: No
    - Primary Key: No
    - Foreign Key: No
    </details>

    <details>
        <summary>category_description</summary>

    - Data Type: `string`
    - Description:
        - Brief Summary of the article that is typically found at the top of the webpage
    - Example Values:
        - Learn how your mind affects your physical and emotional health to strengthen your mental well-being.
    - Null Values Allowed: Yes
    - Primary Key: No
    - Foreign Key: No
    </details>

    <details>
        <summary>content_body</summary>

    - Data Type: `string`
    - Description:
        - HTML element containing the entire article body
    - Null Values Allowed: Yes
    - Primary Key: No
    - Foreign Key: No
    </details>

    <details>
        <summary>keywords</summary>

    - Data Type: `string`
    - Description:
        - Article Keywords
    - Example Values:
        - ICD-21-Health Services,PER_Parent,PGM_Student Screening,PGM_HealthAmbassador,AGE_Teens,AGE_Young Adult,CHILD_Children,INTEREST_Body Care,
    - Null Values Allowed: Yes
    - Primary Key: No
    - Foreign Key: No
    </details>

    <details>
        <summary>feature_title</summary>

    - Data Type: `string`
    - Description:
        - Feature Title of the articles
    - Example Values:
        - Recipe: Nonya Curry Infused Patties
    - Null Values Allowed: Yes
    - Primary Key: No
    - Foreign Key: No
    </details>

    <details>
        <summary>pr_name</summary>

    - Data Type: `string`
    - Description:
        - Provider Name
    - Example Values:
        - Active Health
        - Health Promotion Board
    - Null Values Allowed: Yes
    - Primary Key: No
    - Foreign Key: Yes
    </details>

    <details>
        <summary>alternate_image_text</summary>

    - Data Type: `string`
    - Description:
        - Alternate Image text provided to convey the “why” of the image as it relates to the content
    - Example Values:
        - Benefits of staying smoke-free
    - Null Values Allowed: Yes
    - Primary Key: No
    - Foreign Key: No
    </details>

    <details>
        <summary>date_modified</summary>

    - Data Type: `timestamp`
    - Description:
        - Timestamp of the article when modified
    - Example Values:
        - 2022-11-15T08:35:27.0000000Z
    - Null Values Allowed: Yes
    - Primary Key: No
    - Foreign Key: No
    </details>

    <details>
        <summary>number_of_views</summary>

    - Data Type: `integer`
    - Description:
        - Number of views for the article
    - Example Values:
        - 7925
    - Null Values Allowed: Yes
    - Primary Key: No
    - Foreign Key: No
    </details>

    <details>
        <summary>last_month_view_count</summary>

    - Data Type: `integer`
    - Description:
        - Number of views over the past month
    - Example Values:
        - 63
    - Null Values Allowed: Yes
    - Primary Key: No
    - Foreign Key: No
    </details>

    <details>
        <summary>last_two_months_view</summary>

    - Data Type: `integer`
    - Description:
        - Number of views over the past 2 months
    - Example Values:
        - 91
    - Null Values Allowed: Yes
    - Primary Key: No
    - Foreign Key: No
    </details>

    <details>
        <summary>page_views</summary>

    - Data Type: `integer`
    - Description:
        - (Google Analytics) Number of page views
    - Example Values:
        - 1138
    - Null Values Allowed: No
    - Primary Key: No
    - Foreign Key: No
    </details>

    <details>
        <summary>engagement_rate</summary>

    - Data Type: `float`
    - Description:
        - (Google Analytics) The percentage of engaged sessions for article
    - Example Values:
        - 0.658709107
    - Null Values Allowed: No
    - Primary Key: No
    - Foreign Key: No
    </details>

    <details>
        <summary>bounce_rate</summary>

    - Data Type: `float`
    - Description:
        - (Google Analytics) The percentage of sessions that were not engaged
            - Opposite of Engagement Rate
    - Example Values:
        - 0.34129089300000004
    - Null Values Allowed: No
    - Primary Key: No
    - Foreign Key: No
    </details>

    <details>
        <summary>exit_rate</summary>

    - Data Type: `float`
    - Description:
        - (Google Analytics) The percentage of sessions that ended on a page or screen
            - Equivalent to the number of exits divided by the number of sessions.
    - Example Values:
        - 0.9041850220264317
    - Null Values Allowed: No
    - Primary Key: No
    - Foreign Key: No
    </details>

    <details>
        <summary>scroll_percentage</summary>

    - Data Type: `float`
    - Description:
        - (Google Analytics) Measures how far users scroll down a page before leaving
            - Also known as scroll depth
            - 100% represents that users, on average, scroll to the bottom of the page.
    - Example Values:
        - 0.35698594
    - Null Values Allowed: No
    - Primary Key: No
    - Foreign Key: No
    </details>

    <details>
        <summary>percentage_total_views</summary>

    - Data Type: `float`
    - Description:
        - The percentage of views captured by the article within a particular content category
    - Example Values:
        - 0.002679191533943097
    - Null Values Allowed: No
    - Primary Key: No
    - Foreign Key: No
    </details>

    <details>
        <summary>cumulative_percentage_total_views</summary>

    - Data Type: `float`
    - Description:
        - The cumulative percentage of views captured within a particular content category
    - Example Values:
        - 0.6859483702369595
    - Null Values Allowed: No
    - Primary Key: No
    - Foreign Key: No
    </details>

    <details>
        <summary>content_category</summary>

    - Data Type: `string`
    - Description:
        - The content category that the article corresponds to on HealthHub
    - Example Values:
        - medications
        - live-healthy-articles
        - diseases-and-conditions
    - Null Values Allowed: No
    - Primary Key: No
    - Foreign Key: Yes
    </details>

    <details>
        <summary>to_remove</summary>

    - Data Type: `boolean`
    - Description:
        - Indicates whether the articles have met the criteria for removal
            - No content / Dummy content
            - No extracted content
    - Example Values:
        - True/False
    - Null Values Allowed: No
    - Primary Key: No
    - Foreign Key: No
    </details>

    <details>
        <summary>has_table</summary>

    - Data Type: `boolean`
    - Description:
        - Check whether the article has a table element within the content body
    - Example Values:
        - True/False
    - Null Values Allowed: No
    - Primary Key: No
    - Foreign Key: No
    </details>

    <details>
        <summary>has_image</summary>

    - Data Type: `boolean`
    - Description:
        - Check whether the article has an image element within the content body
    - Example Values:
        - True/False
    - Null Values Allowed: No
    - Primary Key: No
    - Foreign Key: No
    </details>

    <details>
        <summary>related_sections</summary>

    - Data Type: `list[string]`
    - Description:
        - A list of extracted text within articles that are captured under “Related:” and “Read these next:”
    - Example Values:
        - ['How to Eat Right to Feel Right' 'Getting the Fats Right!' 'Banish Nasty Nibbles With Healthy Snacks' 'Getting the Fats Right!' 'Make a Healthier Choice Today!' 'Make Snacking Smart a Healthy Eating Habit']
    - Null Values Allowed: Yes
    - Primary Key: No
    - Foreign Key: No
    </details>

    <details>
        <summary>extracted_links</summary>

    - Data Type: `list[tuple[string, string]]`
    - Description:
        - A list of extracted links with the corresponding text from the content body
    - Example Values:
        - `[('Child Health Booklet', 'https://www.healthhub.sg/programmes/parent-hub/child-health-booklet')]`
    - Null Values Allowed: Yes
    - Primary Key: No
    - Foreign Key: No
    </details>

    <details>
        <summary>extracted_headers</summary>

    - Data Type: `list[tuple[string, string]]`
    - Description:
        - A list of headers extracted from the content body based on the `<h*>` tag
    - Example Values:
        - `[('What is this medication for?', 'h2'])]`
    - Null Values Allowed: Yes
    - Primary Key: No
    - Foreign Key: No
    </details>

    <details>
        <summary>extracted_content_body</summary>

    - Data Type: `string`
    - Description:
        - The extracted text from the `content_body` column
    - Null Values Allowed: Yes
    - Primary Key: No
    - Foreign Key: No
    </details>

### Data Quality and Processing

- **Data Cleaning Process:**
    - Standardise all column names
    - Removed columns where all values are `NaN`
    - Flagged articles with no content or dummy content
    - Mark articles with tables and images in content body
    - Extracted content body as clean text from HTML PageElement
    - Extracted related sections, links, headers
    - Flagged articles with no extracted content body
    - Merged all articles across different content categories into one dataframe

- **Missing Data Handling:**
    - Left as is for exploration purposes
    - No data imputation was used

- **Known Issues or Limitations:**
    - Issue with handling text extraction within `div` containers

- **Data Quality Checks:**
    - Under `content-optimization/data/02_intermediate`

### Changelog

- June 28, 2024 - Created `merged_data.parquet` in `content-optimization/data/03_primary/merged_data.parquet`

</details>
