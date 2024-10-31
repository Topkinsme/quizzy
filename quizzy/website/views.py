from django.shortcuts import render,redirect
from .models import Quiz,Question
import random

chars=[chr(x) for x in range (65,91)]
nums=[chr(x) for x in range (48,58)]

def generategeneric():
    return random.choice(chars)+random.choice(chars)+random.choice(nums)+random.choice(nums)+random.choice(chars)+random.choice(chars)

def generate_quiz_code():
    code=generategeneric()
    while (len(Quiz.objects.filter(quiz_id=code))>0):
        code=generategeneric()
    return code

def generate_question_code():
    code=generategeneric()
    while (len(Question.objects.filter(quiz_id=code))>0):
        code=generategeneric()
    return code



def home(request):
    return render(request,"home.html")

def createcode(request):
    new_quiz_code=generate_quiz_code()
    new_quiz=Quiz.objects.create(quiz_id=new_quiz_code)
    new_quiz.save()
    return redirect(f'/questions/{new_quiz_code}')

def entercode(request):
    return render(request,"entercode.html")

def questions(request,code):
    quiz=Quiz.objects.filter(quiz_id=code)
    if len(quiz)<1:
        return redirect("/")
    context={}
    questions=Question.objects.filter(parent=quiz[0])
    context['questions']=questions
    return render(request,"questions.html")
