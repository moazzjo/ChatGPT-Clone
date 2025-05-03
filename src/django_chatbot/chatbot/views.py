from django.shortcuts import render, redirect
from django.http import JsonResponse

#Django authentication and User model importing
from django.contrib.auth.models import User
from django.contrib import auth

# for login requires 
from django.contrib.auth.decorators import login_required
# AI importing library
# from openai import OpenAI ---> openai need $ 
from google import genai
#load the .env file for using the secure data inside it
from dotenv import load_dotenv
load_dotenv()
# modls 
from .models import Chat
# my OS
import os 
# date time for the device location
from django.utils import timezone

import markdown


# Gimini API 
client = genai.Client(api_key=os.getenv("CHATGPT_API_KEY"))

def ask_genai(message):
    
    if isinstance(message, str):    
        response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents= message
        )
    else:
        response = "invalid value input, Please try again"
    return response.text
    
    

# Create your views here.
@login_required
def chatbot(request):
    chats = Chat.objects.filter(user = request.user)
    if request.method == 'POST':
        message = request.POST.get('message')
        response = ask_genai(message)
        
        chat = Chat(user=request.user, message=message, response=markdown.markdown(response), created_at=timezone.now)
        chat.save()
        return JsonResponse({'message':message, 'response':markdown.markdown(response)})

    return render(request, 'chatbot/chatbot.html', {'chats':chats})


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST["email"]
        password1 = request.POST["password1"]
        password2 = request.POST["password2"]
        
        
        if password1 == password2:
            try:
                user = User.objects.create_user(username, email, password1)
                user.save()
                auth.login(request,user)
                return redirect('chatbot')
            except:
                error_message = "signup faild, Please Try again"
                return render(request, "chatbot/register.html", {'error_message':error_message} )
                
        else:
            error_message = "Passwords Don't match, Please Try again"
            return render(request, "chatbot/register.html", {'error_message':error_message} )
        
    return render(request, "chatbot/register.html" )

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(request ,username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('chatbot') 
        else:
            error_message = "Invalid username or password"
            return render(request, "chatbot/login.html", {'error_message':error_message} )
    else:
        return render(request, "chatbot/login.html")

def logout(request):
    auth.logout(request)
    return redirect('login')
