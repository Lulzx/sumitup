import requests
from bs4 import BeautifulSoup
url = 'https://www.smashingmagazine.com/2020/03/introduction-alpinejs-javascript-framework/'
reqs = requests.get(url)
soup = bs(reqs.text, 'lxml')
print("Outline:")
for heading in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
    print(int(heading.name[1:])*' ' + '- ' + heading.text.strip())