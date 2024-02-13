import datetime
from django.utils import timezone
from django.test import TestCase
from django.urls import reverse

from .models import Question, Choice


# creating a function to create Question for us....
def create_question(question_text, days):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    published_date = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(
        question_text=question_text, published_date=published_date
    )


# self.client ---> we get a client from TestCase class that we inherited to make test classes.
# self ---> contains reference of the object created by "QuestionModelTests" and "TestCase" class
#           because when we inherit a class that means we are using functions and variables of
#           that class.
class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        # question going to be published in 30 days.
        future_question = create_question(question_text="Future Question.", days=30)
        self.assertIs(future_question.was_published_recently(), False)  # --> better
        # or,
        # assert future_question.was_published_recently() == False

    def test_was_published_recently_with_recent_date(self):
        # question going to be published in right now.
        recent_question = create_question(question_text="recent question.", days=0)
        self.assertIs(recent_question.was_published_recently(), True)

    def test_was_published_recently_with_old_question(self):
        # question published in 2 days ago.
        old_question = create_question(question_text="old question.", days=-2)
        self.assertIs(old_question.was_published_recently(), False)


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "No polls are available.But you are welcome to make one!"
        )
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

        # 'response.context["latest_question_list"]' -----> going to return the list of questions
        # we get from "get_querySet()" method of Index view.

    def test_past_question(self):
        question = create_question(question_text="Past Question.", days=-10)
        Choice.objects.create(question=question, choice_text="Yes/No")
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(response.context["latest_question_list"], [question])

    def test_future_question(self):
        create_question(question_text="Future Question.", days=20)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(
            response,
            "No polls are available.But you are welcome to make one!",
        )
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_past_question_and_future_question(self):
        past_question = create_question(question_text="Past Question", days=-30)
        Choice.objects.create(question=past_question, choice_text="Yes/No")
        future_question = create_question(question_text="Future Question", days=30)
        Choice.objects.create(question=future_question, choice_text="Haan/Naa")
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"], [past_question]
        )

    # we need to write test for "multiple past question", which also means test for more than 1 question.
    def test_two_past_questions(self):
        question1 = create_question(question_text="Past Question 1", days=-2)
        Choice.objects.create(question=question1, choice_text="Yes/No")
        self.assertEqual(len(question1.choice_set.all()), 1)
        question2 = create_question(question_text="Past Question 2", days=-3)
        Choice.objects.create(question=question2, choice_text="Haan/Naa")
        response = self.client.get(reverse("polls:index"))
        # I got into an error for comparing 'response.context["latest_question_list"]' with '[question1, question2]' in below "self.assertQuerySetEqual".
        # Exception ----> ValueError: Trying to compare non-ordered queryset against more than one ordered value.
        # Answer ----> You are comparing a QuerySet with a list. List has an ordering but Queryset doesn't.
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question1, question2],
            ordered=False,
        )


# Note that the "django.test.TestCase" class provides some additional "assertion" methods.
# This means "assertQuerySetEqual", "assertContains", "assertIs", "assertEqual" we are using these methods because we inherited the class "TestCase"  in all of our Test classes.


# Now we are going to write Tests for "DetailView"
# 1) Test to make sure past question is displayed flawlessly.
# 2) Test to make sure future question is not displayed.
class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question = create_question(question_text="Future question.", days=5)
        url = reverse("polls:detail", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text="Past Question.", days=-5)
        url = reverse("polls:detail", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)


class QuestionResultViewTests(TestCase):
    # 1) test the past question publishing in Result View.
    # 2) test the future question publishing in Result View.

    def test_past_question(self):
        past_question = create_question(question_text="Past Question.", days=-30)
        url = reverse("polls:results", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

    def test_future_question(self):
        future_question = create_question(question_text="Future Question.", days=1)
        url = reverse("polls:results", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
