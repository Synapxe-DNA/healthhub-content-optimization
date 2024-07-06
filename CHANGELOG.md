# Changelog

## July 6, 2024 <a id="july-6-2024"></a>

- Made QoL improvements to Makefile (see previous release [here](#july-4-2024) for more information)
  - Users can now specify which data directory in the Kedro project to clean
  - Users can now specify which pipeline to run from the root directory
- Usage documented in [README.md](README.md) for interested users

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
