#!/usr/bin/env python3
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import html
import os
from pathlib import Path


ROOT = Path("/Users/**********/Public/VMShare")
PORT = 80


class ShareHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def list_directory(self, path):
        entries = sorted(Path(path).iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
        rows = []
        for entry in entries:
            name = entry.name + ("/" if entry.is_dir() else "")
            href = html.escape(name, quote=True)
            size = "-" if entry.is_dir() else f"{entry.stat().st_size:,} bytes"
            rows.append(
                f"<tr><td><a href='{href}'>{html.escape(name)}</a></td>"
                f"<td>{html.escape(size)}</td></tr>"
            )
        body = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>VMShare</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 32px; max-width: 900px; }}
    h1 {{ font-size: 28px; }}
    form {{ padding: 16px; border: 1px solid #ddd; border-radius: 8px; margin-bottom: 24px; }}
    table {{ border-collapse: collapse; width: 100%; }}
    td, th {{ border-bottom: 1px solid #eee; padding: 10px; text-align: left; }}
    button {{ padding: 8px 14px; }}
  </style>
</head>
<body>
  <h1>VMShare</h1>
  <form method="post" enctype="multipart/form-data">
    <input type="file" name="file" multiple>
    <button type="submit">上传到 Mac</button>
  </form>
  <table>
    <tr><th>文件</th><th>大小</th></tr>
    {''.join(rows)}
  </table>
</body>
</html>"""
        encoded = body.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        return self.wfile.write(encoded)

    def do_POST(self):
        content_type = self.headers.get("Content-Type", "")
        marker = "boundary="
        if marker not in content_type:
            self.send_error(400, "Missing multipart boundary")
            return

        boundary = ("--" + content_type.split(marker, 1)[1].strip().strip('"')).encode()
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length)

        for part in body.split(boundary):
            if b"Content-Disposition:" not in part:
                continue
            header_blob, _, payload = part.partition(b"\r\n\r\n")
            if not payload:
                continue
            disposition = header_blob.decode("utf-8", "ignore")
            token = 'filename="'
            if token not in disposition:
                continue
            filename = disposition.split(token, 1)[1].split('"', 1)[0]
            filename = os.path.basename(filename)
            if not filename:
                continue
            payload = payload.removesuffix(b"\r\n")
            payload = payload.removesuffix(b"--\r\n")
            target = ROOT / filename
            with target.open("wb") as out:
                out.write(payload)
        self.send_response(303)
        self.send_header("Location", "/")
        self.end_headers()


if __name__ == "__main__":
    ROOT.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(("0.0.0.0", PORT), ShareHandler)
    print(f"Serving {ROOT} at http://0.0.0.0:{PORT}", flush=True)
    server.serve_forever()
