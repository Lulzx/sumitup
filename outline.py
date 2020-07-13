import requests
from bs4 import BeautifulSoup as bs
url = 'https://motherfuckingwebsite.com'
reqs = requests.get(url)
soup = bs(reqs.text, 'lxml')
headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
tag = lambda x: str(x)[:4]
l = list(map(tag, headings))
d = {}
for i in l:
    if i in d:
        d[i] += 1
    else:
        d[i] = 1
print(d)
print("Outline:")
outline = ""
for heading in headings:
    heading_text = heading.text.strip()
    if heading.name in ["h1", "h2"]:
        heading_text = f"{heading_text}"
    outline += int(heading.name[1:])*' ' + '- ' + heading_text + '\n'
print(outline)
