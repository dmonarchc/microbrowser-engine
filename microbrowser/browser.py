def show(body):
    in_tag = False
    i = 0

    while i < len(body):
        if body[i] == "<":
            in_tag = True
            i += 1
        elif body[i] == ">":
            in_tag = False
            i += 1
        elif not in_tag and body[i:i+4] == "&lt;":
            print("<", end="")
            i += 4
        elif not in_tag and body[i:i+4] == "&gt;":
            print(">", end="")
            i += 4
        elif not in_tag:
            print(body[i], end="")
            i += 1
        else:
            i += 1

def load(url):
    body = url.request()

    if url.view_source:
        print(body)
    else:
        show(body)

if __name__ == "__main__":
    import sys
    load(URL(sys.argv[1]))
