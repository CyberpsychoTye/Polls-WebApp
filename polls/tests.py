from django.test import TestCase
import datetime
from django.utils import timezone
from polls.models import Question
from django.urls import reverse
# Create your tests here.

class QuestionModelTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        time= timezone.now() +datetime.timedelta(days=30)
        future_question=Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(),False)

    def test_was_published_recently_with_old_question(self):
        time= timezone.now() - datetime.timedelta(days=1,seconds=1)
        old_question=Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(),False)

    def test_was_published_recently_with_recent_question(self):
        time=timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question=Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)

def create_question(question_text,days):
    time=timezone.now()+datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text,pub_date=time)

class QuestionIndexViewTest(TestCase):

    """
    If no questions exists, an appropriate message is displayed.
    """
    def test_no_question(self):
        response=self.client.get(reverse('polls:index'))
        self.assertEquals(response.status_code,200)
        self.assertContains(response,'No polls are available.')
        self.assertQuerysetEqual(response.context['latest_question_list'],[])

    """
    Questions that have pub dates in the past are displayed on the index page.
    """
    def test_past_question(self):
        question=create_question(question_text="Question in the past.",days=-30)
        response=self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'],[question],)

    """
    Questions that have a pub_date in the future are not displayed on index page.
    """
    def test_future_question(self):
        question=create_question(question_text='Future question.',days=30)
        response=self.client.get(reverse('polls:index'))
        self.assertContains(response,'No polls are available.')
        self.assertQuerysetEqual(response.context['latest_question_list'],[])

    """
    Even if both past and future questions exist, only the question with pub_date in the 
    past should be displayed.
    """
    def test_future_and_past_question(self):
        future_question=create_question(question_text='Future question.',days=30)
        past_question=create_question(question_text='Past question.',days=-30)
        response=self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'],[past_question],)

    """
    The index page should display all questions that have a pub_date in the past.
    """
    def test_two_past_questions(self):
        past_question_1=create_question(question_text='Past question 1.',days=-5)
        past_question_2=create_question(question_text='Past question 2.',days=-30)
        response=self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'],[past_question_1,past_question_2],)

class QuestionDetailViewTests(TestCase):

    """
    The detail view for a question in the future should display a 404 not found error message.
    """
    def test_future_question_detail(self):
        future_question=create_question(question_text='Future question.',days=5)
        url=reverse('polls:detail',args=(future_question.id,))
        response=self.client.get(url)
        self.assertEqual(response.status_code,404)

    def test_past_question_detail(self):
        past_question=create_question(question_text='Past question.',days=-5)
        url=reverse('polls:detail',args=(past_question.id,))
        response=self.client.get(url)
        self.assertContains(response,past_question.question_text)