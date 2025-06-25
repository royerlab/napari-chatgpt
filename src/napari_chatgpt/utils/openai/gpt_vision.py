from arbol import asection, aprint

from napari_chatgpt.utils.api_keys.api_key import set_api_key
from napari_chatgpt.utils.openai.model_list import get_openai_model_list


def is_gpt_vision_available(vision_model_name: str = 'gpt-4') -> bool:
    """
    Check if GPT-vision is available.

    Parameters
    ----------
    vision_model_name : str
        Name of the GPT-vision model to check for.

    Returns
    -------
    bool
        True if the model is available, False otherwise.

    """

    with asection(f"Checking if GPT-vision is available:"):
        model_list = get_openai_model_list()
        is_available = any(vision_model_name in model for model in model_list)
        if is_available:
            aprint(f"GPT-vision is available!")
        return is_available

def describe_image(image_path: str,
                   query: str = 'Here is an image, please carefully describe it in detail.',
                   model: str = "gpt-4o",
                   max_tokens: int = 4096,
                   number_of_tries: int = 4,
                   ) -> str:
    """
    Describe an image using GPT-vision.

    Parameters
    ----------
    image_path: str
        Path to the image to describe
    query  : str
        Query to send to GPT
    model   : str
        Model to use
    max_tokens  : int
        Maximum number of tokens to use
    number_of_tries : int
        Number of times to try to send the request to GPT.

    Returns
    -------
    str
        Description of the image

    """

    with (asection(f"Asking GPT-vision to analyse a given image at path: '{image_path}':")):
        aprint(f"Query: '{query}'")
        aprint(f"Model: '{model}'")
        aprint(f"Max tokens: '{max_tokens}'")

        if image_path.endswith('.png'):
            image_format = 'png'
        elif image_path.endswith('.jpg') or image_path.endswith('.jpeg'):
            image_format = 'jpeg'
        else:
            raise NotImplementedError(f"Image format not supported: '{image_path}' (only .png and .jpg are supported)")

        import base64

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
                            "text": query
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

            from openai import OpenAI
            from openai.resources.chat import Completions

            # Ensure that the OpenAI API key is set:
            set_api_key('OpenAI')

            try:
                for tries in range(number_of_tries):

                    # Instantiate API entry points:
                    client = OpenAI()
                    completions = Completions(client)

                    # Send a request to GPT:
                    result = completions.create(model=model,
                                                messages=prompt_messages,
                                                max_tokens=max_tokens)

                    # Actual response:
                    response = result.choices[0].message.content
                    aprint(f"Response: '{response}'")

                    # Check if the response is empty:
                    if not response:
                        aprint(f"Response is empty. Trying again...")
                        continue

                    # response in lower case and trimmed of white spaces
                    response_lc = response.lower().strip()

                    # Check if response is too short:
                    if len(response) < 3:
                        aprint(f"Response is empty. Trying again...")
                        continue

                    # if the response contains these words: "sorry" and ("I cannot" or "I can't")  then try again:
                    if ("sorry" in response_lc and ("i cannot" in response_lc or "i can't" in response_lc or 'i am unable' in response_lc)) \
                        or "i cannot assist" in response_lc or "i can't assist" in response_lc or 'i am unable to assist' in response_lc or "I'm sorry" in response_lc:
                        aprint(f"Vision model refuses to assist (response: {response}). Trying again...")
                        continue
                    else:
                        return response

            except Exception as e:
                # Log the error:
                aprint(f"Error: '{e}'")
                # print stack trace:
                import traceback
                traceback.print_exc()
                return f"Error: '{e}'"

