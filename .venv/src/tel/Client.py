from telethon import TelegramClient
import ujson,asyncio,os
from backend.db import get_session
from backend.models import Config
from backend.views import ConfigView
from ui.component.ApiConfDialog import ApiConfDialog
from ui.component.SignInDialog import SignInDialog
from ui.component.MsgBox import warning
from util import get_conf_path
from ui.signal.Signal import Signal, get_global_signal

from PySide6.QtCore import QTimer

class Client:
    _client = None
    _is_authed = False
    def __init__(self):
        self._signal = get_global_signal()

    def __new__(cls, *args, **kwargs):
        if cls._client is None:
            cls._client = super().__new__(cls)
        return cls._client

    async def get(self):
        print('getClient')
        if not self._client or not self._is_authed:
            print('start')
            await self._initClient()
        print('finishGetClient')
        print('self._client', self._client)
        return self._client

    async def _initClient(self):
        print('_initClient')
        session = get_session()
        conf_view = ConfigView(session)
        api_conf = conf_view.get()
        api_id = api_conf.api_id
        api_hash = api_conf.api_hash
        if not api_id and not api_hash:
            self._signal.emit_conf_signal()
            return
        self._client = TelegramClient(get_conf_path("anon.session"), api_id, api_hash)
        await self._client.connect()
        if not await self._client.is_user_authorized():
            self._signal.emit_signIn_signal(self._client)
            return
        else:
            self._is_authed=True
        return self._client

    async def disconnect(self):
        if self._client and self._is_authed:
            await self._client.disconnect()

