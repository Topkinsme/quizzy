from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request,"home.html")

def entercode(request):
    return render(request,"entercode.html")