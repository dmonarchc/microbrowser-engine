import socket
import ssl


class URL:
    def __init__(self, url):
        
        if url.startswith("view-source:"):
            self.view_source = True
            url = url[len("view-source:"):]
        else:
            self.view_source = False

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
            url = url + "/"

        self.host, url = url.split("/", 1)
        self.path = "/" + url

        if self.scheme == "http":
            self.port = 80
        elif self.scheme == "https":
            self.port = 443

        if ":" in self.host:
            self.host, port = self.host.split(":", 1)
            self.port = int(port)

    def request(self):
        if self.scheme == "data":
            return self.path

        if self.scheme == "file":
            path = self.path

            # Compatibilidad Windows:
            # file:///C:/Users/... -> C:/Users/...
            if path.startswith("/") and len(path) > 2 and path[2] == ":":
                path = path[1:]

            with open(path, "r", encoding="utf8") as f:
                return f.read()

        s = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP,
        )

        s.connect((self.host, self.port))

        if self.scheme == "https":
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(s, server_hostname=self.host)

        headers = {
            "Host": self.host,
            "Connection": "close",
            "User-Agent": "MicroBrowser/0.1",
        }

        request = "GET {} HTTP/1.1\r\n".format(self.path)

        for header, value in headers.items():
            request += "{}: {}\r\n".format(header, value)

        request += "\r\n"

        s.send(request.encode("utf8"))

        response = s.makefile(
            "r",
            encoding="utf8",
            newline="\r\n"
        )

        statusline = response.readline()
        version, status, explanation = statusline.split(" ", 2)

        response_headers = {}

        while True:
            line = response.readline()

            if line == "\r\n":
                break

            header, value = line.split(":", 1)
            response_headers[header.casefold()] = value.strip()

        assert "transfer-encoding" not in response_headers
        assert "content-encoding" not in response_headers

        content = response.read()

        s.close()

        return content