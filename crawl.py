import sys
import requests
from lxml import etree
from io import StringIO
import re
import multiprocessing
import json

def fetch(item):
    try:
        r = requests.get(item['link'])
        r.encoding = "utf-8"
        root = etree.HTML(r.text)
        item['title'] = root.xpath("//table[@class=\"LinkTable\"]/tr/td/h1")[0].text.strip()
        item['image'] = root.xpath("//meta[@property=\"og:image\"]")[0].attrib['content'].strip()
        item['text'] = re.sub('(please only add this icon at the end of the article)','',''.join([s.strip() for s in root.xpath("//div[@id=\"masterContent\"]")[0].itertext()]).strip())
    except Exception as e:
        print("cannot parse %s" % (item['link']))
        raise
    return item


if __name__ == "__main__":
    d = sys.argv[1]
    r = requests.get('http://hk.apple.nextmedia.com/archive/index/%s/index/' % d)
    r.encoding = "utf-8"
    root = etree.HTML(r.text)
    links = []
    for a in root.xpath("//a"):
        href = a.attrib.get('href', '')
        print(href)
        m = re.match(r'(http|https)://hk.([A-z]+).appledaily.com(/[^/]*)/([^/]*)/([^/]*)/([^/]*)/([^/]*)', href)
        if m is not None:
            g = list(m.groups())
            if g[-2] == d and g[-1] != "index" and g[-3] != "index":
                links.append(href)
    items = [{'link': link, 'date': d} for link in list(set(links))]
    pool = multiprocessing.Pool()
    items = pool.map_async(fetch, items).get()
    with open(sys.argv[2], 'w') as f:
        f.write(json.dumps(items, indent=4))
