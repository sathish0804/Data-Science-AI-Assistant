from typing import Annotated, TypedDict

from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph, add_messages
from dotenv import load_dotenv


class State(TypedDict):
    messages: Annotated[list, add_messages]


SEARCH_TOOL_NAME = "tavily_search_results_json"


def _build_graph():
    # Ensure env vars (OPENAI_API_KEY, TAVILY_API_KEY) are available
    load_dotenv()
    memory = MemorySaver()

    search_tool = TavilySearchResults(max_results=4)
    tools = [search_tool]

    llm = ChatOpenAI(model="gpt-4o")
    llm_with_tools = llm.bind_tools(tools=tools)

    async def model(state: State):
        result = await llm_with_tools.ainvoke(state["messages"])
        return {"messages": [result]}

    async def tools_router(state: State):
        last_message = state["messages"][-1]
        if hasattr(last_message, "tool_calls") and len(last_message.tool_calls) > 0:
            return "tool_node"
        return END

    async def tool_node(state: State):
        tool_calls = state["messages"][-1].tool_calls
        tool_messages = []
        for tool_call in tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_id = tool_call["id"]

            if tool_name == SEARCH_TOOL_NAME:
                search_results = await search_tool.ainvoke(tool_args)
                tool_message = ToolMessage(
                    content=str(search_results),
                    tool_call_id=tool_id,
                    name=tool_name,
                )
                tool_messages.append(tool_message)

        return {"messages": tool_messages}

    graph_builder = StateGraph(State)
    graph_builder.add_node("model", model)
    graph_builder.add_node("tool_node", tool_node)
    graph_builder.set_entry_point("model")
    graph_builder.add_conditional_edges("model", tools_router)
    graph_builder.add_edge("tool_node", "model")

    graph = graph_builder.compile(checkpointer=memory)
    return graph


_GRAPH = _build_graph()


def get_graph():
    return _GRAPH


