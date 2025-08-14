from langchain_core.messages import AIMessageChunk


def serialise_ai_message_chunk(chunk) -> str:
    if isinstance(chunk, AIMessageChunk):
        return chunk.content
    raise TypeError(
        f"Object of type {type(chunk).__name__} is not correctly formatted for serialisation"
    )


