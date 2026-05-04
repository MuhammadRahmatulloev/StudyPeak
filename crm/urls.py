from django.urls import path
from .views import *

urlpatterns = [
    path('', CourseListView.as_view(), name='course_list'),
    path('create/', CourseCreateView.as_view(), name='course_create'),
    path('<int:course_id>/', CourseDetailView.as_view(), name='course_detail'),
    path('<int:course_id>/update/', CourseUpdateView.as_view(), name='course_update'),
    path('<int:course_id>/delete/', CourseDeleteView.as_view(), name='course_delete'),

    path('<int:course_id>/enroll/', EnrollRequestView.as_view(), name='enroll_request'),
    path('<int:course_id>/invite/', EnrollInviteView.as_view(), name='enroll_invite'),
    path('enrollment/<int:enrollment_id>/approve/', EnrollApproveView.as_view(), name='enroll_approve'),
    path('enrollment/<int:enrollment_id>/reject/', EnrollRejectView.as_view(), name='enroll_reject'),
    path('enrollment/<int:enrollment_id>/remove/', EnrollRemoveView.as_view(), name='enroll_remove'),
    path('enrollment/<int:enrollment_id>/accept-invite/', EnrollAcceptInviteView.as_view(), name='enroll_accept_invite'),
    path('enrollment/<int:enrollment_id>/reject-invite/', EnrollRejectInviteView.as_view(), name='enroll_reject_invite'),

    path('<int:course_id>/period/create/', CoursePeriodCreateView.as_view(), name='period_create'),
    path('period/<int:period_id>/update/', CoursePeriodUpdateView.as_view(), name='period_update'),
    path('period/<int:period_id>/delete/', CoursePeriodDeleteView.as_view(), name='period_delete'),

    path('period/<int:period_id>/journal/', WeeklyJournalView.as_view(), name='weekly_journal'),
    path('period/<int:period_id>/my-journal/', StudentJournalView.as_view(), name='student_journal'),

    path('period/<int:period_id>/grades/', GradeListView.as_view(), name='grade_list'),
    path('period/<int:period_id>/grades/create/', GradeCreateView.as_view(), name='grade_create'),

    path('period/<int:period_id>/attendance/', AttendanceView.as_view(), name='attendance'),
    path('period/<int:period_id>/my-attendance/', StudentAttendanceView.as_view(), name='student_attendance'),

    path('admin-invitation/<int:invitation_id>/accept/', AcceptCourseAdminInvitationView.as_view(), name='course_admin_invite_accept'),
    path('admin-invitation/<int:invitation_id>/reject/', RejectCourseAdminInvitationView.as_view(), name='course_admin_invite_reject'),
    path('<int:course_id>/search-students/', SearchStudentsView.as_view(), name='search_students'),
]