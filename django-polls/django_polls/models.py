import datetime

from django.db import models
from django.utils import timezone

# create models below...
# keep variable names discriptive....


# We have created 2 models/tables below
# i) Question
# ii) Choice
class Question(models.Model):
    question_text = models.CharField(max_length=200)
    published_date = models.DateTimeField("date published")

    def __str__(self):
        return self.question_text

    def was_published_recently(self):
        now = timezone.now()
        # date of tomorrow <= (self.published_date) <= at the moment date.
        return (now - datetime.timedelta(days=1)) <= self.published_date <= now


"""
was_published_recently() returns True for questions 
whose pub_dateis within the last day.
"""


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    vote = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text
