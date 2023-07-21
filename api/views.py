from django.http import JsonResponse, HttpResponse
import json
import base64
import requests
import openai
import http.client
from google.cloud import texttospeech
from google.auth import credentials

# from django.views.decorators.csrf import csrf_exempt
# from django.http import JsonResponse
import dotenv

import os

dotenv.load_dotenv()

client = texttospeech.TextToSpeechClient()


def process_image(request):
    if request.method == "POST":
        try:
            # Get the image from the request
            image = request.FILES["file"]

            # Read the image data
            content = image.read()

            # Convert image data to base64 encoding
            base64_image = base64.b64encode(content).decode("utf-8")

            # Prepare the request body for Google Cloud Vision API
            request_body = {
                "requests": [
                    {
                        "image": {"content": base64_image},
                        "features": [
                            {"type": "WEB_DETECTION"},
                            # Add more feature types as needed
                        ],
                    }
                ]
            }

            # Set the Google Cloud Vision API endpoint and API key
            endpoint = "https://vision.googleapis.com/v1/images:annotate"
            api_key = os.environ.get("GOOGLE_CLOUD_API")

            # Send the image data to Google Cloud Vision API
            response = requests.post(
                f"{endpoint}?key={api_key}",
                json=request_body,
                headers={"Content-Type": "application/json"},
            )

            if response.status_code == 200:
                # Successful response
                json_response = response.json()
                print("*****************************************")
                print(json.dumps(json_response, indent=4))
                print("*****************************************")

                # Process the JSON response
                # extracted_info = extract_info_from_json(json_response)

                # Use ChatGPT to generate a response
                generated_response = generate_response(json_response)

                return HttpResponse(generated_response)

            else:
                # Handle other response codes
                print(f"Error google lense: {response.status_code} - {response.text}")

        except Exception as e:
            print(str(e))
            return JsonResponse({"error google lense": str(e)}, status=500)

    return JsonResponse({"error google lense": "Invalid request method"}, status=400)


def generate_response(extracted_info):
    # Join the extracted information into a prompt string
    prompt = (
        "Based on the provided JSON information from Google Cloud Vision API, please extract common person names, common brand names, common building names, and common movie names. Also, include the first 5 words with high scores. Use the article permalinks. Only provide the values, and avoid writing the keys.\n"
        + str(extracted_info)
    )

    # Set up the OpenAI API
    openai.api_key = os.environ.get("OPEN_AI_KEY")
    # openai.api_key = "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"

    # Generate a response using ChatGPT
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=100,
        n=1,
        # stop=None,
        temperature=0.7,
    )
    result = response.choices[0].message.content
    print(result)
    return send_serper(result)
    return response.choices[0].message.content


def send_serper(response):
    print("serper in")
    conn = http.client.HTTPSConnection("google.serper.dev")
    payload = json.dumps({"q": response, "gl": "kz", "num": 10})
    headers = {
        "X-API-KEY": os.environ.get("SERPER_KEY"),
        "Content-Type": "application/json",
    }
    conn.request("POST", "/search", payload, headers)
    res = conn.getresponse()
    data = res.read()
    result = data.decode("utf-8")
    print("serper" + result)
    return get_result(result, response)
    return data.decode("utf-8")


def get_result(extracted_info, response):
    prompt = (
        "From the extracted JSON information above and the previous ChatGPT response, please tell me more about the content.\n"
        + str(response)
        + "in/n"
        + "From the information below, can you describe the words mentioned above in 3 sentences? Avoid cutting off sentences, and don't include words like 'from this JSON information,' etc. Provide only the generated 3 sentences.\n"
        + str(extracted_info)
    )

    openai.api_key = os.environ.get("OPEN_AI_KEY")

    # Generate a response using ChatGPT
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=100,
        n=1,
        # stop=None,
        temperature=0.7,
    )
    result = response.choices[0].message.content
    print("RESULT!")
    print(result)
    return result


def chat_with_chatgpt(request):
    if request.method == "POST":
        try:
            # Get the user message from the request
            data = json.loads(request.body)
            user_message = data.get("message")

            # Set up the OpenAI API
            openai.api_key = os.environ.get("OPEN_AI_KEY")

            # Generate a response using ChatGPT
            response = openai.Completion.create(
                engine="text-davinci-002",  # Use the GPT-3.5 Turbo engine
                prompt=user_message,
                max_tokens=100,
                n=1,
                temperature=0.7,
            )

            # Extract the generated response from ChatGPT
            generated_response = response.choices[0].text

            # Send the generated response back to the frontend
            return JsonResponse({"response": generated_response})

        except Exception as e:
            print(str(e))
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=400)
