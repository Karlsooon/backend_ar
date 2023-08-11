from django.http import JsonResponse, HttpResponse
import json
import base64
import requests
import openai
import http.client
import os
import dotenv
import spacy


# Load environment variables
dotenv.load_dotenv()
nlp = spacy.load("en_core_web_sm")


# Initialize the OpenAI API

def search_person(request):
    if request.method == "POST":
        try:
            # Get the user name from the request data sent by the frontend
            data = json.loads(request.body)
            user_name = data["message"]

            # Call the function to extract the person's name from the user name
            person_name = extract_person_name(user_name)

            # Generate a chat response based on the extracted person's name
            chat_response = generate_chat_response2(person_name)

            # Return the chat response as a JSON response to the frontend
            return JsonResponse({"response": chat_response})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=400)


def extract_person_name(user_message):
    # Process the user message using spaCy NER
    doc = nlp(user_message)

    # Extract person names from the document
    person_names = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]

    if person_names:
        return send_serper2(person_names[0])  # Return the first person name found
    else:
        return "User"


def generate_chat_response2(result, person_name):
    # Set up the OpenAI API
    openai.api_key = os.environ.get("OPEN_AI_KEY")

    # Get the person's name from the user message

    # Define the prompt message with the person's name
    prompt = f"tell me about {person_name} from given JSON information {result}"

    # Generate a response using ChatGPT
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": prompt},
            # {"role": "user", "content": person_name},
        ],
        max_tokens=100,
        n=1,
        temperature=0.7,
    )

    # Extract the generated response from ChatGPT's reply
    generated_response = response.choices[0].message["content"]

    # Send the person's name to "serper" service and get information
    serper_response = send_serper2(person_name)

    # Process the "serper" response and append it to the generated response
    final_response = f"{generated_response}\n\n{serper_response}"

    return final_response


def send_serper2(person_name):
    # Send the person's name to the "serper" service to get relevant information
    conn = http.client.HTTPSConnection("google.serper.dev")
    payload = json.dumps({"q": person_name, "gl": "kz", "num": 10})
    headers = {
        "X-API-KEY": os.environ.get("SERPER_KEY"),
        "Content-Type": "application/json",
    }
    conn.request("POST", "/search", payload, headers)
    res = conn.getresponse()
    data = res.read()
    result = data.decode("utf-8")
    return generate_chat_response2(result, person_name)


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
        "Based on the provided JSON information from Google Cloud Vision API, please extract common person names, common brand names, common building names, and common movie names. Only provide the values, and avoid writing the keys.Also, include the first 5 words with high scores. Use the article permalinks. Only provide the values, and avoid writing the keys.And please always end the sentences.End sentences with dote(.).And end last sentense.End last sentence with dote(.) \n"
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
        "From the extracted  information,please tell me in one paragraph    more about the words below,describe them in 3 sentence.Create one paragraph history about them and tell it.Dont contain word 'json' in paragraph.And always end the sentence.And please always end the sentences.End sentences with dote(.).And end last sentense.End last sentence with dote(.) \n"
        + str(response)
        + "in/n"
        + str(extracted_info)
        + "From the information below, can you describe the words mentioned below in 3 sentences? Avoid cutting off sentences, and don't include words like 'from this JSON information,' etc.Dont tell about json.In you sentence dont contain word 'JSON' or 'Json' or 'json'. Provide only the generated in 3 sentences that will describe the response words in 3 sentence.It can be the description of the word like what is it who is it if person and like this.Dont write what words you see in json just describe them.As a 1 paragraph create historyAnd please always end the sentences.End sentences with dote(.).And end last sentense.End last sentence with dote(.)\n"
        + str(response)
    )

    openai.api_key = os.environ.get("OPEN_AI_KEY")

    # Generate a response using ChatGPT
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=100,
        n=1,
        # stop=None,
        temperature=1,
    )
    result = response.choices[0].message.content
    print("RESULT!")
    print(result)
    return result


def chat_with_chatgpt(request):
    if request.method == "POST":
        try:
            print("before json response")
            data = json.loads(request.body)
            print(" Get the message from the request")
            message = data["message"]
            print("Use ChatGPT to generate a response")
            generated_response = generate_chat_response(message)
            return JsonResponse({"response": generated_response})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=502)

    return JsonResponse({"error": "Invalid request method"}, status=400)


def generate_chat_response(user_message):
    print("before key")
    # Set up the OpenAI API
    openai.api_key = os.environ.get("OPEN_AI_KEY")

    # Define the prompt message
    prompt = "Hi you can ask any question about this object....... "
    print("before generating openai key")

    # Generate a response using ChatGPT
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_message},
        ],
        max_tokens=100,
        n=1,
        temperature=0.7,
    )

    print("Extract the generated response from ChatGPTs reply")
    generated_response = response.choices[0].message["content"]

    return generated_response
