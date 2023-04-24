from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    HumanMessage,
    SystemMessage
)

chat = ChatOpenAI(temperature=0)

# result = chat([HumanMessage(content="Translate this sentence from English to French. I love programming.")])
# print(result)
# # -> AIMessage(content="J'aime programmer.", additional_kwargs={})
#
# messages = [
#     SystemMessage(content="You are a helpful assistant that translates English to French."),
#     HumanMessage(content="Translate this sentence from English to French. I love programming.")
# ]
# result = chat(messages)
# print(result)
# # -> AIMessage(content="J'aime programmer.", additional_kwargs={})

system_message = "You are a helpful assistant called 'Omega' that writes image processing or image analysis functions in python." \
                 "The returned python function should have signature: " \
                 "'apply(array_input: Array) ->Array' (Array is the numpy array type)." \
                 "The function should work on 2D or 3D images. " \
                 "The function should be self contained in the sense that should not require any precomputation. " \
                 "Any standard python library like scikit-image, scikit-learn, scipy, or other similar popular libraries can be used. " \
                 "Response should be just the code with minimal comments."

prompt = "Write a function that denoises an image using block matching pursuit. "

messages = [
    SystemMessage(content=""),
    HumanMessage(content=prompt)
]
result = chat(messages)
print(result.content)
