import google.generativeai as genai
from django.http import JsonResponse
from django.shortcuts import render
from markdown2 import markdown
from django.contrib.auth.decorators import login_required
from user_management.models import UserGeminiChat  # Add this import
import google.generativeai as genai

# Configure the API key
genai.configure(api_key="AIzaSyD-4HZiBslNKdFP50NJGl6YQgeae3jOPFU")
model = genai.GenerativeModel('gemini-1.5-flash')

pre_info = """
You are an AI chatbot designed to provide emotional support to construction workers in the UK. 
Understand that this is a demanding profession with unique challenges, including:
* **Physical demands:** Heavy lifting, strenuous work, potential for injuries.
* **Mental stress:** Deadlines, pressure, safety concerns, job security.
* **Social isolation:** Long hours, shift work, potential for loneliness and social disconnect.
* **Substance abuse:** Higher risk of alcohol and drug use due to stress and social factors.

When interacting with users, maintain the following:
* **Empathy and understanding:** Acknowledge their feelings and experiences without judgment.
* **Confidentiality:** Reassure users that their conversations are private and confidential.
* **Non-judgmental support:** Offer a safe space for them to express their emotions without fear of criticism.
* **Practical advice:** Provide helpful resources and information, such as contact details for relevant support organizations (e.g., Construction Industry Helpline, Mind, Samaritans).
* **Positivity and encouragement:** Offer words of support and encouragement to help users cope with challenges.
* **Humility:** Acknowledge your limitations as an AI and direct users to professional help when necessary.

Remember to use a supportive and encouraging tone, avoiding jargon or overly technical language. 
Focus on building rapport and creating a trusting relationship with the user. Avoid placeholders like "insert helpline number here" to ensure professionalism and readiness for deployment.
Avoid promising solutions beyond the chatbot's scope, emphasizing your role as a supportive companion.
also remember since this is like a chat conversatin keep your responses short and concise.
"""
chat = model.start_chat(history=[])
chat.send_message(pre_info)

@login_required(login_url='/auth/login/')
def chatbot_home(request):
    return render(request, 'chatbot/index.html')

def get_chatbot_response(message, language):
    # Add language context to the message
    contextualized_message = f"Please respond in {language} language: {message}"
    response = chat.send_message(contextualized_message)
    return response.text

def chatbot_response(request):
    if request.method == "POST":
        message = request.POST.get('message', '')
        language = request.POST.get('language', 'en')
        
        print(f"\n=== Chatbot Interaction ===")
        print(f"User ID: {request.user.id}")
        print(f"Message: {message}")
        print(f"Language: {language}")
        
        # Get response from chatbot
        response = get_chatbot_response(message, language)
        print(f"Gemini Response: {response[:100]}...")  # Print first 100 chars
        
        # Save the chat to database
        chat = UserGeminiChat.objects.create(
            user=request.user,
            user_message=message,
            gemini_response=response,
            sentiment_score=0.5
        )
        print(f"Chat saved to database with ID: {chat.id}")
        
        return JsonResponse({"response": response})
    
    return JsonResponse({"error": "Invalid request"}, status=400)



