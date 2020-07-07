from whatthelang import WhatTheLang

def detect(text):
    wtl = WhatTheLang()
    lang = wtl.predict_lang(text)
    return lang

result = detect("Reparar tu smartphone o instalarle una ROM será delito en México: la nueva ley que protege los candados digitales, explicada") # check_lang(url)
print(result)
