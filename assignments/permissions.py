from django.shortcuts import redirect
from django.contrib import messages
from accounts.models import UserModel
from .models import Assignment, AssignmentSubmission


class AssignmentTeacherRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        user_id = request.session.get('user_id')
        if not user_id:
            messages.error(request, 'Please login first!')
            return redirect('login')

        user = UserModel.objects.filter(id=user_id).first()
        if not user:
            messages.error(request, 'Please login first!')
            return redirect('login')

        if not (user.is_teacher or user.is_admin_role):
            messages.error(request, 'Teacher or admin access required.')
            return redirect('home')

        assignment_id = kwargs.get('assignment_id')
        if assignment_id:
            assignment = Assignment.objects.filter(id=assignment_id).first()
            if not assignment:
                messages.error(request, 'Assignment not found.')
                return redirect('assignment_list')

            if user.is_teacher and assignment.teacher != user:
                messages.error(request, 'You are not the owner of this assignment.')
                return redirect('assignment_list')

        return super().dispatch(request, *args, **kwargs)


class AssignmentAccessMixin:
    def dispatch(self, request, *args, **kwargs):
        user_id = request.session.get('user_id')
        if not user_id:
            messages.error(request, 'Please login first!')
            return redirect('login')

        user = UserModel.objects.filter(id=user_id).first()
        if not user:
            messages.error(request, 'Please login first!')
            return redirect('login')

        assignment_id = kwargs.get('assignment_id')
        if assignment_id:
            assignment = Assignment.objects.filter(id=assignment_id).first()
            if not assignment:
                messages.error(request, 'Assignment not found.')
                return redirect('assignment_list')

            if not assignment.is_published and user.is_student:
                messages.error(request, 'This assignment is not published yet.')
                return redirect('assignment_list')

            if user.is_student:
                in_group = assignment.group.memberships.filter(user=user).exists()
                if not in_group:
                    messages.error(request, 'You are not a member of this group.')
                    return redirect('assignment_list')

            if user.is_teacher and assignment.teacher != user and not user.is_admin_role:
                messages.error(request, 'Access denied.')
                return redirect('assignment_list')

        return super().dispatch(request, *args, **kwargs)


class SubmissionOwnerRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        user_id = request.session.get('user_id')
        if not user_id:
            messages.error(request, 'Please login first!')
            return redirect('login')

        user = UserModel.objects.filter(id=user_id).first()
        if not user:
            messages.error(request, 'Please login first!')
            return redirect('login')

        submission_id = kwargs.get('submission_id')
        if submission_id:
            submission = AssignmentSubmission.objects.filter(id=submission_id).first()
            if not submission:
                messages.error(request, 'Submission not found.')
                return redirect('assignment_list')

            if user.is_student and submission.student != user:
                messages.error(request, 'This is not your submission.')
                return redirect('assignment_list')

            if user.is_teacher:
                if submission.assignment.teacher != user and not user.is_admin_role:
                    messages.error(request, 'Access denied.')
                    return redirect('assignment_list')

        return super().dispatch(request, *args, **kwargs)


class QuizAccessMixin:
    def dispatch(self, request, *args, **kwargs):
        user_id = request.session.get('user_id')
        if not user_id:
            messages.error(request, 'Please login first!')
            return redirect('login')

        user = UserModel.objects.filter(id=user_id).first()
        if not user:
            messages.error(request, 'Please login first!')
            return redirect('login')

        if not user.is_student:
            messages.error(request, 'Only students can take quizzes.')
            return redirect('home')

        assignment_id = kwargs.get('assignment_id')
        if assignment_id:
            assignment = Assignment.objects.filter(id=assignment_id).first()
            if not assignment:
                messages.error(request, 'Assignment not found.')
                return redirect('assignment_list')

            if assignment.type != assignment.QUIZ:
                messages.error(request, 'This assignment is not a quiz.')
                return redirect('assignment_detail', assignment_id=assignment_id)

            if not assignment.is_published:
                messages.error(request, 'This quiz is not published yet.')
                return redirect('assignment_list')

            in_group = assignment.group.memberships.filter(user=user).exists()
            if not in_group:
                messages.error(request, 'You are not a member of this group.')
                return redirect('assignment_list')

            already_submitted = AssignmentSubmission.objects.filter(
                student=user,
                assignment=assignment,
                status=AssignmentSubmission.SUBMITTED
            ).exists()

            if already_submitted:
                messages.warning(request, 'You have already submitted this quiz.')
                return redirect('assignment_detail', assignment_id=assignment_id)

        return super().dispatch(request, *args, **kwargs)