from typing import Dict

from yaml import safe_load
from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph

from config.project_config import Settings
from llms.base_llm import AgentState
from llms.cart_manager.core import CartManager
from llms.core.core import Core
from llms.writer.core import Writer


def build_graph() -> CompiledStateGraph:
    # load config
    settings = Settings()
    graph_config: Dict = safe_load(open(settings.graph_config_path))

    # mapping
    mapping = {
        "Core": lambda state: Core().run(state),
        "CartManager": lambda state: CartManager().run(state),
        "Writer": lambda state: Writer().run(state),
    }

    # setup graph
    graph: StateGraph = StateGraph(AgentState)

    def routing_function(state: AgentState) -> str:
        return state.route

    # set nodes
    for node in graph_config["graph_architecture"]["nodes"]:
        graph.add_node(node["name"], mapping[node["name"]])
        if node["entry"]:
            graph.set_entry_point(node["name"])
        if node["exit"]:
            graph.set_finish_point(node["name"])

    # set edges
    conditional_edges = [e for e in graph_config["graph_architecture"]["edges"] if e.get("conditional")]
    normal_edges = [e for e in graph_config["graph_architecture"]["edges"] if not e.get("conditional")]

    for edge in normal_edges:
        graph.add_edge(edge["from"], edge["to"])

    grouped = {}
    for edge in conditional_edges:
        grouped.setdefault(edge["from"], []).append(edge["to"])

    for from_node, to_nodes in grouped.items():
        graph.add_conditional_edges(
            from_node,
            routing_function,
            {node: node for node in to_nodes}
        )

    return graph.compile()