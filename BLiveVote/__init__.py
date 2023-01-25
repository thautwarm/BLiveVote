from __future__ import annotations
import asyncio
import dataset
import typing
import re
import json
import os
import pathlib
import sys
from collections import deque
from datetime import datetime
from loguru import logger
from dataclasses import dataclass
from BLiveVote.ui import UI, SettingOption
from BLiveVote.blivedm import BLiveClient, BaseHandler, DanmakuMessage

__all__ = ['App']

_D = typing.TypeVar('_D')


@dataclass
class Point(typing.Generic[_D]):
    start: float
    data: _D

class Message(typing.TypedDict):
    msg: str
    uid: int
    uname: str
    user_level: int
    timestamp: float

async def repeat_task(task: typing.Callable[[], typing.Awaitable[typing.Any]], interval: float = 0.1):
    while True:
        await task()
        await asyncio.sleep(interval)

class BLiveVoteHandler(BaseHandler):
    def __init__(
        self,
        positive_pattern: str,
        load_settings: typing.Callable[[], list[SettingOption]],
        database_path: str,
        set_state: typing.Callable[[dict[str, int]], None],
    ) -> None:
        super().__init__()
        self._db = dataset.connect('sqlite:///' + database_path)
        self._local = typing.cast('list[Message]', list(map(dict, self.database.all())))
        self._cache: deque[Message] = deque()
        self._set_state = set_state
        self._load_settings = load_settings
        self._positive_pattern = re.compile(positive_pattern)

    @property
    def database(self):
        table: dataset.Table = typing.cast(dataset.Table, self._db['danmaku'])
        return table

    async def _on_heartbeat(self, client: BLiveClient, message):
        print(f'[{client.room_id}] 当前人气值：{message.popularity}')

    async def _on_gift(self, client: BLiveClient, message):
        pass

    async def _on_buy_guard(self, client: BLiveClient, message):
        pass

    async def _on_super_chat(self, client, message):
        pass

    async def _on_danmaku(self, client: BLiveClient, message: DanmakuMessage):

        if message.dm_type != 0:
            # not text message
            return
        record = Message(uname=message.uname, uid=message.uid, msg=message.msg, timestamp=message.timestamp / 1_000, user_level=message.user_level)

        t = datetime.fromtimestamp(record["timestamp"])
        logger.debug(f'[{t}] record: {record}')
        self._local.append(record)
        self._cache.append(record)

    async def persistent_job(self: BLiveVoteHandler):
        table = self.database
        while self._cache:
            record = self._cache.pop()
            table.insert(record)

            await asyncio.sleep(0)

    async def update_job(self: BLiveVoteHandler):
        count: dict = {}

        j = 0
        settings = self._load_settings()
        if not settings:
            return

        option = settings[j]

        def get_new_start():
            nonlocal j
            if j < len(settings) - 1:
                return settings[j + 1]["start"]
            return float('inf')

        new_start = get_new_start()


        for i in range(len(self._local)):
            msg = self._local[i]
            while msg["timestamp"] > new_start:
                j += 1
                option = settings[j]
                new_start = get_new_start()

            key = option["option"]
            count.setdefault(key, 0)
            if self._positive_pattern.match(msg["msg"]):
                count[key] += 1

            await asyncio.sleep(0)

        self._set_state(count)

class App:
    def __init__(self, room_id: int, positive_pattern: str, database_path: str = ":memory:"):
        self.room_id = room_id
        self.stats: dict[str, int] = {}

        def set_state(d: dict[str, int]):
            self.stats = d

        settings: list[SettingOption] = []

        self.handler = BLiveVoteHandler(positive_pattern, lambda: settings.copy(), database_path, set_state)
        self.client = BLiveClient(room_id, ssl=True)
        self.client.add_handler(self.handler)
        self.ui = UI(settings, [], lambda: self.stats)

    async def _run_main(self):
        self.client.start()
        try:
            await self.ui.async_serve()
            self.client.stop()
            await self.client.join()
        finally:
            await self.client.stop_and_close()

    async def run(self):
        co2 = self._run_main()
        co3 = asyncio.ensure_future(repeat_task(self.handler.persistent_job))
        co4 = asyncio.ensure_future(repeat_task(self.handler.update_job, 1.0))
        await asyncio.gather(co2, co3, co4)
