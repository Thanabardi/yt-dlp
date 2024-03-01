from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qsl, unquote
import json
import yt_dlp

DEFAULT_QUALITY = "1080"


def video_info(id, quality):
    ydl_opts = {"cachedir": False,
                "extract_flat": "in_playlist",
                "format": f"bestaudio[ext=webm]+bestvideo[height<={quality}][ext=webm]"}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(
            f"https://www.youtube.com/watch?v={id}", download=False)
        sanitized_info = ydl.sanitize_info(info)
        result = {
            "id": sanitized_info.get("id"),
            "url": sanitized_info.get("webpage_url"),
            "title": sanitized_info.get("title"),
            "thumbnail": sanitized_info.get("thumbnail"),
            "upload_date": sanitized_info.get("upload_date"),
            "channel": sanitized_info.get("channel"),
            "channel_id": sanitized_info.get("channel_id"),
            "channel_url": sanitized_info.get("channel_url"),
            "duration": sanitized_info.get("duration"),
            "description": sanitized_info.get("description"),
            "chapters": sanitized_info.get("chapters"),
            "audio_url": sanitized_info.get("requested_formats")[0].get("url"),
            "audio_format": sanitized_info.get("requested_formats")[0].get("format").split(" - ")[1],
            "video_url": sanitized_info.get("requested_formats")[1].get("url"),
            "video_format": sanitized_info.get("requested_formats")[1].get("format").split(" - ")[1],
            "type": "video",
        }
        return result


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = dict(parse_qsl(unquote(urlparse(self.path).query)))
        if "id" not in query:
            self.send_error(422, "missing parameter 'id'")
            return

        try:
            quality = DEFAULT_QUALITY
            if "quality" in query:
                quality = query.get("quality")
            response = video_info(query.get("id"), quality)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
        except Exception as e:
            self.send_error(500, e)
        return
