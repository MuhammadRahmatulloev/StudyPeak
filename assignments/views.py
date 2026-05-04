from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum
from accounts.permissions import SessionLoginRequiredMixin, get_current_user
from accounts.models import UserModel
from .models import Assignment, Question, Choice, AssignmentSubmission, Answer
from .permissions import AssignmentTeacherRequiredMixin, AssignmentAccessMixin, SubmissionOwnerRequiredMixin, QuizAccessMixin


class AssignmentListView(SessionLoginRequiredMixin, View):
    def get(self, request):
        user = get_current_user(request)
        if user.is_teacher:
            assignments = Assignment.objects.filter(teacher=user).select_related('subject', 'group')
        elif user.is_student:
            assignments = Assignment.objects.filter(
                group__memberships__user=user,
                is_published=True
            ).select_related('subject', 'group')
        else:
            assignments = Assignment.objects.all().select_related('subject', 'group')
        return render(request, 'assignments/assignment_list.html', {'assignments': assignments, 'user': user,})


class AssignmentCreateView(AssignmentTeacherRequiredMixin, View):
    def get(self, request):
        from materials.models import Subject
        from chat.models import Group
        user = get_current_user(request)
        if user.is_teacher:
            subjects = Subject.objects.filter(teacher=user)
            groups = Group.objects.filter(memberships__user=user)
        else:
            subjects = Subject.objects.all()
            groups = Group.objects.all()
        return render(request, 'assignments/assignment_create.html', {
            'subjects': subjects,
            'groups': groups,
            'type_choices': Assignment.TYPE_CHOICES,
        })

    def post(self, request):
        user = get_current_user(request)
        from materials.models import Subject
        from chat.models import Group

        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        subject_id = request.POST.get('subject_id')
        group_id = request.POST.get('group_id')
        assignment_type = request.POST.get('type', Assignment.HOMEWORK)
        deadline = request.POST.get('deadline') or None
        time_limit = request.POST.get('time_limit') or None

        if not title:
            messages.error(request, 'Title is required.')
            return redirect('assignment_create')

        subject = get_object_or_404(Subject, id=subject_id)
        group = get_object_or_404(Group, id=group_id)

        if assignment_type not in [Assignment.HOMEWORK, Assignment.TEST, Assignment.QUIZ]:
            assignment_type = Assignment.HOMEWORK

        assignment = Assignment.objects.create(
            title=title,
            description=description,
            teacher=user,
            subject=subject,
            group=group,
            type=assignment_type,
            deadline=deadline,
            time_limit=int(time_limit) if time_limit else None,
        )
        messages.success(request, f'Assignment "{assignment.title}" created.')
        return redirect('assignment_detail', assignment_id=assignment.id)


class AssignmentDetailView(AssignmentAccessMixin, View):
    def get(self, request, assignment_id):
        user = get_current_user(request)
        assignment = get_object_or_404(Assignment, id=assignment_id)
        questions = assignment.questions.prefetch_related('choices').all()

        submission = None
        if user.is_student:
            submission = AssignmentSubmission.objects.filter(student=user, assignment=assignment).first()

        submissions = None
        if user.is_teacher or user.is_admin_role:
            submissions = assignment.submissions.select_related('student').all()

        return render(request, 'assignments/assignment_detail.html', {
            'assignment': assignment,
            'questions': questions,
            'submission': submission,
            'submissions': submissions,
        })


class AssignmentUpdateView(AssignmentTeacherRequiredMixin, View):
    def get(self, request, assignment_id):
        from materials.models import Subject
        from chat.models import Group
        user = get_current_user(request)
        assignment = get_object_or_404(Assignment, id=assignment_id)
        if user.is_teacher:
            subjects = Subject.objects.filter(teacher=user)
            groups = Group.objects.filter(memberships__user=user)
        else:
            subjects = Subject.objects.all()
            groups = Group.objects.all()
        return render(request, 'assignments/assignment_update.html', {
            'assignment': assignment,
            'subjects': subjects,
            'groups': groups,
            'type_choices': Assignment.TYPE_CHOICES,
        })

    def post(self, request, assignment_id):
        assignment = get_object_or_404(Assignment, id=assignment_id)

        assignment.title = request.POST.get('title', assignment.title).strip()
        assignment.description = request.POST.get('description', assignment.description)
        assignment.type = request.POST.get('type', assignment.type)
        assignment.deadline = request.POST.get('deadline') or None
        time_limit = request.POST.get('time_limit') or None
        assignment.time_limit = int(time_limit) if time_limit else None
        assignment.save()

        messages.success(request, 'Assignment updated.')
        return redirect('assignment_detail', assignment_id=assignment_id)


