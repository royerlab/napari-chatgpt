import base64
import openai
import os

from openai.resources.chat import Completions
from openai.types.chat import ChatCompletion

# Updated file path to a JPEG image
#image_path = "/Users/royer/Downloads/image.jpeg"
image_path = "/Users/royer/Downloads/python.png"

image_format = 'png'

# Read and encode the image in base64
with open(image_path, "rb") as image_file:
    encoded_image = base64.b64encode(image_file.read()).decode("utf-8")

# Craft the prompt for GPT
prompt_messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "Here is an image, can you describe it?"
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/{image_format};base64,{encoded_image}"
                }
            }
        ]
    }
]

# Send a request to GPT
params = {
    "model": "gpt-4-vision-preview",
    "messages": prompt_messages,
    #"api_key": ,
    # "response_format": {"type": "json_object"},  # Added response format
    #"headers": {"Openai-Version": "2020-11-07"},
    "max_tokens": 4096,
}

from openai import OpenAI
client = OpenAI()
completions = Completions(client)
result = completions.create(**params)
print(result.choices[0].message.content)
