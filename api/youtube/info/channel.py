from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qsl, unquote
import json
import yt_dlp

# youtube channel filter
VIDEO_FILTER = "videos"
PLAYLIST_FILTER = "playlists"

# default playlist start and end
PLAYLIST_START = 1
PLAYLIST_AMOUNT = 10


def channel_info(id, filter, playlist_start, playlist_amount):
    # get only channel's playlists
    if filter == "playlist":
        filter = PLAYLIST_FILTER

        ydl_opts = {"cachedir": False,
                    "extract_flat": "in_playlist",
                    "playliststart": playlist_start,
                    "playlistend": playlist_start+playlist_amount}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(
                f"https://www.youtube.com/channel/{id}/{filter}", download=False)
            sanitized_info = ydl.sanitize_info(info)

            # get playlist info
            ydl_opts = {"cachedir": False,
                        "extract_flat": "in_playlist",
                        "playlistend": 0}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                playlists = []
                for playlist in sanitized_info.get("entries"):
                    info = ydl.extract_info(
                        f"https://www.youtube.com/playlist?list={playlist.get('id')}", download=False)
                    playlist_info = ydl.sanitize_info(info)
                    playlist_dict = {
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
                    }
                    playlists.append(playlist_dict)
                result = {
                    "id": sanitized_info.get("id"),
                    "banner": sanitized_info.get("thumbnails")[-3].get("url"),
                    "avatar": sanitized_info.get("thumbnails")[-2].get("url"),
                    "channel": sanitized_info.get("channel"),
                    "channel_id": sanitized_info.get("channel_id"),
                    "channel_url": sanitized_info.get("channel_url"),
                    "followers": sanitized_info.get("channel_follower_count"),
                    "type": "channel",
                    "playlist": playlists,
                }

    # get only channel's videos
    else:
        filter = VIDEO_FILTER

        ydl_opts = {"cachedir": False,
                    "extract_flat": "in_playlist",
                    "playliststart": playlist_start,
                    "playlistend": playlist_start+playlist_amount}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(
                f"https://www.youtube.com/channel/{id}/{filter}", download=False)
            sanitized_info = ydl.sanitize_info(info)
            videos = []
            for video in sanitized_info.get("entries"):
                videos.append({
                    "id": video.get("id"),
                    "url": video.get("url"),
                    "title": video.get("title"),
                    "thumbnail": video.get("thumbnails")[-1].get("url"),
                    "channel": sanitized_info.get("channel"),
                    "channel_id": sanitized_info.get("channel_id"),
                    "channel_url": sanitized_info.get("channel_url"),
                    "duration": video.get("duration"),
                    "type": "video_info",
                })
            result = {
                "id": sanitized_info.get("id"),
                "banner": sanitized_info.get("thumbnails")[-3].get("url"),
                "avatar": sanitized_info.get("thumbnails")[-2].get("url"),
                "channel": sanitized_info.get("channel"),
                "channel_id": sanitized_info.get("channel_id"),
                "channel_url": sanitized_info.get("channel_url"),
                "followers": sanitized_info.get("channel_follower_count"),
                "type": "channel",
                "playlist": videos,
            }
    return result


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = dict(parse_qsl(unquote(urlparse(self.path).query)))
        if "id" not in query:
            self.send_error(422, "missing parameter 'id'")
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
            response = channel_info(
                query.get("id"), filter, int(playlist_start), int(playlist_amount))
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
        except Exception as e:
            self.send_error(500, e)
        return