class AssignmentDeleteView(AssignmentTeacherRequiredMixin, View):
    def post(self, request, assignment_id):
        assignment = get_object_or_404(Assignment, id=assignment_id)
        assignment.delete()
        messages.success(request, 'Assignment deleted.')
        return redirect('assignment_list')


class AssignmentPublishToggleView(AssignmentTeacherRequiredMixin, View):
    def post(self, request, assignment_id):
        assignment = get_object_or_404(Assignment, id=assignment_id)
        assignment.is_published = not assignment.is_published
        assignment.save()
        state = 'published' if assignment.is_published else 'unpublished'
        messages.success(request, f'Assignment {state}.')
        return redirect('assignment_detail', assignment_id=assignment_id)


class QuestionCreateView(AssignmentTeacherRequiredMixin, View):
    def get(self, request, assignment_id):
        assignment = get_object_or_404(Assignment, id=assignment_id)
        return render(request, 'assignments/question_create.html', {
            'assignment': assignment,
            'type_choices': Question.TYPE_CHOICES,
        })

    def post(self, request, assignment_id):
        assignment = get_object_or_404(Assignment, id=assignment_id)

        text = request.POST.get('text', '').strip()
        question_type = request.POST.get('type', Question.MCQ)
        order = request.POST.get('order', 0)
        score = request.POST.get('score', 1)

        if not text:
            messages.error(request, 'Question text is required.')
            return redirect('question_create', assignment_id=assignment_id)

        question = Question.objects.create(
            assignment=assignment,
            text=text,
            type=question_type,
            order=int(order),
            score=int(score),
        )
        messages.success(request, 'Question added.')
        return redirect('question_detail', assignment_id=assignment_id, question_id=question.id)


class QuestionDetailView(AssignmentTeacherRequiredMixin, View):
    def get(self, request, assignment_id, question_id):
        assignment = get_object_or_404(Assignment, id=assignment_id)
        question = get_object_or_404(Question, id=question_id, assignment=assignment)
        choices = question.choices.all()
        return render(request, 'assignments/question_detail.html', {
            'assignment': assignment,
            'question': question,
            'choices': choices,
        })


class QuestionUpdateView(AssignmentTeacherRequiredMixin, View):
    def get(self, request, assignment_id, question_id):
        assignment = get_object_or_404(Assignment, id=assignment_id)
        question = get_object_or_404(Question, id=question_id, assignment=assignment)
        return render(request, 'assignments/question_update.html', {
            'assignment': assignment,
            'question': question,
            'type_choices': Question.TYPE_CHOICES,
        })

    def post(self, request, assignment_id, question_id):
        assignment = get_object_or_404(Assignment, id=assignment_id)
        question = get_object_or_404(Question, id=question_id, assignment=assignment)

        question.text = request.POST.get('text', question.text).strip()
        question.type = request.POST.get('type', question.type)
        question.order = int(request.POST.get('order', question.order))
        question.score = int(request.POST.get('score', question.score))
        question.save()

        messages.success(request, 'Question updated.')
        return redirect('question_detail', assignment_id=assignment_id, question_id=question_id)


class QuestionDeleteView(AssignmentTeacherRequiredMixin, View):
    def post(self, request, assignment_id, question_id):
        assignment = get_object_or_404(Assignment, id=assignment_id)
        question = get_object_or_404(Question, id=question_id, assignment=assignment)
        question.delete()
        messages.success(request, 'Question deleted.')
        return redirect('assignment_detail', assignment_id=assignment_id)


class ChoiceCreateView(AssignmentTeacherRequiredMixin, View):
    def post(self, request, assignment_id, question_id):
        assignment = get_object_or_404(Assignment, id=assignment_id)
        question = get_object_or_404(Question, id=question_id, assignment=assignment)

        text = request.POST.get('text', '').strip()
        is_correct = request.POST.get('is_correct') == 'on'

        if not text:
            messages.error(request, 'Choice text is required.')
            return redirect('question_detail', assignment_id=assignment_id, question_id=question_id)

        Choice.objects.create(question=question, text=text, is_correct=is_correct)
        messages.success(request, 'Choice added.')
        return redirect('question_detail', assignment_id=assignment_id, question_id=question_id)


