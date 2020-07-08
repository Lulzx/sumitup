import spacy
from spacy_fastlang import LanguageDetector

nlp = spacy.load('en_core_web_sm')
nlp.add_pipe(LanguageDetector())
doc = nlp('Life is like a box of chocolates. You never know what you are gonna get.')

assert doc._.language == 'en'
assert doc._.language_score >= 0.8
