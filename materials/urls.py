from django.urls import path
from .views import *

urlpatterns = [
    path('', SubjectListView.as_view(), name='subject_list'),
    path('create/', SubjectCreateView.as_view(), name='subject_create'),
    path('<int:subject_id>/', SubjectDetailView.as_view(), name='subject_detail'),
    path('<int:subject_id>/update/', SubjectUpdateView.as_view(), name='subject_update'),
    path('<int:subject_id>/delete/', SubjectDeleteView.as_view(), name='subject_delete'),

    path('<int:subject_id>/lessons/create/', LessonCreateView.as_view(), name='lesson_create'),
    path('<int:subject_id>/lessons/<int:lesson_id>/', LessonDetailView.as_view(), name='lesson_detail'),
    path('<int:subject_id>/lessons/<int:lesson_id>/update/', LessonUpdateView.as_view(), name='lesson_update'),
    path('<int:subject_id>/lessons/<int:lesson_id>/delete/', LessonDeleteView.as_view(), name='lesson_delete'),

    path('<int:subject_id>/lessons/<int:lesson_id>/materials/create/', MaterialCreateView.as_view(), name='material_create'),
    path('<int:subject_id>/lessons/<int:lesson_id>/materials/<int:material_id>/update/', MaterialUpdateView.as_view(), name='material_update'),
    path('<int:subject_id>/lessons/<int:lesson_id>/materials/<int:material_id>/delete/', MaterialDeleteView.as_view(), name='material_delete'),
]