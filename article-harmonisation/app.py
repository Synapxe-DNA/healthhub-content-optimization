from io import StringIO

import streamlit as st
from evaluations import calculate_readability
from harmonisation import (
    COMPILER,
    CONTENT_GUIDELINES,
    META_DESC,
    RESEARCHER,
    TITLE,
    WRITING_GUIDELINES,
    app,
    print_checks,
)
from models import start_llm

# Available models configured to the project
MODELS = ["mistral", "llama3"]

# Declaring model to use
MODEL = MODELS[1]

researcher_agent = start_llm(MODEL, RESEARCHER)
compiler_agent = start_llm(MODEL, COMPILER)
meta_desc_agent = start_llm(MODEL, META_DESC)
title_agent = start_llm(MODEL, TITLE)
content_guidelines_agent = start_llm(MODEL, CONTENT_GUIDELINES)
writing_guidelines_agent = start_llm(MODEL, WRITING_GUIDELINES)

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
        score, level = calculate_readability(texts[i], choice="hemmingway")
        cols[i].write(f"Readability score: {score}, Reading level: {level}")
        with cols[i].container(height=800):
            st.write(texts[i])
st.divider()

# Run AI Agent and Display Output
if texts:
    inputs = {
        "article_content": texts,
        "keypoints": [],
        "article_researcher_counter": 0,
        "flag_for_content_optimisation": True,
        "flag_for_title_optimisation": False,
        "flag_for_meta_desc_optimisation": False,
        "researcher_agent": researcher_agent,
        "compiler_agent": compiler_agent,
        "meta_desc_agent": meta_desc_agent,
        "title_agent": title_agent,
        "content_guidelines_agent": content_guidelines_agent,
        "writing_guidelines_agent": writing_guidelines_agent,
    }

    result = app.invoke(inputs)

    # Prints the various checks
    print_checks(result)

    with st.container(height=500):
        st.write("\n".join(result["keypoints"]))
