from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from django.contrib import messages
from accounts.permissions import SessionLoginRequiredMixin, TeacherOrAdminRequiredMixin, get_current_user
from .models import Subject, Lesson, Material


class SubjectListView(SessionLoginRequiredMixin, View):
    def get(self, request):
        user = get_current_user(request)
        if user.is_teacher:
            subjects = Subject.objects.filter(teacher=user)
        elif user.is_student:
            subjects = Subject.objects.filter(
                group__memberships__user=user,
                is_active=True
            ).distinct()
        else:
            subjects = Subject.objects.all()
        return render(request, 'materials/subject_list.html', {'subjects': subjects})


class SubjectCreateView(TeacherOrAdminRequiredMixin, View):
    def get(self, request):
        from chat.models import Group
        user = get_current_user(request)
        if user.is_teacher:
            groups = Group.objects.filter(memberships__user=user)
        else:
            groups = Group.objects.all()
        return render(request, 'materials/subject_create.html', {'groups': groups})

    def post(self, request):
        from chat.models import Group
        user = get_current_user(request)
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        group_id = request.POST.get('group_id') or None

        if not title:
            messages.error(request, 'Title is required.')
            return redirect('subject_create')

        group = None
        if group_id:
            group = get_object_or_404(Group, id=group_id)

        subject = Subject.objects.create(
            title=title,
            description=description,
            teacher=user,
            group=group,
        )

        if request.FILES.get('cover'):
            subject.cover = request.FILES['cover']
            subject.save()

        messages.success(request, f'Subject "{subject.title}" created.')
        return redirect('subject_detail', subject_id=subject.id)


class SubjectDetailView(SessionLoginRequiredMixin, View):
    def get(self, request, subject_id):
        user = get_current_user(request)
        subject = get_object_or_404(Subject, id=subject_id)

        if user.is_student:
            if subject.group and not subject.group.memberships.filter(user=user).exists():
                messages.error(request, 'You do not have access to this subject.')
                return redirect('subject_list')

        lessons = subject.lessons.all()
        return render(request, 'materials/subject_detail.html', {
            'subject': subject,
            'lessons': lessons,
        })


class SubjectUpdateView(TeacherOrAdminRequiredMixin, View):
    def get(self, request, subject_id):
        from chat.models import Group
        user = get_current_user(request)
        subject = get_object_or_404(Subject, id=subject_id)

        if user.is_teacher and subject.teacher != user:
            messages.error(request, 'Access denied.')
            return redirect('subject_detail', subject_id=subject_id)

        if user.is_teacher:
            groups = Group.objects.filter(memberships__user=user)
        else:
            groups = Group.objects.all()

        return render(request, 'materials/subject_update.html', {
            'subject': subject,
            'groups': groups,
        })

    def post(self, request, subject_id):
        from chat.models import Group
        user = get_current_user(request)
        subject = get_object_or_404(Subject, id=subject_id)

        if user.is_teacher and subject.teacher != user:
            messages.error(request, 'Access denied.')
            return redirect('subject_detail', subject_id=subject_id)

        subject.title = request.POST.get('title', subject.title).strip()
        subject.description = request.POST.get('description', subject.description)
        subject.is_active = request.POST.get('is_active') == 'on'

        group_id = request.POST.get('group_id') or None
        if group_id:
            subject.group = get_object_or_404(Group, id=group_id)
        else:
            subject.group = None

        if request.FILES.get('cover'):
            subject.cover = request.FILES['cover']

        subject.save()
        messages.success(request, 'Subject updated.')
        return redirect('subject_detail', subject_id=subject_id)


class SubjectDeleteView(TeacherOrAdminRequiredMixin, View):
    def post(self, request, subject_id):
        user = get_current_user(request)
        subject = get_object_or_404(Subject, id=subject_id)

        if user.is_teacher and subject.teacher != user:
            messages.error(request, 'Access denied.')
            return redirect('subject_detail', subject_id=subject_id)

        subject.delete()
        messages.success(request, 'Subject deleted.')
        return redirect('subject_list')


