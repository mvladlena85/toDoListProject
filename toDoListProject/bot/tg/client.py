import json

import marshmallow_dataclass
import requests

from toDoListProject import settings
from toDoListProject.bot.tg.dc import GetUpdatesResponse, SendMessageResponse


class TgClient:
    def __init__(self, token: str | None = None):
        self.token = token if token else settings.BOT_TOKEN

    def get_url(self, method: str) -> str:
        return f"https://api.telegram.org/bot{self.token}/{method}"

    def get_updates(self, offset: int = 0, timeout: int = 60) -> GetUpdatesResponse:
        url = self.get_url('getUpdates')
        response = requests.get(url=url, params={'offset': offset, 'timeout': timeout})
        GetUpdatesResponseSchema = marshmallow_dataclass.class_schema(GetUpdatesResponse)
        return GetUpdatesResponseSchema().loads(json.dumps(response.json()))

    def send_message(self, chat_id: int, text: str) -> SendMessageResponse:
        url = self.get_url('sendMessage')
        response = requests.get(url=url, params={'chat_id': chat_id, 'text': text})
        SendMessageResponseSchema = marshmallow_dataclass.class_schema(SendMessageResponse)
        return SendMessageResponseSchema().loads(json.dumps(response.json()))
