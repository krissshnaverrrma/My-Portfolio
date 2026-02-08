import markdown


def markdown_filter(text):
    if text:
        return markdown.markdown(text, extensions=['fenced_code', 'codehilite'])
    return ""