class ChoiceUpdateView(AssignmentTeacherRequiredMixin, View):
    def post(self, request, assignment_id, question_id, choice_id):
        assignment = get_object_or_404(Assignment, id=assignment_id)
        question = get_object_or_404(Question, id=question_id, assignment=assignment)
        choice = get_object_or_404(Choice, id=choice_id, question=question)

        choice.text = request.POST.get('text', choice.text).strip()
        choice.is_correct = request.POST.get('is_correct') == 'on'
        choice.save()

        messages.success(request, 'Choice updated.')
        return redirect('question_detail', assignment_id=assignment_id, question_id=question_id)


class ChoiceDeleteView(AssignmentTeacherRequiredMixin, View):
    def post(self, request, assignment_id, question_id, choice_id):
        assignment = get_object_or_404(Assignment, id=assignment_id)
        question = get_object_or_404(Question, id=question_id, assignment=assignment)
        choice = get_object_or_404(Choice, id=choice_id, question=question)
        choice.delete()
        messages.success(request, 'Choice deleted.')
        return redirect('question_detail', assignment_id=assignment_id, question_id=question_id)


class AssignmentStartView(AssignmentAccessMixin, View):
    def post(self, request, assignment_id):
        user = get_current_user(request)
        assignment = get_object_or_404(Assignment, id=assignment_id)

        if not user.is_student:
            messages.error(request, 'Only students can start assignments.')
            return redirect('assignment_detail', assignment_id=assignment_id)

        submission, created = AssignmentSubmission.objects.get_or_create(
            student=user,
            assignment=assignment,
            defaults={'status': AssignmentSubmission.PENDING, 'started_at': timezone.now()}
        )

        if not created and submission.status == AssignmentSubmission.SUBMITTED:
            messages.warning(request, 'You have already submitted this assignment.')
            return redirect('submission_detail', submission_id=submission.id)

        if created or not submission.started_at:
            submission.started_at = timezone.now()
            submission.save()

        if assignment.type == Assignment.QUIZ:
            return redirect('quiz_take', assignment_id=assignment_id)

        return redirect('assignment_take', assignment_id=assignment_id)


class AssignmentTakeView(AssignmentAccessMixin, View):
    def get(self, request, assignment_id):
        user = get_current_user(request)
        assignment = get_object_or_404(Assignment, id=assignment_id)

        if not user.is_student:
            return redirect('assignment_detail', assignment_id=assignment_id)

        submission = AssignmentSubmission.objects.filter(student=user, assignment=assignment).first()
        if not submission:
            messages.error(request, 'Please start the assignment first.')
            return redirect('assignment_detail', assignment_id=assignment_id)

        if submission.status == AssignmentSubmission.SUBMITTED:
            messages.warning(request, 'You have already submitted this assignment.')
            return redirect('submission_detail', submission_id=submission.id)

        questions = assignment.questions.prefetch_related('choices').all()
        existing_answers = Answer.objects.filter(submission=submission).select_related('question', 'selected_choice')
        answer_map = {a.question_id: a for a in existing_answers}

        return render(request, 'assignments/assignment_take.html', {
            'assignment': assignment,
            'questions': questions,
            'submission': submission,
            'answer_map': answer_map,
        })

    def post(self, request, assignment_id):
        user = get_current_user(request)
        assignment = get_object_or_404(Assignment, id=assignment_id)

        submission = get_object_or_404(AssignmentSubmission, student=user, assignment=assignment)

        if submission.status == AssignmentSubmission.SUBMITTED:
            messages.warning(request, 'Already submitted.')
            return redirect('submission_detail', submission_id=submission.id)

        questions = assignment.questions.prefetch_related('choices').all()
        total_score = 0

        for question in questions:
            answer, _ = Answer.objects.get_or_create(submission=submission, question=question)

            if question.type == Question.MCQ:
                choice_id = request.POST.get(f'question_{question.id}')
                if choice_id:
                    choice = Choice.objects.filter(id=choice_id, question=question).first()
                    if choice:
                        answer.selected_choice = choice
                        answer.is_correct = choice.is_correct
                        answer.score = question.score if choice.is_correct else 0
                        total_score += answer.score

            elif question.type == Question.TRUE_FALSE:
                choice_id = request.POST.get(f'question_{question.id}')
                if choice_id:
                    choice = Choice.objects.filter(id=choice_id, question=question).first()
                    if choice:
                        answer.selected_choice = choice
                        answer.is_correct = choice.is_correct
                        answer.score = question.score if choice.is_correct else 0
                        total_score += answer.score

            elif question.type == Question.TEXT:
                answer_text = request.POST.get(f'question_{question.id}', '').strip()
                answer.answer_text = answer_text
                answer.is_correct = None
                answer.score = 0

            answer.save()

        submission.total_score = total_score
        submission.submit()

        messages.success(request, 'Assignment submitted successfully!')
        return redirect('submission_detail', submission_id=submission.id)


