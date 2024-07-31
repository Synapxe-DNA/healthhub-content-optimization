from langgraph.graph import MessagesState, StateGraph
from langgraph.graph.graph import CompiledGraph

from typing import Any, Callable, TypedDict, Optional
import phoenix as px
import time
from phoenix.trace.langchain import LangChainInstrumentor
from .paths import get_root_dir


# Creating a StateGraph object with GraphState as input.
def create_graph(
        schema: TypedDict,
        nodes: dict[str, Callable[[MessagesState], dict]],
        edges: dict[str, list[str]],
        conditional_edges: Optional[dict[str, tuple[Callable, dict[str, str]]]] = None,
):
    # creating a StateGraph object with GraphState as input.
    workflow = StateGraph(schema)

    # Adding the nodes to the workflow
    for name, func in nodes.items():
        workflow.add_node(name, func)

    # Adding the edges to the workflow
    for start_node, end_nodes in edges.items():
        for end_node in end_nodes:
            workflow.add_edge(start_node, end_node)

    if conditional_edges is not None:
        for start_node, values in conditional_edges.items():
            func, path_map = values
            workflow.add_conditional_edges(
                start_node,
                func,
                path_map
            )

    graph = workflow.compile()

    return graph


def draw_graph(graph: CompiledGraph, filepath: str):
    img = graph.get_graph(xray=True).draw_mermaid_png()
    with open(filepath, "wb") as f:
        f.write(img)


def execute_graph(graph: CompiledGraph, input: dict[str, Any]) -> dict[str, Any]:
    # Set up LLM tracing session
    LangChainInstrumentor().instrument()

    # Run LangGraph Application
    result = graph.invoke(input=input)

    # root_dir = get_root_dir()
    # trace_df = px.Client().get_spans_dataframe()
    # timestr = time.strftime("%Y%m%d-%H%M%S")
    # trace_df.to_parquet(f"{root_dir}/article-harmonisation/data/traces/traces-{timestr}.parquet", index=False)

    return result
