from http.server import BaseHTTPRequestHandler
import json
import yt_dlp
from datetime import datetime

DEFAULT_QUALITY = "1080"


def video_info(id, quality):
    ydl_opts = {"cachedir": False,
                "extract_flat": "in_playlist",
                "format": f"bestaudio[ext=webm]+bestvideo[height<={quality}][ext=webm]"}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(
            f"https://www.youtube.com/playlist?list={id}", download=False)
        sanitized_info = ydl.sanitize_info(info)
        videos = []
        for video in sanitized_info["entries"]:
            videos.append({
                "id": video["id"],
                "webpage_url": video["url"],
                "title": video["title"],
                "thumbnail": video["thumbnails"][-1]["url"],
                "channel": video["channel"],
                "channel_id": video["channel_id"],
                "channel_url": video["channel_url"],
                "duration": video["duration"],
            })
        result = {
            "id": sanitized_info["id"],
            "webpage_url": sanitized_info["webpage_url"],
            "title": sanitized_info["title"],
            "thumbnail": sanitized_info["thumbnails"][-2]["url"],
            "modified_date": sanitized_info["modified_date"],
            "playlist_count": sanitized_info["playlist_count"],
            "channel": sanitized_info["channel"],
            "channel_id": sanitized_info["channel_id"],
            "channel_url": sanitized_info["channel_url"],
            "videos": videos,
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
