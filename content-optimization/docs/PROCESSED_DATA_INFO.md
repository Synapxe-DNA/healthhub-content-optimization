# Processed Articles Information <a id="processed-articles"></a>

## General Information <a id="processed-articles-general-information"></a>

- **Location**: [`data/03_primary`](../data/03_primary/)
- **Dataset Description:** JSON format of the article content and tables files
- **Version**: v1
- **Date of Creation:** August 28, 2024
- **Last Updated:** August 28, 2024

## File Information <a id="processed-articles-file-information"></a>

- **File Format:** JSON
- **Number of Files:** 2724
- **Total Size:** 31.8MB

## Data Schema <a id="merged-data-data-schema"></a>

- Not applicable.

### **Columns** <a id="processed-articles-columns"></a>

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

- **`content`**

  <details>

  - Data Type: `string`
  - Description:
    - Post processed table/article content by the LLM.
  - Null Values Allowed: Yes
  - Primary Key: No
  - Foreign Key: No

  </details>

</details>

## Data Quality and Processing <a id="processed-articles-data-quality-and-processing"></a>

### Data Cleaning Process <a id="processed-articles-data-cleaning-process"></a>

1. Filter articles by their `to_remove` categories
2. Convert the data in `content_body` column to `processed_table_content` with a language model.
3. Split the dataframe by rows and according to their `extracted_content_body` and `processed_table_content` to `{row_id}_content.json` and `{row_id}_table.json`.

### Missing Data Handling <a id="processed-articles-missing-data-handling"></a>

- Left as is for exploration purposes
- No data imputation was used

### Known Issues or Limitations <a id="processed-articles-issues"></a>

- Not applicable.

### Data Quality Checks <a id="processed-articles-data-quality-checks"></a>

- Not applicable.
