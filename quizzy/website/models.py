from django.db import models

class Quiz(models.Model):
    quiz_id=models.CharField(max_length=10,primary_key=True)

class Question(models.Model):
    q_id=models.CharField(max_length=10,primary_key=True)
    parent=models.ForeignKey(to=Quiz,on_delete=models.CASCADE)
    question=models.CharField(max_length=200)
    option_a=models.CharField(max_length=100)
    option_b=models.CharField(max_length=100)
    option_c=models.CharField(max_length=100)
    option_d=models.CharField(max_length=100)
    ans=models.CharField(max_length=1)
