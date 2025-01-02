create table users
(
    user_id           bigint not null,
    is_admin          bool default false,
    videoQuality      text default '1080',
    audioFormat       text default 'mp3',
    audioBitrate      text default '128',
    filenameStyle     text default 'classic',
    downloadMode      text default 'auto',
    youtubeVideoCodec text default 'auto',
    youtubeDubLang    text default 'ru',
    alwaysProxy       bool default false,
    disableMetadata   bool default false,
    tiktokFullAudio   bool default false,
    tiktokH265        bool default false,
    twitterGif        bool default false,
    youtubeHLS        bool default false
);

