import spacy
nlp = spacy.load("en_core_web_sm")
doc = nlp("A new world is being born. I just hope I live to see it, and that there's room in it for someone like me to exist.")
print([(w.text, w.pos_) for w in doc])
