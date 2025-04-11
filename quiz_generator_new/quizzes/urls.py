from django.urls import path
from . import views

urlpatterns = [
    path('', views.quiz_list, name='quiz_list'),
    path('generate/', views.generate_quiz, name='generate_quiz'),
    path('<int:pk>/', views.quiz_detail, name='quiz_detail'),
    path('<int:pk>/edit/', views.edit_quiz, name='edit_quiz'),
    path('<int:quiz_pk>/question/<int:question_pk>/edit/', views.edit_question, name='edit_question'),
    path('<int:quiz_pk>/question/<int:question_pk>/delete/', views.delete_question, name='delete_question'),
    path('<int:pk>/export/', views.export_quiz, name='export_quiz'),
    # New URLs for quiz taking and results
    path('<int:pk>/take/', views.take_quiz, name='take_quiz'),
    path('attempt/<int:attempt_pk>/submit/', views.submit_quiz, name='submit_quiz'),
    path('attempt/<int:attempt_pk>/results/', views.quiz_results, name='quiz_results'),
    path('<int:pk>/attempts/', views.all_attempts, name='all_attempts'),
]
