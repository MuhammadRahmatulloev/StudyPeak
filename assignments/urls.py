from django.urls import path
from .views import *

urlpatterns = [
    path('', AssignmentListView.as_view(), name='assignment_list'),
    path('create/', AssignmentCreateView.as_view(), name='assignment_create'),
    path('<int:assignment_id>/', AssignmentDetailView.as_view(), name='assignment_detail'),
    path('<int:assignment_id>/update/', AssignmentUpdateView.as_view(), name='assignment_update'),
    path('<int:assignment_id>/delete/', AssignmentDeleteView.as_view(), name='assignment_delete'),
    path('<int:assignment_id>/publish/', AssignmentPublishToggleView.as_view(), name='assignment_publish'),

    path('<int:assignment_id>/start/', AssignmentStartView.as_view(), name='assignment_start'),
    path('<int:assignment_id>/take/', AssignmentTakeView.as_view(), name='assignment_take'),
    path('<int:assignment_id>/quiz/', QuizTakeView.as_view(), name='quiz_take'),

    path('<int:assignment_id>/questions/create/', QuestionCreateView.as_view(), name='question_create'),
    path('<int:assignment_id>/questions/<int:question_id>/', QuestionDetailView.as_view(), name='question_detail'),
    path('<int:assignment_id>/questions/<int:question_id>/update/', QuestionUpdateView.as_view(), name='question_update'),
    path('<int:assignment_id>/questions/<int:question_id>/delete/', QuestionDeleteView.as_view(), name='question_delete'),

    path('<int:assignment_id>/questions/<int:question_id>/choices/create/', ChoiceCreateView.as_view(), name='choice_create'),
    path('<int:assignment_id>/questions/<int:question_id>/choices/<int:choice_id>/update/', ChoiceUpdateView.as_view(), name='choice_update'),
    path('<int:assignment_id>/questions/<int:question_id>/choices/<int:choice_id>/delete/', ChoiceDeleteView.as_view(), name='choice_delete'),

    path('submissions/<int:submission_id>/', SubmissionDetailView.as_view(), name='submission_detail'),
    path('<int:assignment_id>/submissions/', SubmissionListView.as_view(), name='submission_list'),
    path('submissions/<int:submission_id>/answers/<int:answer_id>/grade/', GradeTextAnswerView.as_view(), name='grade_answer'),
]