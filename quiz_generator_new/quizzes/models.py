from django.db import models
from django.contrib.auth.models import User
from documents.models import Document


class Quiz(models.Model):
    title = models.CharField(max_length=255)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='quizzes')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Question(models.Model):
    QUESTION_TYPES = (
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('essay', 'Essay'),
    )

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=15, choices=QUESTION_TYPES)

    def __str__(self):
        return self.question_text[:50]


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    choice_text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.choice_text


# New models for quiz attempts and answers
class QuizAttempt(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    score = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s attempt on {self.quiz.title}"

    def calculate_score(self):
        """Calculate the score for this attempt"""
        total_questions = self.quiz.questions.filter(question_type__in=['multiple_choice', 'true_false']).count()
        if total_questions == 0:
            return 0

        correct_answers = 0
        for answer in self.answers.filter(question__question_type__in=['multiple_choice', 'true_false']):
            if answer.is_correct():
                correct_answers += 1

        return (correct_answers / total_questions) * 100


class UserAnswer(models.Model):
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, on_delete=models.CASCADE, null=True, blank=True)
    essay_answer = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Answer to {self.question}"

    def is_correct(self):
        """Check if the answer is correct for multiple choice and true/false questions"""
        if self.question.question_type in ['multiple_choice', 'true_false']:
            return self.selected_choice and self.selected_choice.is_correct
        return None  # Essay questions don't have correct/incorrect answers
