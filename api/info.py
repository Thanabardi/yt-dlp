from http.server import BaseHTTPRequestHandler
import json
import yt_dlp


def video_info(platform, id):
    print("video_info function start")
    if platform == "youtube":
        url = f"https://www.youtube.com/watch?v={id}"
    else:
        raise ValueError('unsupported platform')
    ydl_opts = {"quiet": True, "no_warnings": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        print("video_info function end")
        return ydl.sanitize_info(info)


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        print("called")
        try:
            print("split query")
            query_str = self.path.split("?", 1)[1]
            query = dict(q.split("=") for q in query_str.split("&"))
        except:
            print("invalid parameters")
            self.send_error(422, "invalid parameters")
            return

        if "platform" not in query or "id" not in query:
            print("parameters not found")
            self.send_error(422, "invalid parameters")
            return

        try:
            print("called video_info")
            response = video_info(query["platform"], query["id"])
            print("video_info done")
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            print("write")
            self.wfile.write(json.dumps(response).encode('utf-8'))
        except Exception as e:
            print("some error")
            self.send_error(500, e)
        return
