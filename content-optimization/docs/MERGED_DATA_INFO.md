# Merged Data Information <a id="dataset-info"></a>

## General Information <a id="merged-data-general-information"></a>

- **Location**: [`data/03_primary/`](../data/03_primary/)
- **Dataset Description:** Merged collection of Health Hub articles across different content categories
- **Version**: v1
- **Date of Creation:** June 28, 2024
- **Last Updated:** August 2, 2024

## File Information <a id="merged-data-file-information"></a>

- **File Format:** Apache Parquet
- **Number of Files:** 1
- **Total Size:** 13.5MB

## Data Schema <a id="merged-data-data-schema"></a>

- **Number of Rows:** 2613
- **Number of Columns:** 39
- **Subject Area/Domain:** Health Hub Articles

### **Columns** <a id="merged-data-columns"></a>

<details>
  <summary>Expand for more information</summary>

- **`id`**
  <details>

  - Data Type: `integer`
  - Description:
    - Corresponds to the Article ID
  - Example Values:
    - 1464154
  - Null Values Allowed: No
  - Primary Key: Yes
  - Foreign Key: No

  </details>

- **`content_name`**
  <details>

  - Data Type: `string`
  - Description:
    - Name of the article stored as metadata
  - Example Values:
    - Zopiclone
  - Null Values Allowed: No
  - Primary Key: No
  - Foreign Key: No

  </details>

- **`title`**
  <details>

  - Data Type: `string`
  - Description:
    - Title of the article
  - Example Values:
    - deLIGHTS for Diabetic Patients
  - Null Values Allowed: No
  - Primary Key: No
  - Foreign Key: No

  </details>

- **`article_category_names`**
  <details>

  - Data Type: `string`
  - Description:
    - Categories that articles can belong to
  - Example Values:
    - Food & Nutrition, Exercise and Fitness
  - Null Values Allowed: Yes
  - Primary Key: No
  - Foreign Key: No

  </details>

- **`cover_image_url`**
  <details>

  - Data Type: `string`
  - Description:
    - URL of the cover image of the article
  - Null Values Allowed: Yes
  - Primary Key: No
  - Foreign Key: No

  </details>

- **`full_url`**

  <details>

  - Data Type: `string`
  - Description:
    - URL of the article
  - Null Values Allowed: No
  - Primary Key: No
  - Foreign Key: No

  </details>

- **`full_url2`**

  <details>

  - Data Type: `string`
  - Description:
    - URL of the article (backup)
  - Null Values Allowed: No
  - Primary Key: No
  - Foreign Key: No

  </details>

- **`friendly_url`**

  <details>

  - Data Type: `string`
  - Description:
    - File path with reference from content category for redirection
  - Example Values:
    - dont-forget-your-form
  - Null Values Allowed: No
  - Primary Key: No
  - Foreign Key: No

  </details>

- **`category_description`**

  <details>

  - Data Type: `string`
  - Description:
    - Brief Summary of the article that is typically found at the top of the webpage
  - Example Values:
    - Learn how your mind affects your physical and emotional health to strengthen your mental well-being.
  - Null Values Allowed: Yes
  - Primary Key: No
  - Foreign Key: No

  </details>

- **`content_body`**

  <details>

  - Data Type: `string`
  - Description:
    - HTML element containing the entire article body
  - Null Values Allowed: Yes
  - Primary Key: No
  - Foreign Key: No

  </details>

- **`keywords`**

  <details>

  - Data Type: `string`
  - Description:
    - Article Keywords
  - Example Values:
    - ICD-21-Health Services,PER_Parent,PGM_Student Screening,PGM_HealthAmbassador,AGE_Teens,AGE_Young Adult,CHILD_Children,INTEREST_Body Care,
  - Null Values Allowed: Yes
  - Primary Key: No
  - Foreign Key: No

  </details>

- **`feature_title`**

  <details>

  - Data Type: `string`
  - Description:
    - Feature Title of the articles
  - Example Values:
    - Recipe: Nonya Curry Infused Patties
  - Null Values Allowed: Yes
  - Primary Key: No
  - Foreign Key: No

  </details>

- **`pr_name`**

  <details>

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

- **`alternate_image_text`**

  <details>

  - Data Type: `string`
  - Description:
    - Alternate Image text provided to convey the “why” of the image as it relates to the content
  - Example Values:
    - Benefits of staying smoke-free
  - Null Values Allowed: Yes
  - Primary Key: No
  - Foreign Key: No

  </details>

- **`date_modified`**

  <details>

  - Data Type: `timestamp`
  - Description:
    - Timestamp of the article when modified
  - Example Values:
    - 2022-11-15T08:35:27.0000000Z
  - Null Values Allowed: Yes
  - Primary Key: No
  - Foreign Key: No

  </details>

- **`last_month_view_count`**

  <details>

  - Data Type: `integer`
  - Description:
    - Number of views over the past month
  - Example Values:
    - 63
  - Null Values Allowed: Yes
  - Primary Key: No
  - Foreign Key: No

  </details>

- **`last_two_months_view`**

  <details>

  - Data Type: `integer`
  - Description:
    - Number of views over the past 2 months
  - Example Values:
    - 91
  - Null Values Allowed: Yes
  - Primary Key: No
  - Foreign Key: No

  </details>

- **`page_views`**

  <details>

  - Data Type: `integer`
  - Description:
    - (Google Analytics) Number of page views
  - Example Values:
    - 1138
  - Null Values Allowed: No
  - Primary Key: No
  - Foreign Key: No

  </details>

- **`engagement_rate`**

  <details>

  - Data Type: `float`
  - Description:
    - (Google Analytics) The percentage of engaged sessions for article
  - Example Values:
    - 0.658709107
  - Null Values Allowed: No
  - Primary Key: No
  - Foreign Key: No

  </details>