class LessonCreateView(TeacherOrAdminRequiredMixin, View):
    def get(self, request, subject_id):
        subject = get_object_or_404(Subject, id=subject_id)
        return render(request, 'materials/lesson_create.html', {'subject': subject})

    def post(self, request, subject_id):
        user = get_current_user(request)
        subject = get_object_or_404(Subject, id=subject_id)

        if user.is_teacher and subject.teacher != user:
            messages.error(request, 'Access denied.')
            return redirect('subject_detail', subject_id=subject_id)

        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        order = request.POST.get('order', 0)

        if not title:
            messages.error(request, 'Title is required.')
            return render(request, 'materials/lesson_create.html', {'subject': subject})

        lesson = Lesson.objects.create(
            subject=subject,
            title=title,
            description=description,
            order=int(order),
        )
        messages.success(request, f'Lesson "{lesson.title}" created.')
        return redirect('lesson_detail', subject_id=subject_id, lesson_id=lesson.id)


class LessonDetailView(SessionLoginRequiredMixin, View):
    def get(self, request, subject_id, lesson_id):
        user = get_current_user(request)
        subject = get_object_or_404(Subject, id=subject_id)
        lesson = get_object_or_404(Lesson, id=lesson_id, subject=subject)

        if user.is_student:
            if subject.group and not subject.group.memberships.filter(user=user).exists():
                messages.error(request, 'You do not have access to this lesson.')
                return redirect('subject_list')

        materials = lesson.materials.all()

        from dashboard.models import LessonView, ActivityLog
        LessonView.objects.get_or_create(user=user, lesson=lesson)
        ActivityLog.objects.create(
            user=user,
            action=ActivityLog.VIEWED_LESSON,
            description=f'Viewed lesson: {lesson.title}',
        )

        return render(request, 'materials/lesson_detail.html', {
            'subject': subject,
            'lesson': lesson,
            'materials': materials,
        })


class LessonUpdateView(TeacherOrAdminRequiredMixin, View):
    def get(self, request, subject_id, lesson_id):
        user = get_current_user(request)
        subject = get_object_or_404(Subject, id=subject_id)
        lesson = get_object_or_404(Lesson, id=lesson_id, subject=subject)

        if user.is_teacher and subject.teacher != user:
            messages.error(request, 'Access denied.')
            return redirect('lesson_detail', subject_id=subject_id, lesson_id=lesson_id)

        return render(request, 'materials/lesson_update.html', {
            'subject': subject,
            'lesson': lesson,
        })

    def post(self, request, subject_id, lesson_id):
        user = get_current_user(request)
        subject = get_object_or_404(Subject, id=subject_id)
        lesson = get_object_or_404(Lesson, id=lesson_id, subject=subject)

        if user.is_teacher and subject.teacher != user:
            messages.error(request, 'Access denied.')
            return redirect('lesson_detail', subject_id=subject_id, lesson_id=lesson_id)

        lesson.title = request.POST.get('title', lesson.title).strip()
        lesson.description = request.POST.get('description', lesson.description)
        lesson.order = int(request.POST.get('order', lesson.order))
        lesson.save()

        messages.success(request, 'Lesson updated.')
        return redirect('lesson_detail', subject_id=subject_id, lesson_id=lesson_id)


class LessonDeleteView(TeacherOrAdminRequiredMixin, View):
    def post(self, request, subject_id, lesson_id):
        user = get_current_user(request)
        subject = get_object_or_404(Subject, id=subject_id)
        lesson = get_object_or_404(Lesson, id=lesson_id, subject=subject)

        if user.is_teacher and subject.teacher != user:
            messages.error(request, 'Access denied.')
            return redirect('lesson_detail', subject_id=subject_id, lesson_id=lesson_id)

        lesson.delete()
        messages.success(request, 'Lesson deleted.')
        return redirect('subject_detail', subject_id=subject_id)


