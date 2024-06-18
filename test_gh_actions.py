import os


EMBEDDING_MODEL = "test"

INPUT_GRAPH_PATH = os.path.join("..", "artifacts", "outputs", EMBEDDING_MODEL + "_graph")

INPUT_CSV_PATH = os.path.join("..", "artifacts", "outputs", f"{EMBEDDING_MODEL}_graph_louvain_cluster.csv")

OUTPUT_GRAPH_PATH = os.path.join("..", "artifacts", "outputs", EMBEDDING_MODEL + "_graph_plot.html")
