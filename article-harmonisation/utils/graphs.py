from typing import Any, Callable, Optional, TypedDict

from langgraph.graph import MessagesState, StateGraph
from langgraph.graph.graph import CompiledGraph
from phoenix.trace.langchain import LangChainInstrumentor


# Creating a StateGraph object with GraphState as input.
def create_graph(
    schema: TypedDict,
    nodes: dict[str, Callable[[MessagesState], dict]],
    edges: dict[str, list[str]],
    conditional_edges: Optional[dict[str, tuple[Callable, dict[str, str]]]] = None,
) -> CompiledGraph:
    """
    Creates and compiles a StateGraph object based on the provided schema, nodes, and edges.

    This function constructs a workflow by adding nodes and edges to a StateGraph,
    with optional conditional edges. The final compiled graph is returned.

    Args:
        schema (TypedDict): The schema used to initialize the StateGraph.
        nodes (dict[str, Callable[[MessagesState], dict]]): A dictionary of node names mapped to their corresponding callable
            functions that process messages.
        edges (dict[str, list[str]]): A dictionary representing the edges between nodes. The keys are start nodes and the
            values are lists of end nodes.
        conditional_edges (Optional[dict[str, tuple[Callable, dict[str, str]]]], optional): A dictionary representing conditional
            edges between nodes. The keys are start nodes, and the values are tuples containing a condition function and
            a mapping of possible paths. Defaults to None.

    Returns:
        CompiledGraph: The compiled StateGraph object ready for execution.

    Example:
        graph = create_graph(schema, nodes, edges, conditional_edges)
    """

    # Create a StateGraph object with GraphState as input.
    workflow = StateGraph(schema)

    # Adding the nodes to the workflow
    for name, func in nodes.items():
        workflow.add_node(name, func)

    # Add edges to the workflow
    for start_node, end_nodes in edges.items():
        for end_node in end_nodes:
            workflow.add_edge(start_node, end_node)

    # Add conditional edges if provided
    if conditional_edges is not None:
        for start_node, values in conditional_edges.items():
            func, path_map = values
            workflow.add_conditional_edges(start_node, func, path_map)

    # Compile into a graph
    graph = workflow.compile()

    return graph


def draw_graph(graph: CompiledGraph, filepath: str) -> None:
    """
    Draws the graph and saves it as a PNG image at the specified file path.

    This function generates a visual representation of the compiled graph
    and saves it as a PNG file using the Mermaid diagram tool.

    Args:
        graph (CompiledGraph): The compiled graph object to be visualized.
        filepath (str): The file path where the PNG image should be saved.

    Example:
        draw_graph(graph, "/path/to/graph.png")
    """

    # Generate a visual representation of the graph and save it as a PNG image
    img = graph.get_graph(xray=True).draw_mermaid_png()
    with open(filepath, "wb") as f:
        f.write(img)


def execute_graph(graph: CompiledGraph, input: dict[str, Any]) -> dict[str, Any]:
    """
    Executes the compiled graph with the provided input and returns the result.

    This function runs the compiled StateGraph using the input data and traces
    the execution with LangChain instrumentation.

    Args:
        graph (CompiledGraph): The compiled graph object to be executed.
        input (dict[str, Any]): The input data for the graph execution.

    Returns:
        dict[str, Any]: The result of the graph execution.

    Example:
        result = execute_graph(graph, {"input_key": "input_value"})
    """

    # Set up LangChain tracing session for instrumentation
    LangChainInstrumentor().instrument()

    # Run LangGraph Application
    result = graph.invoke(input=input)

    # # Save traces as a parquet file
    # root_dir = get_root_dir()
    # trace_df = px.Client().get_spans_dataframe()
    # timestr = time.strftime("%Y%m%d-%H%M%S")
    # trace_df.to_parquet(f"{root_dir}/article-harmonisation/data/traces/traces-{timestr}.parquet", index=False)

    return result
