from dataclasses import dataclass
from typing import Literal

import requests

@dataclass(frozen=True)
class DownloadResponse:
    url: str
    filename: str

def download(url: str, api_key: str,
             videoQuality: Literal[144, 360, 720, 1080, 1440, 2160, 4320, 'max'] = None,
             audioFormat: Literal['best', 'mp3', 'opus', 'ogg', 'wav'] = None,
             audioBitrate: Literal[320, 256, 128, 96, 64, 8] = None,
             filenameStyle: Literal['classic', 'pretty', 'basic', 'nerdy'] = None,
             downloadMode: Literal['auto', 'audio', 'mute'] = None,
             youtubeVideoCodec: Literal['h264', 'av1', 'vp9'] = None,
             youtubeDubLang: str = 'ru',
             tiktokFullAudio: bool = None,
             tiktokH265: bool = None,
             twitterGif: bool = None,
             youtubeHLS: bool = None) -> DownloadResponse | dict:
    kwargs = {k: v for k, v in locals().items() if v is not None}
    r = requests.post("https://dl.dwip.pro", headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'User-Agent': "Mozilla/5.0 (X11; Linux x86_64; rv:131.0) Gecko/20100101 Firefox/131.0"}, json={'url': "https://www.youtube.com/watch?v=VQ_-A1BDCH0"})
    response = r.json()
    if response['status'] != 'tunnel' or response['status'] != 'redirect':
        return
    dresponse = DownloadResponse(url=response['url'], filename=response['filename'])

    file = requests.get(dresponse).content
    return file


print(download('https://vk.com/clip-1236_456240241', 'edc7710c-c140-4268-b794-5da821400510'))