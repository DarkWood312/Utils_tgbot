from dataclasses import dataclass
from typing import Any, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, registry, Mapped, mapped_column
from sqlalchemy import Column, Integer, String, Boolean, select, update, insert, BigInteger, Text

Base = declarative_base()
mapper_registry = registry()
template_metadata = mapper_registry.metadata


@mapper_registry.mapped
@dataclass
class User:
    __tablename__ = 'users'
    __sa_dataclass_metadata_key = 'sa'

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    videoquality: Mapped[str] = mapped_column(Text, default='1080')
    audioformat: Mapped[str] = mapped_column(Text, default='mp3')
    audiobitrate: Mapped[str] = mapped_column(Text, default='128')
    filenamestyle: Mapped[str] = mapped_column(Text, default='classic')
    downloadmode: Mapped[str] = mapped_column(Text, default='auto')
    youtubevideocodec: Mapped[str] = mapped_column(Text, default='h264')
    youtubedublang: Mapped[str] = mapped_column(Text, default='ru')
    alwaysproxy: Mapped[bool] = mapped_column(Boolean, default=False)
    disablemetadata: Mapped[bool] = mapped_column(Boolean, default=False)
    tiktokfullaudio: Mapped[bool] = mapped_column(Boolean, default=False)
    tiktokh265: Mapped[bool] = mapped_column(Boolean, default=False)
    twittergif: Mapped[bool] = mapped_column(Boolean, default=False)
    youtubehls: Mapped[bool] = mapped_column(Boolean, default=False)


class DB:
    def __init__(
        self,
        user: str,
        password: str,
        host: str,
        port: int,
        database: str,
        echo: bool = False,
    ):
        url = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}"
        self.engine = create_async_engine(url, echo=echo)
        self.async_session = async_sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
            class_=AsyncSession,
        )

    async def __aenter__(self) -> AsyncSession:
        self.session: AsyncSession = self.async_session()
        return self.session

    async def __aexit__(
        self, exc_type, exc_val, exc_tb
    ):
        await self.session.close()

    async def get_user(self, user_id: int) -> Optional[User]:
        async with self.async_session() as session:
            result = await session.execute(
                select(User).where(User.user_id == user_id)
            )
            user_obj = result.scalar_one_or_none()
            return user_obj

    async def get_user_settings(self, user_id: int) -> Dict[str, Any]:
        async with self.async_session() as session:
            result = await session.execute(
                select(
                    User.videoquality,
                    User.audioformat,
                    User.audiobitrate,
                    User.filenamestyle,
                    User.downloadmode,
                    User.youtubevideocodec,
                    User.youtubedublang,
                    User.alwaysproxy,
                    User.disablemetadata,
                    User.tiktokfullaudio,
                    User.tiktokh265,
                    User.twittergif,
                    User.youtubehls,
                ).where(User.user_id == user_id)
            )

            values = result.first()
            # return values


        if not values:
            return {}

        (
            videoquality,
            audioformat,
            audiobitrate,
            filenamestyle,
            downloadmode,
            youtubevideocodec,
            youtubedublang,
            alwaysproxy,
            disablemetadata,
            tiktokfullaudio,
            tiktokh265,
            twittergif,
            youtubehls,
        ) = values

        return {
            'videoQuality': videoquality,
            'audioFormat': audioformat,
            'audioBitrate': audiobitrate,
            'filenameStyle': filenamestyle,
            'downloadMode': downloadmode,
            'youtubeVideoCodec': youtubevideocodec,
            'youtubeDubLang': youtubedublang,
            'alwaysProxy': alwaysproxy,
            'disableMetadata': disablemetadata,
            'tiktokFullAudio': tiktokfullaudio,
            'tiktokH265': tiktokh265,
            'twitterGif': twittergif,
            'youtubeHLS': youtubehls,
        }

    async def add_user(self, user_id: int) -> None:
        async with self.async_session() as session:
            stmt = insert(User).values(user_id=user_id)
            await session.execute(stmt)
            await session.commit()

    async def change_user_setting(
        self, user_id: int, name: str, value: Any
    ) -> None:
        async with self.async_session() as session:
            stmt = update(User).where(User.user_id == user_id).values({name: value})
            await session.execute(stmt)
            await session.commit()

    async def create_db(self) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(template_metadata.create_all)