class QuizTakeView(QuizAccessMixin, View):
    def get(self, request, assignment_id):
        user = get_current_user(request)
        assignment = get_object_or_404(Assignment, id=assignment_id)

        submission = AssignmentSubmission.objects.filter(student=user, assignment=assignment).first()
        if not submission:
            messages.error(request, 'Please start the quiz first.')
            return redirect('assignment_detail', assignment_id=assignment_id)

        questions = assignment.questions.prefetch_related('choices').all()

        return render(request, 'assignments/quiz_take.html', {
            'assignment': assignment,
            'questions': questions,
            'submission': submission,
            'time_limit_seconds': (assignment.time_limit or 0) * 60,
        })

    def post(self, request, assignment_id):
        user = get_current_user(request)
        assignment = get_object_or_404(Assignment, id=assignment_id)

        submission = get_object_or_404(AssignmentSubmission, student=user, assignment=assignment)

        if submission.status == AssignmentSubmission.SUBMITTED:
            messages.warning(request, 'Quiz already submitted.')
            return redirect('submission_detail', submission_id=submission.id)

        questions = assignment.questions.prefetch_related('choices').all()
        total_score = 0

        for question in questions:
            answer, _ = Answer.objects.get_or_create(submission=submission, question=question)

            if question.type in [Question.MCQ, Question.TRUE_FALSE]:
                choice_id = request.POST.get(f'question_{question.id}')
                if choice_id:
                    choice = Choice.objects.filter(id=choice_id, question=question).first()
                    if choice:
                        answer.selected_choice = choice
                        answer.is_correct = choice.is_correct
                        answer.score = question.score if choice.is_correct else 0
                        total_score += answer.score

            elif question.type == Question.TEXT:
                answer.answer_text = request.POST.get(f'question_{question.id}', '').strip()
                answer.is_correct = None
                answer.score = 0

            answer.save()

        submission.total_score = total_score
        submission.submit()

        messages.success(request, 'Quiz submitted!')
        return redirect('submission_detail', submission_id=submission.id)


class SubmissionListView(AssignmentTeacherRequiredMixin, View):
    def get(self, request, assignment_id):
        assignment = get_object_or_404(Assignment, id=assignment_id)
        submissions = assignment.submissions.select_related('student').all()
        return render(request, 'assignments/submission_list.html', {
            'assignment': assignment,
            'submissions': submissions,
        })


class SubmissionDetailView(SubmissionOwnerRequiredMixin, View):
    def get(self, request, submission_id):
        user = get_current_user(request)
        submission = get_object_or_404(AssignmentSubmission, id=submission_id)
        answers = submission.answers.select_related('question', 'selected_choice').all()

        return render(request, 'assignments/submission_detail.html', {
            'submission': submission,
            'answers': answers,
            'assignment': submission.assignment,
        })


class GradeTextAnswerView(AssignmentTeacherRequiredMixin, View):
    def post(self, request, submission_id, answer_id):
        user = get_current_user(request)
        submission = get_object_or_404(AssignmentSubmission, id=submission_id)
        answer = get_object_or_404(Answer, id=answer_id, submission=submission)

        if answer.question.type != Question.TEXT:
            messages.error(request, 'Only text answers can be manually graded.')
            return redirect('submission_detail', submission_id=submission_id)

        score = int(request.POST.get('score', 0))
        is_correct = request.POST.get('is_correct') == 'on'

        answer.score = min(score, answer.question.score)
        answer.is_correct = is_correct
        answer.save()

        total = submission.answers.aggregate(total=Sum('score'))['total'] or 0
        submission.total_score = total
        submission.status = AssignmentSubmission.GRADED
        submission.save()

        messages.success(request, 'Answer graded.')
        return redirect('submission_detail', submission_id=submission_id)