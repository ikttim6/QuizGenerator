from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from documents.models import Document
from quizzes.models import Quiz
from accounts.models import UserProfile
from django.contrib.auth.models import User


def home(request):
    return render(request, 'core/home.html')


def about(request):
    return render(request, 'core/about.html')


@login_required
def dashboard(request):
    user_profile = request.user.profile

    # Get counts for dashboard stats
    document_count = Document.objects.filter(uploaded_by=request.user).count()
    quiz_count = Quiz.objects.filter(created_by=request.user).count()

    # Get recent documents and quizzes
    recent_documents = Document.objects.filter(uploaded_by=request.user).order_by('-uploaded_at')[:5]
    recent_quizzes = Quiz.objects.filter(created_by=request.user).order_by('-created_at')[:5]

    context = {
        'user_profile': user_profile,
        'document_count': document_count,
        'quiz_count': quiz_count,
        'recent_documents': recent_documents,
        'recent_quizzes': recent_quizzes,
    }

    return render(request, 'core/dashboard.html', context)


@login_required
def admin_dashboard(request):
    # Check if user is admin
    if not request.user.is_staff:
        return render(request, 'core/access_denied.html')

    # Get counts for admin dashboard
    user_count = User.objects.count()
    document_count = Document.objects.count()
    quiz_count = Quiz.objects.count()

    # Get user breakdown
    professor_count = UserProfile.objects.filter(user_type='professor').count()
    student_count = UserProfile.objects.filter(user_type='student').count()

    # Get recent users, documents, and quizzes
    recent_users = User.objects.order_by('-date_joined')[:10]
    recent_documents = Document.objects.order_by('-uploaded_at')[:10]
    recent_quizzes = Quiz.objects.order_by('-created_at')[:10]

    context = {
        'user_count': user_count,
        'document_count': document_count,
        'quiz_count': quiz_count,
        'professor_count': professor_count,
        'student_count': student_count,
        'recent_users': recent_users,
        'recent_documents': recent_documents,
        'recent_quizzes': recent_quizzes,
    }

    return render(request, 'core/admin_dashboard.html', context)
