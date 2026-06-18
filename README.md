# MicroBrowser Engine

A lightweight browser engine implemented in Python to explore how web browsers communicate over HTTP, retrieve documents, process responses, and render content.

This project focuses on understanding browser internals by implementing networking, resource loading, caching, compression handling, and content rendering from first principles.

---

## Features

### Networking

- HTTP/1.1 support
- HTTPS support
- Custom request headers
- User-Agent support
- Keep-Alive connections
- Socket reuse between requests

### URL Schemes

- HTTP URLs
- HTTPS URLs
- Local File URLs (`file://`)
- Data URLs (`data:`)
- View Source URLs (`view-source:`)

### HTTP Processing

- Redirect handling (3xx responses)
- Response caching
- Cache-Control support
- Gzip decompression
- Chunked transfer decoding
- Content-Length handling

### Rendering

- Basic HTML text extraction
- HTML entity decoding
- Source code viewing mode

---

## Project Structure

```text
microbrowser-engine/
│
├── microbrowser/
│   ├── __init__.py
│   ├── browser.py
│   └── url.py
│
├── examples/
│   └── test.html
│
├── main.py
└── README.md
```

## Running

```bash
python main.py http://info.cern.ch
```

```bash
python main.py file:///C:/path/to/file.html
```

```bash
python main.py "data:text/html,<h1>Hello World</h1>"
```

```bash
python main.py "view-source:http://info.cern.ch"
```

## Status

Current stage: Networking and document retrieval engine completed.

Next stage: HTML parsing and document tree construction.
