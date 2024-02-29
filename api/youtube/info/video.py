from http.server import BaseHTTPRequestHandler
import json
import yt_dlp
from datetime import datetime

DEFAULT_QUALITY = "1080"


def video_info(id, quality):
    ydl_opts = {"cachedir": False,
                "extract_flat": "in_playlist",
                "source_address": "::",
                "format": f"bestaudio[ext=webm]+bestvideo[height<={quality}][ext=webm]"}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(
            f"https://www.youtube.com/watch?v={id}", download=False)
        sanitized_info = ydl.sanitize_info(info)
        result = {
            "id": sanitized_info["id"],
            "webpage_url": sanitized_info["webpage_url"],
            "title": sanitized_info["title"],
            "thumbnail": sanitized_info["thumbnail"],
            "upload_date": sanitized_info["upload_date"],
            "channel": sanitized_info["channel"],
            "channel_id": sanitized_info["channel_id"],
            "channel_url": sanitized_info["channel_url"],
            "duration": sanitized_info["duration"],
            "audio_url": sanitized_info["requested_formats"][0]["url"],
            "audio_format": sanitized_info["requested_formats"][0]["format"].split(" - ")[1],
            "video_url": sanitized_info["requested_formats"][1]["url"],
            "video_format": sanitized_info["requested_formats"][1]["format"].split(" - ")[1],
            "lookup_timestamp": datetime.now().timestamp()
        }
        return result


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            query_str = self.path.split("?", 1)[1]
            query = dict(q.split("=") for q in query_str.split("&"))
        except:
            self.send_error(422, "invalid parameters")
            return

        if "id" not in query:
            self.send_error(422, "invalid parameters")
            return

        try:
            quality = DEFAULT_QUALITY
            if "quality" in query:
                quality = query["quality"]
            response = video_info(query["id"], quality)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
        except Exception as e:
            self.send_error(500, e)
        return
