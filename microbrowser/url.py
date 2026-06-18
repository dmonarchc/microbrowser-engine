import socket
import ssl
import gzip
import time


CACHE = {}
SOCKETS = {}
MAX_REDIRECTS = 10


class URL:
    def __init__(self, url):
        self.view_source = False

        if url.startswith("view-source:"):
            self.view_source = True
            url = url[len("view-source:"):]

        if url.startswith("data:"):
            self.scheme = "data"
            self.path = url.split(",", 1)[1]
            return

        self.scheme, url = url.split("://", 1)
        assert self.scheme in ("http", "https", "file")

        if self.scheme == "file":
            self.path = url
            return

        if "/" not in url:
            url += "/"

        self.host, url = url.split("/", 1)
        self.path = "/" + url

        if self.scheme == "http":
            self.port = 80
        elif self.scheme == "https":
            self.port = 443

        if ":" in self.host:
            self.host, port = self.host.split(":", 1)
            self.port = int(port)

    def socket_key(self):
        return (self.scheme, self.host, self.port)

    def make_socket(self):
        s = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP,
        )

        s.connect((self.host, self.port))

        if self.scheme == "https":
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(s, server_hostname=self.host)

        return s

    def get_socket(self):
        key = self.socket_key()

        if key not in SOCKETS:
            SOCKETS[key] = self.make_socket()

        return SOCKETS[key]

    def request(self, redirect_count=0):
        if self.scheme == "data":
            return self.path

        if self.scheme == "file":
            path = self.path

            if path.startswith("/") and len(path) > 2 and path[2] == ":":
                path = path[1:]

            with open(path, "r", encoding="utf8") as f:
                return f.read()

        cache_key = self.cache_key()
        cached = CACHE.get(cache_key)

        if cached:
            expires_at, content = cached
            if time.time() < expires_at:
                return content
            else:
                del CACHE[cache_key]

        s = self.get_socket()

        headers = {
            "Host": self.host,
            "Connection": "keep-alive",
            "User-Agent": "MicroBrowser/0.1",
            "Accept-Encoding": "gzip",
        }

        request = "GET {} HTTP/1.1\r\n".format(self.path)

        for header, value in headers.items():
            request += "{}: {}\r\n".format(header, value)

        request += "\r\n"
        s.send(request.encode("utf8"))

        response = s.makefile("rb")

        statusline = response.readline().decode("utf8")
        version, status, explanation = statusline.split(" ", 2)
        status = int(status)

        response_headers = {}

        while True:
            line = response.readline()
            if line == b"\r\n":
                break

            line = line.decode("utf8")
            header, value = line.split(":", 1)
            response_headers[header.casefold()] = value.strip()

        if 300 <= status < 400:
            if redirect_count >= MAX_REDIRECTS:
                raise Exception("Too many redirects")

            location = response_headers["location"]

            if location.startswith("/"):
                location = "{}://{}{}".format(
                    self.scheme,
                    self.host,
                    location
                )

            return URL(location).request(redirect_count + 1)

        body = self.read_body(response, response_headers)

        if response_headers.get("content-encoding") == "gzip":
            body = gzip.decompress(body)

        content = body.decode("utf8", errors="replace")

        self.maybe_cache(cache_key, status, response_headers, content)

        return content

    def read_body(self, response, response_headers):
        if response_headers.get("transfer-encoding") == "chunked":
            body = b""

            while True:
                length_line = response.readline()
                length = int(length_line.strip(), 16)

                if length == 0:
                    response.readline()
                    break

                body += response.read(length)
                response.readline()

            return body

        if "content-length" in response_headers:
            length = int(response_headers["content-length"])
            return response.read(length)

        return response.read()

    def cache_key(self):
        return "{}://{}:{}{}".format(
            self.scheme,
            self.host,
            self.port,
            self.path
        )

    def maybe_cache(self, cache_key, status, response_headers, content):
        if status != 200:
            return

        cache_control = response_headers.get("cache-control")

        if not cache_control:
            return

        values = [value.strip() for value in cache_control.split(",")]

        max_age = None

        for value in values:
            if value == "no-store":
                return
            elif value.startswith("max-age="):
                max_age = int(value.split("=", 1)[1])
            else:
                return

        if max_age is not None:
            CACHE[cache_key] = (time.time() + max_age, content)