from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qsl, unquote
import json
import yt_dlp

# youtube search filter
VIDEO_FILTER = "EgIQAQ%253D%253D"
PLAYLIST_FILTER = "EgIQAw%253D%253D"
CHANNEL_FILTER = "EgIQAg%253D%253D"

# default playlist start and end
PLAYLIST_START = 1
PLAYLIST_AMOUNT = 10


def search(query, filter, playlist_start, playlist_amount):
    # search only playlist
    if filter == "playlist":
        filter = PLAYLIST_FILTER

        ydl_opts = {"cachedir": False,
                    "extract_flat": "in_playlist",
                    "playliststart": playlist_start,
                    "playlistend": playlist_start+playlist_amount}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(
                f"https://www.youtube.com/results?search_query={query}&sp={filter}", download=False)
            sanitized_result = ydl.sanitize_info(info)

        # get playlist info
        ydl_opts = {"cachedir": False,
                    "extract_flat": "in_playlist",
                    "playlistend": 0}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = []
            for playlist in sanitized_result.get("entries"):
                info = ydl.extract_info(
                    f"https://www.youtube.com/playlist?list={playlist.get('id')}", download=False)
                playlist_info = ydl.sanitize_info(info)
                result.append({
                    "id": playlist_info.get("id"),
                    "url": playlist_info.get("webpage_url"),
                    "title": playlist_info.get("title"),
                    "thumbnail": playlist_info.get("thumbnails")[-1].get("url"),
                    "modified_date": playlist_info.get("modified_date"),
                    "playlist_count": playlist_info.get("playlist_count"),
                    "channel": playlist_info.get("channel"),
                    "channel_id": playlist_info.get("channel_id"),
                    "channel_url": playlist_info.get("channel_url"),
                    "type": "playlist_info",
                })

    # search only channel
    elif filter == "channel":
        filter = CHANNEL_FILTER

        ydl_opts = {"cachedir": False,
                    "extract_flat": "in_playlist",
                    "playliststart": playlist_start,
                    "playlistend": playlist_start+playlist_amount}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(
                f"https://www.youtube.com/results?search_query={query}&sp={filter}", download=False)
            sanitized_result = ydl.sanitize_info(info)
            result = []
            for channel in sanitized_result.get("entries"):
                result.append({
                    "id": channel.get("id"),
                    "url": channel.get("url"),
                    "title": channel.get("title"),
                    "avatar": "https:"+channel.get("thumbnails")[-1].get("url"),
                    "channel": channel.get("channel"),
                    "channel_id": channel.get("channel_id"),
                    "channel_url": channel.get("channel_url"),
                    "followers": channel.get("channel_follower_count"),
                    "type": "channel_info",
                })

    # search only video
    else:
        ydl_opts = {"cachedir": False,
                    "extract_flat": "in_playlist"}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(
                f"ytsearch30:{query}", download=False)
            sanitized_result = ydl.sanitize_info(info)
            result = []
            for video in sanitized_result.get("entries"):
                # ignore youtube shorts
                if "/shorts/" in video.get("url"):
                    continue
                result.append({
                    "id": video.get("id"),
                    "url": video.get("url"),
                    "title": video.get("title"),
                    "thumbnail": video.get("thumbnails")[-1].get("url"),
                    "channel": video.get("channel"),
                    "channel_id": video.get("channel_id"),
                    "channel_url": video.get("channel_url"),
                    "duration": video.get("duration"),
                    "type": "video_info",
                })
    return result


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = dict(parse_qsl(unquote(urlparse(self.path).query)))
        if "query" not in query:
            self.send_error(422, "missing parameter 'query'")
            return

        try:
            playlist_start = query.get("playlist_start")
            playlist_amount = query.get("playlist_amount")
            if playlist_start is None or int(playlist_start) <= 0:
                playlist_start = PLAYLIST_START
            if playlist_amount is None or int(playlist_amount) <= 0:
                playlist_amount = PLAYLIST_AMOUNT
        except Exception:
            self.send_error(
                422, "invalid parameter type in playlist_start or playlist_amount")
            return

        try:
            filter = query.get("filter")
            response = search(query.get("query"), filter,
                              int(playlist_start), int(playlist_amount))
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
        except Exception as e:
            self.send_error(500, e)
        return
