import pyttsx3
engine = pyttsx3.init()
engine.save_to_file('this is pathetic sound of my voice', 'test.mp3')
engine.runAndWait()
