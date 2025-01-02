from collections.abc import Coroutine
from typing import Any

import asyncpg


class DB:
    def __init__(self, host, port, user, password, database):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database

    async def __aenter__(self):
        self.conn = await asyncpg.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                     database=self.database)
        return self.conn

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.conn.close()

    async def cursor(self):
        cursor = await asyncpg.connect(**self.conn_kwargs)
        return cursor

    @property
    def conn_kwargs(self):
        return dict(host=self.host, port=self.port, user=self.user, password=self.password, database=self.database)

    async def get_user_settings(self, user_id: int) -> dict[str, Any]:
        async with self as conn:
            values = await conn.fetch('SELECT videoquality, audioformat, audiobitrate, filenamestyle, downloadmode, '
                             'youtubevideocodec, youtubedublang, alwaysproxy, disablemetadata, tiktokfullaudio, '
                             'tiktokh265, twittergif, youtubehls from users where user_id = $1', user_id)
        values = values[0]
        return {
            'videoQuality': values[0],
            'audioFormat': values[1],
            'audioBitrate': values[2],
            'filenameStyle': values[3],
            'downloadMode': values[4],
            'youtubeVideoCodec': values[5],
            'youtubeDubLang': values[6],
            'alwaysProxy': values[7],
            'disableMetadata': values[8],
            'tiktokFullAudio': values[9],
            'tiktokH265': values[10],
            'twitterGif': values[11],
            'youtubeHLS': values[12]
        }
        # return dict(values.items())

    async def add_user(self, user_id: int):
        async with self as conn:
            await conn.execute("INSERT INTO users VALUES ($1)", user_id)

    async def change_user_setting(self, user_id: int, name: str, value):
        async with self as conn:
            await conn.execute(f"UPDATE users SET {name} = $1 WHERE user_id = $2", value, user_id)
