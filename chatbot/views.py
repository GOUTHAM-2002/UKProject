import google.generativeai as genai
from django.http import JsonResponse
from django.shortcuts import render
from markdown2 import markdown

# Configure the API key
genai.configure(api_key="AIzaSyD-4HZiBslNKdFP50NJGl6YQgeae3jOPFU")
model = genai.GenerativeModel('gemini-1.5-flash')
chat = model.start_chat(history=[])

def chatbot_home(request):
    return render(request, 'chatbot/index.html')


def chatbot_response(request):
    if request.method == "POST":
        user_input = request.POST.get('message')
        if user_input.lower() == "exit":
            return JsonResponse({"response": "Goodbye!"})

        # Generate response from the chatbot
        response = chat.send_message(user_input, stream=False)
        full_response = "".join(chunk.text for chunk in response if chunk.text)

        # Convert the markdown response to HTML
        html_response = markdown(full_response)

        return JsonResponse({"response": html_response})