- **`bounce_rate`**

  <details>

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

- **`exit_rate`**

  <details>

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

- **`scroll_percentage`**

  <details>

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

- **`percentage_total_views`**

  <details>

  - Data Type: `float`
  - Description:
    - The percentage of views captured by the article within a particular content category
  - Example Values:
    - 0.002679191533943097
  - Null Values Allowed: No
  - Primary Key: No
  - Foreign Key: No

  </details>

- **`cumulative_percentage_total_views`**

  <details>

  - Data Type: `float`
  - Description:
    - The cumulative percentage of views captured within a particular content category
  - Example Values:
    - 0.6859483702369595
  - Null Values Allowed: No
  - Primary Key: No
  - Foreign Key: No

  </details>

- **`content_category`**

  <details>

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

- **`to_remove`**

  <details>

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

- **`remove_type`**

  <details>

  - Data Type: `string`
  - Description:
    - Indicates reason for removal if article is flagged
  - Example Values:
    - No HTML Tags
    - Excel Error
  - Null Values Allowed: Yes
  - Primary Key: No
  - Foreign Key: No

  </details>

- **`has_table`**

  <details>

  - Data Type: `boolean`
  - Description:
    - Check whether the article has a table element within the content body
  - Example Values:
    - True/False
  - Null Values Allowed: No
  - Primary Key: No
  - Foreign Key: No

  </details>

- **`has_image`**

  <details>

  - Data Type: `boolean`
  - Description:
    - Check whether the article has an image element within the content body
  - Example Values:
    - True/False
  - Null Values Allowed: No
  - Primary Key: No - Foreign Key: No

  </details>

- **`related_sections`**

  <details>

  - Data Type: `list[string]`
  - Description:
    - A list of extracted text within articles that are captured under “Related:” and “Read these next:”
  - Example Values:
    - ['How to Eat Right to Feel Right' 'Getting the Fats Right!' 'Banish Nasty Nibbles With Healthy Snacks' 'Getting the Fats Right!' 'Make a Healthier Choice Today!' 'Make Snacking Smart a Healthy Eating Habit']
  - Null Values Allowed: Yes
  - Primary Key: No
  - Foreign Key: No

  </details>

- **`extracted_tables`**

  <details>

  - Data Type: `list[list[list[string]]]`
  - Description:
    - A list of extracted tables as a 2d-array extracted from the content body
  - Null Values Allowed: Yes
  - Primary Key: No
  - Foreign Key: No

  </details>

- **`extracted_raw_html_tables`**

  <details>

  - Data Type: `list[string]`
  - Description:
    - A list of extracted tables in HTML extracted from the content body
  - Null Values Allowed: Yes
  - Primary Key: No
  - Foreign Key: No

  </details>

- **`extracted_links`**

  <details>

  - Data Type: `list[tuple[string, string]]`
  - Description:
    - A list of extracted links with the corresponding text from the content body
  - Example Values:
    - `[('Child Health Booklet', 'https://www.healthhub.sg/programmes/parent-hub/child-health-booklet')]`
  - Null Values Allowed: Yes
  - Primary Key: No
  - Foreign Key: No

  </details>

- **`extracted_headers`**

  <details>

  - Data Type: `list[tuple[string, string]]`
  - Description:
    - A list of headers extracted from the content body based on the `<h*>` tag
  - Example Values:
    - `[('What is this medication for?', 'h2'])]`
  - Null Values Allowed: Yes
  - Primary Key: No
  - Foreign Key: No

  </details>

- **`extracted_images`**

  <details>

  - Data Type: `list[tuple[string, string]]`
  - Description:
    - A list of alternate text and urls extracted from images based on the `<img>` tag
  - Example Values:
    - `[('chas blue card','https://ch-api.healthhub.sg/api/public/content/059bbb4ca6934cea84c745e45518b15a?v=f726ce14')]`
  - Null Values Allowed: Yes
  - Primary Key: No
  - Foreign Key: No

  </details>

- **`extracted_content_body`**

  <details>

  - Data Type: `string`
  - Description:
    - The extracted text from the `content_body` column
  - Null Values Allowed: Yes
  - Primary Key: No
  - Foreign Key: No

  </details>

- **`l1_mappings`**

  <details>

  - Data Type: `string`
  - Description:
    - A list of L1 IA Mappings presented as a joined string, delimited by "|"
  - Null Values Allowed: Yes
  - Primary Key: No
  - Foreign Key: No

  </details>

- **`l2_mappings`**

  <details>

  - Data Type: `string`
  - Description:
    - A list of L2 IA Mappings presented as a joined string, delimited by "|"
  - Null Values Allowed: Yes
  - Primary Key: No
  - Foreign Key: No

  </details>

</details>

## Data Quality and Processing <a id="merged-data-quality-and-processing"></a>

### Data Cleaning Process <a id="merged-data-data-cleaning-process"></a>

1. Standardise all column names.
2. Removed columns where all values are `NaN`.
3. Flagged articles with no content or dummy content.
4. Mark articles with tables and images in content body.
5. Extracted content body as clean text from HTML page element.
6. Extracted related sections, links, headers.
7. Flagged articles with no extracted content body.
8. Merged all articles across different content categories into one dataframe.

### Missing Data Handling <a id="merged-data-missing-data-handling"></a>

- Left as is for exploration purposes
- No data imputation was used

### Known Issues or Limitations <a id="merged-data-issues"></a>

- Issue with handling text extraction within `<div>` containers

### Data Quality Checks <a id="merged-data-data-quality-checks"></a>

- Under [`data/02_intermediate/`](../data/02_intermediate/)
