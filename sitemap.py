def loc(x):
    return '<loc>' + x + '</loc>'

def indent(content):
    lines = content.split('\n')
    result = []
    for line in lines:
        result.append('    ' + line)
    return '\n'.join(result)

def tag(content, tag, attrib=None):
    if attrib:
        attrib = ' ' + attrib
    else:
        attrib = ''
    result = '<' + tag + attrib + '>\n'
    result += indent(content)
    result += '\n</' + tag + '>'
    return result

def url(content):
    return tag(content, 'url')

def urlset(content):
    return tag(content, 'urlset', 'xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"')

def sitemap(paths):
    lines = [url(loc(x)) for x in paths]
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + urlset('\n'.join(lines))

