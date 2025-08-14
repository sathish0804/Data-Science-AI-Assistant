import json
from typing import AsyncIterator, Optional
from uuid import uuid4

from fastapi import Query
from langchain_core.messages import HumanMessage

from services.langgraph_service import SEARCH_TOOL_NAME, get_graph
from utils.serialization import serialise_ai_message_chunk


async def generate_chat_responses(
    message: str, checkpoint_id: Optional[str] = None
) -> AsyncIterator[str]:
    graph = get_graph()
    is_new_conversation = checkpoint_id is None

    if is_new_conversation:
        new_checkpoint_id = str(uuid4())
        config = {"configurable": {"thread_id": new_checkpoint_id}}
        events = graph.astream_events(
            {"messages": [HumanMessage(content=message)]},
            version="v2",
            config=config,
        )
        yield f"data: {{\"type\": \"checkpoint\", \"checkpoint_id\": \"{new_checkpoint_id}\"}}\n\n"
    else:
        config = {"configurable": {"thread_id": checkpoint_id}}
        events = graph.astream_events(
            {"messages": [HumanMessage(content=message)]},
            version="v2",
            config=config,
        )

    async for event in events:
        event_type = event["event"]

        if event_type == "on_chat_model_stream":
            chunk_content = serialise_ai_message_chunk(event["data"]["chunk"])
            safe_content = chunk_content.replace("'", "\\'").replace("\n", "\\n")
            yield f"data: {{\"type\": \"content\", \"content\": \"{safe_content}\"}}\n\n"

        elif event_type == "on_chat_model_end":
            tool_calls = (
                event["data"]["output"].tool_calls
                if hasattr(event["data"]["output"], "tool_calls")
                else []
            )
            search_calls = [
                call for call in tool_calls if call["name"] == SEARCH_TOOL_NAME
            ]
            if search_calls:
                search_query = search_calls[0]["args"].get("query", "")
                safe_query = (
                    search_query.replace('"', '\\"').replace("'", "\\'").replace("\n", "\\n")
                )
                yield f"data: {{\"type\": \"search_start\", \"query\": \"{safe_query}\"}}\n\n"

        elif event_type == "on_tool_end" and event["name"] == SEARCH_TOOL_NAME:
            output = event["data"]["output"]
            if isinstance(output, list):
                urls = []
                for item in output:
                    if isinstance(item, dict) and "url" in item:
                        urls.append(item["url"])
                urls_json = json.dumps(urls)
                yield f"data: {{\"type\": \"search_results\", \"urls\": {urls_json}}}\n\n"

    yield f"data: {{\"type\": \"end\"}}\n\n"


