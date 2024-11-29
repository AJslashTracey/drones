import base64
from openai import OpenAI
from dotenv import load_dotenv
import os

# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

def getChatGPTResponse(image_path):
    # Load environment variables from the .env file
    load_dotenv()

    # Fetch the API key from environment variables
    api_key = os.getenv("api_key")

    client = OpenAI(api_key=api_key)

    # Getting the base64 string
    base64_image = encode_image(image_path)

    response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": "Carry out commands given in image",
            },
            {
            "type": "image_url",
            "image_url": {
                "url":  f"data:image/jpeg;base64,{base64_image}"
            },
            },
        ],
        }
    ],
    )

    return response.choices[0].message.content