from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qsl, unquote
import json
import yt_dlp

# youtube search filter
VIDEO_FILTER = "EgIQAQ%253D%253D"
PLAYLIST_FILTER = "EgIQAw%253D%253D"


def search(query, filter):
    # search only playlist (10 result)
    if filter == "playlist":
        filter = PLAYLIST_FILTER

        ydl_opts = {"cachedir": False,
                    "extract_flat": "in_playlist",
                    "playlistend": 10}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(
                f"https://www.youtube.com/results?search_query={query}&sp={filter}", download=False)
            sanitized_result = ydl.sanitize_info(info)
        ydl_opts = {"cachedir": False,
                    "extract_flat": "in_playlist",
                    "playlistend": 0}

        # get playlist info
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = []
            for playlist in sanitized_result.get("entries"):
                info = ydl.extract_info(
                    f"https://www.youtube.com/playlist?list={playlist.get('id')}", download=False)
                playlist_info = ydl.sanitize_info(info)
                playlist_dict = {
                    "id": playlist_info.get("id"),
                    "webpage_url": playlist_info.get("webpage_url"),
                    "title": playlist_info.get("title"),
                    "thumbnail": playlist_info.get("thumbnails")[-1].get("url"),
                    "modified_date": playlist_info.get("modified_date"),
                    "playlist_count": playlist_info.get("playlist_count"),
                    "channel": playlist_info.get("channel"),
                    "channel_id": playlist_info.get("channel_id"),
                    "channel_url": playlist_info.get("channel_url"),
                    "type": "playlist_search",
                }
                result.append(playlist_dict)
    else:
        # search only video (up to 30 result)
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
                video_dict = {
                    "id": video.get("id"),
                    "webpage_url": video.get("url"),
                    "title": video.get("title"),
                    "thumbnail": video.get("thumbnails")[-1].get("url"),
                    "channel": video.get("channel"),
                    "channel_id": video.get("channel_id"),
                    "channel_url": video.get("channel_url"),
                    "duration": video.get("duration"),
                    "type": "video_search",
                }
                result.append(video_dict)
    return result


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = dict(parse_qsl(unquote(urlparse(self.path).query)))
        if "query" not in query:
            self.send_error(422, "missing parameter 'query'")
            return

        try:
            filter = query.get("filter")
            response = search(query.get("query"), filter)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
        except Exception as e:
            self.send_error(500, e)
        return
