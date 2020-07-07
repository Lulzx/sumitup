# import requests
from langdetect import detect
# from lxml.html import fromstring


def check_lang(url):
	value = requests.get(url).text
	tree = fromstring(value)
	title = str(tree.findtext('.//title'))
	print(title)
	lang = detect(title) # translator.detect(title).lang
	return lang


url = "https://www.xataka.com.mx/legislacion-y-derechos/reparar-tu-smartphone-instalarle-rom-sera-delito-mexico-nueva-ley-que-proteje-candados-digitales-explicada" #input("Enter the link: ")
result = detect("Reparar tu smartphone o instalarle una ROM será delito en México: la nueva ley que protege los candados digitales, explicada") # check_lang(url)
print(result)