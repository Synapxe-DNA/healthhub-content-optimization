# Changelog

## July 3, 2024

- Added utility functions in [`utils.py`](content-optimization/src/content_optimization/pipelines/data_processing/utils.py) in `data_processing` pipeline to flag the articles for removal as well as assign the respective types

## July 1, 2024

- Added addtional feature to flag articles for removal below a certain word count (for more information, you can see the [`word_count.ipynb`](content-optimization/notebooks/word_count.ipynb) notebook)
- Reporting files are generated, versioned and stored in [`content-optimization/data/08_reporting`](content-optimization/data/08_reporting)

## June 28, 2024

- Refactored pipeline to standarized the column names to facilitate downstream merging
- The merged data is generated, versioned and stored in [`content-optimization/data/03_primary`](content-optimization/data/03_primary)
