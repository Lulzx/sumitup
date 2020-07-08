import requests
passage = "Aunt Jessie bought an ice cream"
question = "what did Aunt Jessie buy?"
data = {"model":"bidaf-elmo","passage": passage ,"question": question}
r = requests.post('https://demo.allennlp.org/api/bidaf-elmo/predict', json=data).json()
print(r["best_span_str"])