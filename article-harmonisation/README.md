# Article harmonisation

## Introduction

This project will be utilizing Large Language Model (LLM) graphs to harmonise similar articles, followed article optimisation based on HealthHub content playbook guidelines.
The models are deployed through Azure OpenAI Endpoints. Currently, this project uses [GPT-4o-mini](https://azure.microsoft.com/en-us/blog/openais-fastest-model-gpt-4o-mini-is-now-available-on-azure-ai/) from Microsoft Azure.

> [!WARNING]
> The prompts for the HuggingFace models are not updated as we no longer use them. You will need to update the prompts and LLM Chains to mimic the implementation for Azure OpenAI Chat models.

The article harmonisation process is broken up into 2 stages -

1. Article Optimisation Checks

  <p align="center">
      <img src="docs/images/Optimisation%20Checks%20Flow.jpg" width="600", alt="Article Optimisation Checks">
  </p>
2. Article Rewriting
  <p align="center">
      <img src="docs/images/Article%20Rewriting%20Flow.jpg" width="600", alt="Article Rewriting">
  </p>

This is the current article harmonisation flow. This diagram will be continually updated as more nodes are added in.

## Rules and Guidelines

- Don't remove any lines from the `.gitignore` file provided (although you may modify or add to it)
- Don't commit data to the repository
- Don't commit any credentials or local configuration to the repository. Remember to add `.env` to `.gitignore`

## Installation guide

### Installing Relevant Packages

Start by installing all the packages required to run the project.

```zsh
pip install -r requirements.txt
```

### Setting up Microsoft Azure OpenAI

First, install the Azure Command-Line Interface (CLI) to access the Azure resources. Refer to this [guide](https://learn.microsoft.com/en-us/cli/azure/) for the installation procedures.

Sign in to your Azure account via the CLI. Refer to this [guide](https://learn.microsoft.com/en-us/cli/azure/authenticate-azure-cli-managed-identity).

After a successful login, run the following command to check that your credentials are saved -

```bash
  az account show
```

Next, head to the [Microsoft Azure](https://www.portal.azure.com/#home) and set up the Azure OpenAI Chat Model Deployment.

Copy your new token and paste it under your `.env` file.

- Set the Resource Name as `AZURE_OPENAI_API_SERVICE`
- Set the Deployment Name as `AZURE_DEPLOYMENT_NAME`.
- Set the Endpoint URL (`AZURE_OPENAI_ENDPOINT`) as `f"https://{AZURE_OPENAI_API_SERVICE}.openai.azure.com/"`. Replace `{AZURE_OPENAI_API_SERVICE}` in the URL.
- Set the `AZURE_OPENAI_API_VERSION` to the latest version mentioned [here](https://learn.microsoft.com/en-us/azure/ai-services/openai/api-version-deprecation)

Finally, head to [`quickstart.py`](examples/quickstart.py) and run the file to check if your packages are working.

### Setting up LLM Observability via arize-phoenix

To set up the `arize-phoenix` LLM observability server -

```python
    # Launches the web server at http://127.0.0.1:6006
    python3 -m phoenix.server.main serve
```

If you are unable to run the server, perform the following command - `pip install 'arize-phoenix[evals]'`. For more information, refer to [`Phoenix Setup Environment`](https://docs.arize.com/phoenix/setup/environments).

## Instruction to run the project

### Running the Optimisation Checks Workflow

To run the project, first ensure that you have installed all the packages in `requirements.txt`. Next, head to [`checks.py`](checks.py) and run the file to start the article optimization checks workflow.

Currently, the article optimization checks is ran concurrently within the workflow. This may result in deadlocks.

To run the agentic framework on CLI -

```python
    # Install the requirements within `article-harmonisation` directory
    pip install -r requirements.txt
    # Change directory to ROOT
    cd ..
    # Run the python script
    python3 ./article-harmonisation/checks.py
```

### Running the Article Rewriting Workflow

To run the project, first ensure that you have installed all the packages in `requirements.txt`. Next, head to `harmonisation.py` and run the file to start the article harmonisation process.

Currently, the article harmonisation and optimisation is a single process but it might be bound to change in future developments.

To run the agentic framework on CLI -

```python
    # Install the requirements within `article-harmonisation` directory
    pip install -r requirements.txt
    # Change directory to ROOT
    cd ..
    # Run the python script
    python3 ./article-harmonisation/harmonisation.py
```

### Running the streamlit application

> [!WARNING]
> The streamlit application is merely for prototyping purposes. It is not actively maintained due to the change in direction (i.e. generating Excel files instead).

To run the `streamlit` application -

```python
    # Install the requirements within `article-harmonisation` directory
    pip install -r requirements.txt
    # Run the streamlit demo
    streamlit run ./app.py
```

## File Structure

- [`agents`](agents): contains all the classes and functions to initialise the models, roles and prompts
  - [`enums.py`](agents/enums.py): python file containing classes to initialise the models from HuggingFace/Azure OpenAI and the roles involved in the Agentic Workflow
  - [`models.py`](agents/models.py): python file containing classes to instantiate each LLM used in the project
  - [`prompts.py`](agents/prompts.py): python file containing classes to instantiate prompts unique to each LLM type. Do note that different LLM will have different prompts that can be retrieved under their respective classes
  - [`prompts_archive.py`](agents/prompts_archive.py): python file containing classes to instantiate older prompts for each LLM type. Used to archive old prompts.
- [`data`](data): contains all the datasets pertaining to this project
  - [`final_articles`](data/marked_articles): contains the dataframes that are marked for article optimisation checks
  - [`optimization_checks`](data/optimization_checks): contains all the dataframes generated from the execution of `checks.py`
- [`docs`](docs): contains all miscellaneous documents pertaining to this project
  - [`images/`](docs/images): contains all images pertaining to this project
  - [`txt_outputs/`](docs/txt_outputs): contains all generated outputs from the chosen model when harmonisation.py is executed (stored as .txt file)
- [`examples`](examples): contains all the examples to test the execution of the LLM model
  - [`quickstart.py`](examples/quickstart.py): python file containing the script to test whether the Azure OpenAI model is working. Run this file to test if the azure resources and identity is functional.
- [`notebooks`](notebooks): contains all the Jupyter Notebooks to evaluate the project
  - [`calculate_tokens.ipynb`](notebooks/calculate_tokens.ipynb): Jupyter Notebook to calculate the tokens consumed by running the project for all articles
  - [`evalauate_word_count.ipynb`](notebooks/evaluate_word_count.ipynb): Jupyter Notebook to find a suitable threshold to perform `flag_below_word_count` for each content category
  - [`generate_annotation_excel.ipynb`](notebooks/generate_annotation_excel.ipynb): Jupyter Notebook to generate the Excel file from the Optimisation Checks output
  - [`readability_scores.ipynb`](notebooks/readability_scores.ipynb): Jupyter Notebook to calculate the readability scores for all articles
- [`states`](states): contains all the states used for the LangGraph workflow
  - [`definitions.py`](states/definitions.py): python file containing the TypedDict definitions used in the Optimisation Checks and Article Rewriting workflow
- [`utils`](utils): contains all the utility functions pertaining to this project
  - [`arize-phoenix.py`](utils/arize-phoenix.py): python file containing the functions related to `arize-phoenix` LLM Observability package
  - [`evaluations.py`](utils/evaluations.py): python file containing the metrics to evaluate the articles
  - [`formatters.py`](utils/formatters.py): python file containing functions to format inputs and outputs for ingestion and presentation purposes
  - [`graphs.py`](utils/graphs.py): python file containing functions to create, execute and draw LangGraph objects
  - [`paths.py`](utils/paths.py): python file to set the ROOT directory of the project (set at `healthhub-content-optimization`)
  - [`reducers.py`](utils/reducers.py): python file to support the merging of dictionaries when Optimisation Checks workflow is executed.
- [`.env.example`](.env.example): a template file for `.env` to contain the environment variables for the project.
- [`app.py`](app.py): python file containing the streamlit application
- [`checks.py`](checks.py): python file containing the Article Optimisation Checks workflow. Run this file to execute the optimisation checks process
- [`config.py`](config.py): python file containing the initialisation of environment variables for use within the project
- [`harmonisation.py`](harmonisation.py): python file containing the Article Rewriting workflow. Run this file to execute the rewriting process
- [`main.py`](main.py): python file to run the project
- [`requirements.txt`](requirements.txt): txt file containing all the packages needed to run the project
