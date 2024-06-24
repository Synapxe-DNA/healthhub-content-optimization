# Content Optimization

## Overview

This Kedro project with Kedro-Viz setup was generated using `kedro 0.19.6`.

## Rules and guidelines

- Don't remove any lines from the `.gitignore` file provided (although you may modify or add to it)
- Make sure any results can be reproduced by following a [data engineering convention](https://docs.kedro.org/en/stable/faq/faq.html#what-is-data-engineering-convention)
- Don't commit data to the repository
- Don't commit any credentials or local configuration to the repository. Keep all credentials and local configuration in [`conf/local/`](content-optimization/conf/local)

## How to install dependencies

### Anaconda (recommended)

Declare any dependencies in `requirements.txt` for `pip` installation. To install them, run:

```bash
pip install -r requirements.txt
```

### Poetry

If you're using Poetry instead, run:

```bash
cat requirements.txt | xargs poetry add
```

> **Note:** This assumes that you have already created and activated your virtual environment. For more information on how to get set up, refer [here](../README.md#installation).

## How to run the Kedro pipeline

You can simply run the Kedro project with:

```bash
kedro run
```
