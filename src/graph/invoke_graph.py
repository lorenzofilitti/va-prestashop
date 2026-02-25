from typing import Any

from conversation.conversation import Message
from graph.create_graph import build_graph
from llms.base_llm import AgentState
from storage.redis_db import RedisDB

def invoke_graph(
        user_query: str,
        session_id: str,
        user_id: str,
):
    # initialize DB
    db = RedisDB()

    conversation_history = []
    if not bool(db.client.exists(f"{session_id}:messages")):
        db.create_conversation(
            conversation_id=session_id,
            user_id=user_id
        )
    else:
        # retrieve conversation history
        conversation_history = db.get_conversation_by_id(session_id)

    # add user message to conversation on the DB
    db.update_conversation(
        message=Message(
            conversation_id=session_id,
            author="user",
            message=user_query
        )
    )

    # initialize graph and state
    graph = build_graph()

    default_state = AgentState(
        user_query=user_query,
        conversation_history=conversation_history,
        search_query=None,
        route=None,
        instruction=None,
        cart_confirmed=False,
        cart_populated=False,
    )

    final_state: dict[str, Any] = graph.invoke(default_state)
    final_answer = final_state.get("final_answer", "")
    breakpoint()

    # add assistant message to conversation on the DB
    db.update_conversation(
        message=Message(
            conversation_id=session_id,
            author="assistant",
            message=final_answer
        )
    )

    return final_answer



if __name__ == "__main__":
    ass = invoke_graph(
        "Ciao chi sei?",
        "prova3",
        "Lorenzo"
    )

    print(ass)