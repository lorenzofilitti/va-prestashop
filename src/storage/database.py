import os
import uuid

from sqlalchemy import create_engine, text
from functools import wraps

from conversation.conversation import ConversationManager, Message

def while_connected(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        with self._engine.begin() as connection:
            return func(self, connection, *args, **kwargs)
    return wrapper

#----------------------------------------------------------

class SQLDatabase:
    def __init__(self):
        self.conversation_manager = ConversationManager()
        self._endpoint = os.environ.get("SQL_DB_ENDPOINT")
        self._engine = create_engine(self._endpoint)


    @while_connected
    def insert_conversation_message(self, connection, message: Message) -> None:
        query: str = f"""
        INSERT into conversations VALUES (:conversation_id, :message_id, :role, :message, :created_at, :turn) 
        """
        connection.execute(text(query), {"conversation_id": message.conversation_id, "message_id": message.message_id,
                                        "role": message.role, "message": message.message,
                                        "created_at": message.created_at, "turn": message.turn})

    @while_connected
    def get_conversation_history(self, connection, conversation_id: str) -> list[str]:
        query: str = f"""
            SELECT role, message FROM conversations WHERE conversation_id = {conversation_id} ORDER BY turn
            """
        result = connection.execute(text(query))
        formatted_conversation = self.conversation_manager.format_conversation_history(result.all())
        return formatted_conversation



if __name__=="__main__":
    sql = SQLDatabase()
    sql.insert_conversation_message(sql.conversation_manager.parse_message(
        conversation_id=str(uuid.uuid4()),
        role="user",
        message="Ciao",
        turn=1,
    ))