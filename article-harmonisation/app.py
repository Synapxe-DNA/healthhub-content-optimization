import re
from io import StringIO

import streamlit as st
from agents.enums import ROLES
from agents.models import start_llm
from config import settings
from utils.evaluations import calculate_readability
from main import main

# Declaring model to use
MODEL = settings.MODEL_NAME

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
filenames = []
if uploaded_files:
    if len(uploaded_files) > 2:
        st.warning(
            "Maximum number of files reached. Only the first two files will be processed"
        )
        uploaded_files = uploaded_files[-2:]

    for file in uploaded_files:
        print(file)
        filenames.append(file.name)
        text_string = StringIO(file.getvalue().decode("utf-8")).read()
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
    result = main(filenames, setting="filename")

    with st.container(height=500):
        optimised_article_content = result["optimised_article_output"]["optimised_writing"]
        optimised_article_title = result["optimised_article_output"]["optimised_article_title"]
        optimised_meta_desc = result["optimised_article_output"]["optimised_meta_desc"]

        text = f"Title:\n{optimised_article_title}\n\nMeta Description:\n{optimised_meta_desc}\n\nContent:\n{optimised_article_content}"
        compiled_keypoints = re.sub(" +", " ", text)
        st.write(compiled_keypoints)
