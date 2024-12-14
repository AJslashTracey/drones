import base64
import csv
from openai import OpenAI
from dotenv import load_dotenv
import os

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def save_response_to_csv(response, file_path):
    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Write the response to a CSV file
    with open(file_path, mode='w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["Response"])
        writer.writerow([response])

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
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        },
                    },
                ],
            }
        ],
    )

    # Extract the response content
    chat_response = response.choices[0].message.content

    # Save the response to a CSV file
    csv_file_path = os.path.join("responses", "response3.csv")
    save_response_to_csv(chat_response, csv_file_path)

    return chat_response

# Example usage
# Replace 'path_to_image.jpg' with the path to your image
# response = getChatGPTResponse('path_to_image.jpg')
# print("ChatGPT Response:", response)
