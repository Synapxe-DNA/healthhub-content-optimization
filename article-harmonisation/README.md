
## Article harmonisation
This project will be utilizing Large Language Model (LLM) graphs to harmominise similar articles, followed article optimisation based on HealthHub content playbook guidelines.

The models are deployed through HuggingFace Endpoints. Currnetly, this project uses [mistralai/Mistral-7B-Instruct-v0.3](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3) from HuggingFace.

This is the current article harmonisation flow. This diagram will be continually updated as more nodes are added in.

<p align="center">
    <img src="docs/images/Article harmonisation flow 1.png" height="500">
</p>

## Rules and Guidelines

- Don't remove any lines from the `.gitignore` file provided (although you may modify or add to it)
- Do not add any prompts into the repo due to potential leak of personal information
- Don't commit data to the repository
- Don't commit any credentials or local configuration to the repository. Remember to add `.env` to `.gitignore `

## Installation guide
Start by installing all the packages required to run the project.

```
pip install -r requirements.txt
```
Next, head to the [HuggingFace website ](https://huggingface.co/) and create a new access token under `settings`.

Copy your new token and paste it under your `.env` file. The token should be able to `write`. Be sure to save it under `.env` like so:

```
HUGGINGFACEHUB_API_TOKEN = "YOUR_TOKEN_HERE"
```
Finally, head to [`harmonisation.py`](harmonisation.py) and run the file to check if your packages are working.

## Instruction to run the project
To run the project, first ensure that you have installed all the packages in `requirements.txt`. Next, head to `harmonisation.py` and run the file to start the article harmonisation process.

Currently, the article harmonisation and optimisation is a single process but it might be bound to change in future developments.

## File Structure
- [`docs`](docs): contains all miscellaneous documents pertaining to this project
    * [`images/`](docs/images): contains all images pertaining to this project
- [`evaluations.py`](evaluations.py): python file containing the metric to evaluate the articles
- [`harmonisation.py`](harmonisation.py): python file containing the graph. Run this file to run the article harmonisation process
- [`models.py`](models.py): python file containing classes to instantiate each LLM used in the project.
- [`prompts.py`](prompts.py): python file containing classes to instantiate prompts unique to each LLM type. Do note that different LLM will have different prompts that can be retrieved under their respective classes.
- [`requirements.txt`](requirements.txt): txt file containing all the packages need to run the project.
