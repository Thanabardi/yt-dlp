from http.server import BaseHTTPRequestHandler
import json
import yt_dlp


def video_info(platform, id):
    if platform == "youtube":
        url = f"https://www.youtube.com/watch?v={id}"
    else:
        raise ValueError('unsupported platform')

    with yt_dlp.YoutubeDL() as ydl:
        info = ydl.extract_info(url, download=False)
        return ydl.sanitize_info(info)


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            query_str = self.path.split("?", 1)[1]
            query = dict(q.split("=") for q in query_str.split("&"))
        except:
            self.send_error(422, "invalid parameters")
            return

        if "platform" not in query or "id" not in query:
            self.send_error(422, "invalid parameters")
            return

        try:
            response = video_info(query["platform"], query["id"])
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(bytes(json.dumps(response), 'utf-8'))
        except Exception as e:
            self.send_error(500, e)
        return
