from django.shortcuts import render,redirect
from .models import Quiz,Question,Participant
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
    while (len(Question.objects.filter(q_id=code))>0):
        code=generategeneric()
    return code



def home(request):
    return render(request,"home.html")

def createcode(request):
    new_quiz_code=generate_quiz_code()
    new_quiz=Quiz.objects.create(quiz_id=new_quiz_code)
    new_quiz.save()
    return redirect(f'/quizdata/{new_quiz_code}')

def entercode(request):
    if request.method=="POST":
        return redirect(f"/quizdata/{request.POST['code']}")
    return render(request,"entercode.html")

def questions(request,code):
    quiz=Quiz.objects.filter(quiz_id=code)
    if len(quiz)<1:
        return redirect("/")
    if request.method=="POST":
        new_q=Question.objects.create(q_id=generate_question_code(),
                                parent=quiz[0],
                                question=request.POST['question'],
                                option_a=request.POST['option_a'],
                                option_b=request.POST['option_b'],
                                option_c=request.POST['option_c'],
                                option_d=request.POST['option_d'],
                                ans=request.POST['answer'])
        new_q.save()
    context={}
    context['quiz']=quiz[0]
    questions=Question.objects.filter(parent=quiz[0])
    context['questions']=questions
    return render(request,"questions.html",context=context)

def delete(request,q_code,code):
    question=Question.objects.filter(q_id=code)
    if question:
        question.delete()
    return redirect(f"/questions/{q_code}")
    
def quizdata(request,code):
    quiz=Quiz.objects.filter(quiz_id=code)
    if len(quiz)<0:
        redirect("/")
    context={}
    context['quiz']=quiz[0]
    #questions=Question.objects.filter(parent=quiz[0])
    #context['questions']=questions
    participants=Participant.objects.filter(quiz=quiz[0])
    new_participants=[]
    for x in participants:
        temp_data=x
        content=[f"Question {i+1}: RIGHT" if t=="1" else f"Question {i+1}: WRONG" for i,t in enumerate(x.answers)]
        #track=" ".join(content)
        score=str(x.answers.count('1')*100/len(x.answers))
        new_participants.append({'data':temp_data,'track':content,'score':score})
    context['participants']=new_participants
    return render(request,"quizdata.html",context=context)