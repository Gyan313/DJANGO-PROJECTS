# importing all the modules below.....
from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.http import Http404
from django.utils import timezone

# F() is used to avoid the race condition.
from django.db.models import F

from django.views import generic

# from .models import Question, Choice
from django_polls.models import Question, Choice


""" 
In our poll application, we'll have the following four views:

Question “index” page - displays the latest few questions.
Question “detail” page - displays a question text, with no results but with a form to vote.
Question “results” page - displays results for a particular question.
"Vote" action - handles voting for a particular choice in a particular question. 
"""

# We have made "function based views" first.

""" 
def index(request):
    # Below "latest_question_list" is intended to get us 5 questions published most recently.
    # And in descending order by there published date. "-" sign indicates descending.
    latest_question_list = Question.objects.order_by("-published_date")[:5]

    # uncomment output when not using any django created template.
    # output = ", ".join([q.question_text for q in latest_question_list])

    '''
    template = loader.get_template("polls/index.html")
    context = {"latest_question_list": latest_question_list}
    return HttpResponse(template.render(context, request))
    '''

    # shortcut for above code.
    context = {"latest_question_list": latest_question_list}
    return render(request, "polls/index.html", context)


def detail(request, question_id):
    '''
    try:
        question = Question.objects.get(pk=question_id)
    except Question.DoesNotExist:
        raise Http404("Question does not exist...")
    '''

    # or there is a shortcut for writing above lines of code by using ....
    question = get_object_or_404(Question, pk=question_id)

    # at last
    return render(request, "polls/detail.html", {"question": question})


def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, "polls/results.html", {"question": question})

"""


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        return render(
            request,
            "polls/detail.html",
            {"question": question, "error_message": "You didn't select a choice."},
        )
    else:
        selected_choice.vote = F("vote") + 1
        selected_choice.save()
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))


# Now,below we are creating "class based views"...
# Below, I am going to refactor the code of 'index, results, detail' view to convert them into
# generic views which are class based view.
class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self) -> QuerySet[str]:
        # last 5 question chahiye, thats why we used "-"published_date
        # published_date__lte : here "__lte" means 'less-than-or-equal-to'.
        present_questions = Question.objects.filter(
            published_date__lte=timezone.now()
        ).order_by("-published_date")[:5]

        question_set = Question.objects.none()

        # only questions with choices to be displayed on the screen
        for question in present_questions:
            number_of_choices = len(question.choice_set.all())
            if number_of_choices > 0:
                question_set |= Question.objects.filter(pk=question.id)

        return question_set


class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"

    def get_queryset(self) -> QuerySet[str]:
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(published_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"

    def get_queryset(self) -> QuerySet[str]:
        return Question.objects.filter(published_date__lte=timezone.now())


# This get_queryset() method is the one setting the "context" dictionary value.
# See, above "context" in the view is a dictionary whose key is used in templates of that view and
# value is set by us using get_queryset() and manually too.
