from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from .models import Quiz, Question, Choice, QuizAttempt, UserAnswer
from .forms import QuizGenerationForm, QuestionForm, ChoiceForm
from .utils import generate_questions
import json


@login_required
def quiz_list(request):
    quizzes = Quiz.objects.filter(created_by=request.user)
    return render(request, 'quizzes/quiz_list.html', {'quizzes': quizzes})


@login_required
def generate_quiz(request):
    if request.method == 'POST':
        form = QuizGenerationForm(request.user, request.POST)
        if form.is_valid():
            document = form.cleaned_data['document']
            title = form.cleaned_data['title']
            num_multiple_choice = form.cleaned_data['num_multiple_choice']
            num_true_false = form.cleaned_data['num_true_false']
            num_essay = form.cleaned_data['num_essay']

            # Create a new quiz
            quiz = Quiz.objects.create(
                title=title,
                document=document,
                created_by=request.user
            )

            # Generate questions using OpenAI
            generated_questions = generate_questions(
                document.content,
                num_multiple_choice,
                num_true_false,
                num_essay
            )

            # Save generated questions to the database
            for q_data in generated_questions:
                question = Question.objects.create(
                    quiz=quiz,
                    question_text=q_data['question'],
                    question_type=q_data['type']
                )

                # Save choices for multiple choice and true/false questions
                if q_data['type'] in ['multiple_choice', 'true_false']:
                    for choice_data in q_data['choices']:
                        Choice.objects.create(
                            question=question,
                            choice_text=choice_data['text'],
                            is_correct=choice_data['is_correct']
                        )

            messages.success(request, 'Quiz generated successfully!')
            return redirect('edit_quiz', pk=quiz.pk)
    else:
        form = QuizGenerationForm(request.user)

    return render(request, 'quizzes/generate_quiz.html', {'form': form})


@login_required
def quiz_detail(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    # Get user attempts for this quiz
    user_attempts = QuizAttempt.objects.filter(quiz=quiz, user=request.user).order_by('-started_at')

    return render(request, 'quizzes/quiz_detail.html', {
        'quiz': quiz,
        'user_attempts': user_attempts
    })


@login_required
def edit_quiz(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk, created_by=request.user)
    return render(request, 'quizzes/edit_quiz.html', {'quiz': quiz})


@login_required
def edit_question(request, quiz_pk, question_pk):
    quiz = get_object_or_404(Quiz, pk=quiz_pk, created_by=request.user)
    question = get_object_or_404(Question, pk=question_pk, quiz=quiz)

    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            messages.success(request, 'Question updated successfully!')
            return redirect('edit_quiz', pk=quiz.pk)
    else:
        form = QuestionForm(instance=question)

    return render(request, 'quizzes/edit_question.html', {
        'form': form,
        'quiz': quiz,
        'question': question
    })


@login_required
def delete_question(request, quiz_pk, question_pk):
    quiz = get_object_or_404(Quiz, pk=quiz_pk, created_by=request.user)
    question = get_object_or_404(Question, pk=question_pk, quiz=quiz)

    if request.method == 'POST':
        question.delete()
        messages.success(request, 'Question deleted successfully!')
        return redirect('edit_quiz', pk=quiz.pk)

    return render(request, 'quizzes/delete_question.html', {
        'quiz': quiz,
        'question': question
    })


@login_required
def export_quiz(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk, created_by=request.user)

    # Create a JSON representation of the quiz
    quiz_data = {
        'title': quiz.title,
        'questions': []
    }

    for question in quiz.questions.all():
        q_data = {
            'text': question.question_text,
            'type': question.question_type,
        }

        if question.question_type in ['multiple_choice', 'true_false']:
            q_data['choices'] = [
                {
                    'text': choice.choice_text,
                    'is_correct': choice.is_correct
                }
                for choice in question.choices.all()
            ]

        quiz_data['questions'].append(q_data)

    # Return as JSON file
    response = HttpResponse(json.dumps(quiz_data, indent=4), content_type='application/json')
    response['Content-Disposition'] = f'attachment; filename="{quiz.title}.json"'
    return response


# New views for taking quizzes and viewing results
@login_required
def take_quiz(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)

    # Create a new attempt
    attempt = QuizAttempt.objects.create(
        quiz=quiz,
        user=request.user
    )

    return render(request, 'quizzes/take_quiz.html', {
        'quiz': quiz,
        'attempt': attempt
    })


@login_required
def submit_quiz(request, attempt_pk):
    attempt = get_object_or_404(QuizAttempt, pk=attempt_pk, user=request.user)

    if request.method == 'POST':
        # Process the submitted answers
        for question in attempt.quiz.questions.all():
            if question.question_type == 'essay':
                essay_answer = request.POST.get(f'question_{question.id}', '')
                UserAnswer.objects.create(
                    attempt=attempt,
                    question=question,
                    essay_answer=essay_answer
                )
            else:  # multiple_choice or true_false
                choice_id = request.POST.get(f'question_{question.id}')
                if choice_id:
                    choice = get_object_or_404(Choice, id=choice_id)
                    UserAnswer.objects.create(
                        attempt=attempt,
                        question=question,
                        selected_choice=choice
                    )

        # Mark the attempt as completed
        attempt.completed_at = timezone.now()
        attempt.score = attempt.calculate_score()
        attempt.save()

        messages.success(request, 'Quiz submitted successfully!')
        return redirect('quiz_results', attempt_pk=attempt.pk)

    return redirect('take_quiz', pk=attempt.quiz.pk)


@login_required
def quiz_results(request, attempt_pk):
    attempt = get_object_or_404(QuizAttempt, pk=attempt_pk, user=request.user)

    # Make sure the attempt is completed
    if not attempt.completed_at:
        messages.error(request, 'This quiz attempt has not been completed yet.')
        return redirect('take_quiz', pk=attempt.quiz.pk)

    return render(request, 'quizzes/quiz_results.html', {
        'attempt': attempt,
        'quiz': attempt.quiz
    })


@login_required
def all_attempts(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    attempts = QuizAttempt.objects.filter(quiz=quiz, user=request.user, completed_at__isnull=False).order_by(
        '-completed_at')

    return render(request, 'quizzes/all_attempts.html', {
        'quiz': quiz,
        'attempts': attempts
    })
