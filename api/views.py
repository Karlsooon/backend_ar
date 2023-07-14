from django.http import JsonResponse, HttpResponse
import json
import base64
import requests
import openai
import http.client
from google.cloud import texttospeech
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

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
            api_key = "AIzaSyCYP2i5j5TOs3k8MwmFnvGVqoE0amU52A0"

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
        " Based on the provided JSON information, please extract common   person name, common  brand name,common  building name,common   movie name.use the article permalinks. And print only value dont write key \n"
        + str(extracted_info)
    )

    # Set up the OpenAI API
    openai.api_key = "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"

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
    conn = http.client.HTTPSConnection("google.serper.dev")
    payload = json.dumps({"q": response, "gl": "kz", "num": 20})
    headers = {
        "X-API-KEY": "93ec7673945edb129002d825eacb90d68283fc58",
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
        " From using given json information tell me about /n"
        + str(response)
        + "in /n"
        + str(extracted_info)
        + "you can add extra informations.Write it in one paragraph.Finish the sentences all time."
    )

    openai.api_key = "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"

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


def register(request):
    if request.method == "POST":
        try:
            # Retrieve registration data from the request
            data = json.loads(request.body)
            name = data["name"]
            email = data["email"]
            password = data["password"]

            # Perform registration logic and save to the database
            # Add your MongoDB code here to save the registration data

            # Return a success response
            return JsonResponse({"message": "Registration successful"})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=400)
