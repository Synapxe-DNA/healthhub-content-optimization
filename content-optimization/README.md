# Content Optimization

## Overview <a id="kedro-pipeline"></a>

> This Kedro project with Kedro-Viz setup was generated using `kedro 0.19.6`.

This visualization shows the current (latest) Kedro pipeline. This will be updated as the pipeline progresses.

![kedro-pipeline](docs/images/kedro-pipeline.png "Kedro Pipeline")

## Rules and guidelines

- Don't remove any lines from the `.gitignore` file provided (although you may modify or add to it)
- Make sure any results can be reproduced by following a [data engineering convention](https://docs.kedro.org/en/stable/faq/faq.html#what-is-data-engineering-convention)
- Don't commit data to the repository
- Don't commit any credentials or local configuration to the repository. Keep all credentials and local configuration in [`conf/local/`](conf/local)

## How to install dependencies

<a id="note"></a>
> **Note:** This assumes that you have already created and activated your virtual environment. For more information on how to get set up, refer [here](../README.md#installation). From this section onwards, do also take note that you are in the `content-optimization` directory. Simply check by running `pwd` in your terminal and `cd content-optimization` if you're not already there.

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

## How to run the Kedro pipeline

Similarly, ensure you're in the correct directory. Refer [here](#note) for more information. You can simply run the Kedro project with:

```bash
kedro run
```

This will run the entire project for all pipelines.

## How to run specific pipelines

### Data Processing

> **❗ Important:** Before running the `data_processing` [pipeline](src/content_optimization/pipelines/data_processing/pipeline.py)), ensure that you have the raw data in the [`data/01_raw/all_contents`](../content-optimization/data/01_raw/all_contents) directory.

You can run the entire `data_processing` pipeline by running:

```bash
kedro run --pipeline=data_processing
```

If for any reason, you would like to run specific nodes in the `data_processing` pipeline, you can run:

```bash
# Running only the `process_data_node`
kedro run --nodes="process_data_node"
```

The pipeline is a [Directed Acyclic Graph (DAG)](https://en.wikipedia.org/wiki/Directed_acyclic_graph). You can view the visualization [here](#kedro-pipeline). This means that if it's your first time running the pipeline, you should ensure that the nodes are ran in order.

> **Note:** For example in the `data_processing` pipeline, you should run the `process_data_node` first, followed by the `extract_data_node`. After this, you may run the nodes in any order for subsequent runs. This is because there may be intermediate outputs that are required in subsequent nodes.