class MaterialCreateView(TeacherOrAdminRequiredMixin, View):
    def get(self, request, subject_id, lesson_id):
        subject = get_object_or_404(Subject, id=subject_id)
        lesson = get_object_or_404(Lesson, id=lesson_id, subject=subject)
        return render(request, 'materials/material_create.html', {
            'subject': subject,
            'lesson': lesson,
            'type_choices': Material.TYPE_CHOICES,
        })

    def post(self, request, subject_id, lesson_id):
        user = get_current_user(request)
        subject = get_object_or_404(Subject, id=subject_id)
        lesson = get_object_or_404(Lesson, id=lesson_id, subject=subject)

        if user.is_teacher and subject.teacher != user:
            messages.error(request, 'Access denied.')
            return redirect('lesson_detail', subject_id=subject_id, lesson_id=lesson_id)

        title = request.POST.get('title', '').strip()
        material_type = request.POST.get('type', '')
        order = request.POST.get('order', 0)

        if not title:
            messages.error(request, 'Title is required.')
            return redirect('material_create', subject_id=subject_id, lesson_id=lesson_id)

        if material_type not in [t[0] for t in Material.TYPE_CHOICES]:
            messages.error(request, 'Invalid material type.')
            return redirect('material_create', subject_id=subject_id, lesson_id=lesson_id)

        material = Material(
            lesson=lesson,
            title=title,
            type=material_type,
            order=int(order),
        )

        if material_type == Material.LINK:
            material.url = request.POST.get('url', '').strip()
        elif material_type == Material.TEXT:
            material.content = request.POST.get('content', '').strip()
        elif material_type in [Material.PDF, Material.IMAGE, Material.VIDEO]:
            if request.FILES.get('file'):
                material.file = request.FILES['file']

        material.save()
        messages.success(request, f'Material "{material.title}" added.')
        return redirect('lesson_detail', subject_id=subject_id, lesson_id=lesson_id)


class MaterialUpdateView(TeacherOrAdminRequiredMixin, View):
    def get(self, request, subject_id, lesson_id, material_id):
        user = get_current_user(request)
        subject = get_object_or_404(Subject, id=subject_id)
        lesson = get_object_or_404(Lesson, id=lesson_id, subject=subject)
        material = get_object_or_404(Material, id=material_id, lesson=lesson)

        if user.is_teacher and subject.teacher != user:
            messages.error(request, 'Access denied.')
            return redirect('lesson_detail', subject_id=subject_id, lesson_id=lesson_id)

        return render(request, 'materials/material_update.html', {
            'subject': subject,
            'lesson': lesson,
            'material': material,
            'type_choices': Material.TYPE_CHOICES,
        })

    def post(self, request, subject_id, lesson_id, material_id):
        user = get_current_user(request)
        subject = get_object_or_404(Subject, id=subject_id)
        lesson = get_object_or_404(Lesson, id=lesson_id, subject=subject)
        material = get_object_or_404(Material, id=material_id, lesson=lesson)

        if user.is_teacher and subject.teacher != user:
            messages.error(request, 'Access denied.')
            return redirect('lesson_detail', subject_id=subject_id, lesson_id=lesson_id)

        material.title = request.POST.get('title', material.title).strip()
        material.order = int(request.POST.get('order', material.order))

        if material.type == Material.LINK:
            material.url = request.POST.get('url', material.url).strip()
        elif material.type == Material.TEXT:
            material.content = request.POST.get('content', material.content).strip()
        elif material.type in [Material.PDF, Material.IMAGE, Material.VIDEO]:
            if request.FILES.get('file'):
                material.file = request.FILES['file']

        material.save()
        messages.success(request, 'Material updated.')
        return redirect('lesson_detail', subject_id=subject_id, lesson_id=lesson_id)


class MaterialDeleteView(TeacherOrAdminRequiredMixin, View):
    def post(self, request, subject_id, lesson_id, material_id):
        user = get_current_user(request)
        subject = get_object_or_404(Subject, id=subject_id)
        lesson = get_object_or_404(Lesson, id=lesson_id, subject=subject)
        material = get_object_or_404(Material, id=material_id, lesson=lesson)

        if user.is_teacher and subject.teacher != user:
            messages.error(request, 'Access denied.')
            return redirect('lesson_detail', subject_id=subject_id, lesson_id=lesson_id)

        material.delete()
        messages.success(request, 'Material deleted.')
        return redirect('lesson_detail', subject_id=subject_id, lesson_id=lesson_id)