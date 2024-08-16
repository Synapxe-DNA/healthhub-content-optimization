# Changelog

## August 16, 2024 <a id="august-16-2024"></a>

- Added `generate_embeddings_node` and `combine_embeddings_by_weightage_node` to [`feature_engineering`](content-optimization/src/content_optimization/pipelines/feature_engineering) pipeline to generate feature embeddings
- Added [`clustering`](content-optimization/src/content_optimization/pipelines/clustering) pipeline for two-step clustering via community detection and BERTopic

## August 8, 2024 <a id="august-8-2024"></a>

- Added `blacklist` dictionary in `parameters_data_processing.yml` with remove_type description
- Added `flag_articles_via_blacklist` to flag articles stated as blacklisted in `parameters_data_processing.yml`
- Updated `data_processing` pipeline to include `blacklist` parameter for flagging

## August 2, 2024 <a id="august-2-2024"></a>

- Added IA Mappings (L1 and L2) into the dataset as `l1_mappings` and `l2_mappings` column
- Created `all_contents_mapped` intermediate dataset to hold new IA mappings
- Renamed `add_contents_node` to `add_data_node` to include the addition of updated URLs as well
- Refactored `add_content_body` as a separate helper function to add content for articles with Excel error
- Created function to update urls for selected articles defined in `parameters_date_processing.yml`

## July 25, 2024 <a id="july-25-2024"></a>

- Added column from `extracted_raw_html_tables` column
  - Using raw html of tables for ingestion

## July 24, 2024 <a id="july-24-2024"></a>

- Renamed column from `extracted_img_alt_text` to `extracted_images`.
- Updated test cases to ensure that they all pass.

## July 18, 2024 <a id="july-18-2024"></a>

- Extended [`.pre-commit-config.yaml`](.pre-commit-config.yaml) file
- Updated GitHub Workflows
  - Renamed `lint.yml` to [`run-checks.yml`](.github/workflows/run-checks.yml)
  - Improved `run-checks.yml`

## July 17, 2024 <a id="july-17-2024"></a>

- Integrated code to flag for recipe articles

## July 16, 2024 <a id="july-16-2024"></a>

- Improved test cases for `data_processing` pipeline
- Implemented test cases for `add_contents` node
- Implemented article whitelisting within `data_processing` pipeline

## July 15, 2024 <a id="july-15-2024"></a>

- Added selected articles with `Excel Error` back into the dataset

## July 13, 2204 <a id="july-13-2024"></a>

- Added unit tests and integration test for [`feature_engineering`](content-optimization/src/content_optimization/pipelines/feature_engineering) pipeline

## July 12, 2024 <a id="july-12-2024"></a>

- Added unit tests and integration test for [`data_processing`](content-optimization/src/content_optimization/pipelines/data_processing) pipeline
- Added [data directories](content-optimization/tests/data) for test datasets
- Removed use of `alive_progress` because of incompatibility with `pytest`
- Added [`run_tests.py`](run_tests.py) to provide as an entry point for `make test`

## July 11, 2024 <a id="july-11-2024"></a>

- Added new column `extracted_tables` as a new column into `merged_data.parquet`
- Replace En Dash with a dash to extract these dashes into `extracted_content_body`
- Amended `extract_links` to ignore footnotes and online forms

## July 9, 2024 <a id="july-9-2024"></a>

- Created [`clustering`](content-optimization/src/content_optimization/pipelines/clustering) pipeline

## July 8, 2024 <a id="july-8-2024"></a>

- Overhauled the text processing in [`data_processing`](content-optimization/src/content_optimization/pipelines/data_processing) pipeline to handle edge cases across the chosen 5 content categories
- Added logging statements to monitor for edge cases during extraction (only during development)
- Added new column `extracted_img_alt_text` to preserve alternate texts present in images
- Renamed column `type` to `remove_type` for better understanding

---

- Added [`script.py`](script.py) to provide as an entry point for `make clean`
  - This is an improvement over the previous release on [July 6, 2024](#july-6-2024) where it was not compatible with Windows OS

## July 6, 2024 <a id="july-6-2024"></a>

- Made QoL improvements to Makefile (see previous release [here](#july-4-2024) for more information)
  - Users can now specify which data directory in the Kedro project to clean
  - Users can now specify which pipeline to run from the root directory
- Usage documented in [README](README.md#working-with-kedro-from-root-directory) for interested users

## July 5, 2024 <a id="july-5-2024"></a>

- Swapped out vanilla `CountVectorizer` for `KeyphraseVectorizer` in [`feature engineering`](content-optimization/src/content_optimization/pipelines/feature_engineering) pipeline
- No longer storing intermediate features such as `doc_embeddings`, `word_embeddings` and `filtered_data`

## July 4, 2024 <a id="july-4-2024"></a>

- Refactored and improved text processing pipeline to handle nested <div> containers
  - All articles should now be organised as paragraphs
- Removed `data_science` pipeline
- Added [`feature engineering`](content-optimization/src/content_optimization/pipelines/feature_engineering) pipeline to extract keywords from articles
- Updated Makefile to run Kedro from root and clean Kedro datasets for fresh run

## July 3, 2024 <a id="july-3-2024"></a>

- Added utility functions in [`utils.py`](content-optimization/src/content_optimization/pipelines/data_processing/utils.py) in `data_processing` pipeline to flag the articles for removal as well as assign the respective types

## July 1, 2024 <a id="july-1-2024"></a>

- Added additional feature to flag articles for removal below a certain word count (for more information, you can see the [`word_count.ipynb`](content-optimization/notebooks/word_count.ipynb) notebook)
- Reporting files are generated, versioned and stored in [`content-optimization/data/08_reporting`](content-optimization/data/08_reporting)

## June 28, 2024

- Refactored pipeline to standardize the column names to facilitate downstream merging
- The merged data is generated, versioned and stored in [`content-optimization/data/03_primary`](content-optimization/data/03_primary)
