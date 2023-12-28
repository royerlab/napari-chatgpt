from openai import OpenAI

client = OpenAI()

model_lst = client.models.list()

print(model_lst)
