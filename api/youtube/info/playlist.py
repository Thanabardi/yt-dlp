from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qsl, unquote
import json
import yt_dlp


def playlist_info(id):
    ydl_opts = {"cachedir": False,
                "extract_flat": "in_playlist"}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(
            f"https://www.youtube.com/playlist?list={id}", download=False)
        sanitized_info = ydl.sanitize_info(info)
        videos = []
        for video in sanitized_info.get("entries"):
            videos.append({
                "id": video.get("id"),
                "url": video.get("url"),
                "title": video.get("title"),
                "thumbnail": video.get("thumbnails")[-1].get("url"),
                "channel": video.get("channel"),
                "channel_id": video.get("channel_id"),
                "channel_url": video.get("channel_url"),
                "duration": video.get("duration"),
            })

        try:
            thumbnail = sanitized_info.get("thumbnails")[-2].get("url")
        except IndexError:
            thumbnail = sanitized_info.get("thumbnails")[0].get("url")
        result = {
            "id": sanitized_info.get("id"),
            "url": sanitized_info.get("webpage_url"),
            "title": sanitized_info.get("title"),
            "thumbnail": thumbnail,
            "modified_date": sanitized_info.get("modified_date"),
            "playlist_count": sanitized_info.get("playlist_count"),
            "channel": sanitized_info.get("channel"),
            "channel_id": sanitized_info.get("channel_id"),
            "channel_url": sanitized_info.get("channel_url"),
            "type": "playlist",
            "videos": videos,
        }
        return result


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = dict(parse_qsl(unquote(urlparse(self.path).query)))
        if "id" not in query:
            self.send_error(422, "missing parameter 'id'")
            return

        try:
            response = playlist_info(query.get("id"))
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
        except Exception as e:
            self.send_error(500, e)
        return
