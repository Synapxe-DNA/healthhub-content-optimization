import re
from io import StringIO

import streamlit as st
from agents.enums import MODELS, ROLES
from agents.models import start_llm
from config import settings
from harmonisation import execute_graph, workflow
from utils.evaluations import calculate_readability
from utils.formatters import concat_headers_to_content

CONFIG = settings

# Declaring model to use
MODEL = MODELS("llama3").name

# Define Agents
researcher_agent = start_llm(MODEL, ROLES.RESEARCHER)
compiler_agent = start_llm(MODEL, ROLES.COMPILER)
meta_desc_agent = start_llm(MODEL, ROLES.META_DESC)
title_agent = start_llm(MODEL, ROLES.TITLE)
content_optimisation_agent = start_llm(MODEL, ROLES.CONTENT_OPTIMISATION)
writing_optimisation_agent = start_llm(MODEL, ROLES.WRITING_OPTIMISATION)
title_optimisation_agent = start_llm(MODEL, ROLES.TITLE)
meta_desc_optimisation_agent = start_llm(MODEL, ROLES.META_DESC)

# Set Page Config and Title for Streamlit
st.set_page_config(page_title="Article Harmonisation", layout="wide")
st.title("Article Harmonisation Demo")
st.divider()

# Upload File Section
uploaded_files = st.file_uploader(
    "Upload your text here. File Limit: 2", type=["txt"], accept_multiple_files=True
)
st.divider()

# Show Extracted Text and Readability Score
texts = []
if uploaded_files:
    if len(uploaded_files) > 2:
        st.warning(
            "Maximum number of files reached. Only the last two files will be processed"
        )
        uploaded_texts = uploaded_files[:2]

    for uploaded_file in uploaded_files:
        text_string = StringIO(uploaded_file.getvalue().decode("utf-8")).read()
        texts.append(text_string)

    cols = st.columns(len(texts), vertical_alignment="top")
    for i in range(len(cols)):
        metrics = calculate_readability(texts[i], choice="hemmingway")
        score = metrics["score"]
        level = metrics["level"]
        cols[i].write(f"Readability score: {score}, Reading level: {level}")
        with cols[i].container(height=800):
            st.write(texts[i])
st.divider()

# Run AI Agent and Display Output
if texts:
    processed_input_articles = concat_headers_to_content(texts)

    inputs = {
        "original_article_content": {"article_content": processed_input_articles},
        "optimised_article_output": {
            "researcher_keypoints": [],
            "article_researcher_counter": 0,
        },
        "user_flags": {
            "flag_for_content_optimisation": True,
            "flag_for_title_optimisation": True,
            "flag_for_meta_desc_optimisation": True,
        },
        "llm_agents": {
            "researcher_agent": researcher_agent,
            "compiler_agent": compiler_agent,
            "content_optimisation_agent": content_optimisation_agent,
            "writing_optimisation_agent": writing_optimisation_agent,
            "title_optimisation_agent": title_optimisation_agent,
            "meta_desc_optimisation_agent": meta_desc_optimisation_agent,
        },
    }

    result = execute_graph(workflow=workflow, input=inputs)

    with st.container(height=500):
        compiled_keypoints = re.sub(" +", " ", result["compiled_keypoints"])
        st.write(compiled_keypoints)
