import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Optional
import logging

from storage import Message

import redis
from redis.exceptions import RedisError, ConnectionError, TimeoutError
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class RedisDB:
    def __init__(self):
        self.client = redis.Redis(
            host=os.environ.get("HOST"),
            port=int(os.environ.get("PORT")),
            username=os.environ.get("USERNAME"),
            password=os.environ.get("PASSWORD"),
            decode_responses=True
        )

    @retry(stop=stop_after_attempt(2), wait=wait_fixed(2),
           retry=retry_if_exception_type((TimeoutError, ConnectionError)))
    def create_conversation(self, conversation_id: str, user_id: str, key_expiration_days: int = 7) -> None:
        """
        Method sets a document in the Redis DB
        :param user_id: (str) user_id of the conversation
        :param conversation_id: (str) id of the conversation
        :param key_expiration_days: (int) number of days after which the conversation expires
        :return: True if document was successfully set, False otherwise
        """
        timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        try:
            # set messages
            self.client.set(f"{conversation_id}:messages", json.dumps([]))
            self.client.expire(f"{conversation_id}:messages", key_expiration_days * 86400)

            # set metadata
            self.client.hset(
                name=f"{conversation_id}:metadata",
                mapping={
                    "user_id": user_id,
                    "created_at": timestamp,
                    "updated_at": timestamp,
                    "message_count": 0
                }
            )
            self.client.expire(f"{conversation_id}:metadata", key_expiration_days * 86400)
            self.client.close()
            logging.info(f"Created conversation {conversation_id} for user {user_id}")
        except RedisError as e:
            logging.error(f"Unexpected Redis error while creating conversation: {e} -> {sys.exc_info()[0]}")
            return
        except Exception as e:
            logging.error(f"Unexpected error while creating conversation: {e} -> {sys.exc_info()[0]}")
            return

    @retry(stop=stop_after_attempt(2), wait=wait_fixed(2),
           retry=retry_if_exception_type((TimeoutError, ConnectionError)))
    def update_conversation(self, message: Message) -> None:
        """
        Method to update a conversation stored in the Redis DB
        :param message: (Message) the message to update the conversation with
        :return:
        """
        messages_key = f"{message.conversation_id}:messages"
        metadata_key = f"{message.conversation_id}:metadata"
        try:
            conversation: List[Dict[str, str]] = json.loads(self.client.get(message.conversation_id) or "[]")
            conversation.append({"author": message.author, "message": message.message})

            self.client.set(messages_key, json.dumps(conversation))
            self.client.hset(metadata_key, "updated_at", datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
            self.client.hincrby(metadata_key, "message_count", 1)
            self.client.close()
            logging.info(f"Updated conversation {message.conversation_id}")
        except RedisError as e:
            logging.error(f"Unexpected Redis error while updating conversation: {e} -> {sys.exc_info()[0]}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error while updating conversation: {e} -> {sys.exc_info()[0]}")
            return

    @retry(stop=stop_after_attempt(2), wait=wait_fixed(2),
           retry=retry_if_exception_type((TimeoutError, ConnectionError)))
    def get_conversation_by_id(self, conversation_id: str) -> Optional[List[Dict[str, str]]]:
        """
        Method to get a conversation stored in the Redis DB
        :param conversation_id: (str) id of the conversation
        :return: the list of messages exchanged in the specified conversation
        """
        conversation: List[Dict[str, str]]
        try:
             conversation = json.loads(self.client.get(f"{conversation_id}:messages") or "[]")
             self.client.close()
             if conversation:
                logging.info(f"Retrieved conversation '{conversation_id}'")
             else:
                 logging.info(f"Retrieved empty conversation '{conversation_id}'")
        except RedisError as e:
            logging.error(f"Unexpected Redis error while retrieving conversation: {e} -> {sys.exc_info()[0]}")
            conversation = []
        except Exception as e:
            logging.error(f"Unexpected error while retrieving conversation: {e} -> {sys.exc_info()[0]}")
            conversation = []

        return conversation

    @retry(stop=stop_after_attempt(2), wait=wait_fixed(2),
           retry=retry_if_exception_type((TimeoutError, ConnectionError)))
    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Method to delete a conversation stored in the Redis DB
        :param conversation_id: (str) id of the conversation
        :return: True if conversation was successfully deleted, False otherwise
        """
        messages_key = f"{conversation_id}:messages"
        metadata_key = f"{conversation_id}:meta"
        try:
            deleted: bool = bool(self.client.delete(messages_key, metadata_key))
            self.client.close()
            logging.info(f"Deleted conversation {conversation_id} -> {deleted} ")
        except RedisError as e:
            logging.error(f"Unexpected Redis error while deleting conversation: {e} -> {sys.exc_info()[0]}")
            deleted = False
        except Exception as e:
            logging.error(f"Unexpected error while deleting conversation: {e} -> {sys.exc_info()[0]}")
            deleted = False

        return deleted

    @retry(stop=stop_after_attempt(2), wait=wait_fixed(2),
           retry=retry_if_exception_type((TimeoutError, ConnectionError)))
    def get_conversation_metadata(self, conversation_id: str) -> Optional[Dict[str, str]]:
        """
        Method to get a conversation's metadata stored in the Redis DB
        :param conversation_id: (str) id of the conversation
        :return: dictionary containing the conversation's metadata
        """
        try:
            meta: Dict[str, str] = self.client.hgetall(f"{conversation_id}:metadata")
            self.client.close()
        except RedisError as e:
            logging.error(f"Unexpected Redis error while retrieving metadata: {e} -> {sys.exc_info()[0]}")
            meta = {}
        except Exception as e:
            logging.error(f"Unexpected error while retrieving metadata: {e} -> {sys.exc_info()[0]}")
            meta = {}

        return meta




