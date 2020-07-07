import requests

url = 'https://api.microlink.io?url=https%3A%2F%2Fexample.com&data.screenshot=true&data.meta=false'
response = requests.request("GET", url)

print(response.text)