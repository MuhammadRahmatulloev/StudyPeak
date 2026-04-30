from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from django.contrib import messages
from accounts.permissions import SessionLoginRequiredMixin, TeacherOrAdminRequiredMixin, get_current_user
from accounts.models import UserModel, Profile
from .models import NewsFeed


class HomeView(SessionLoginRequiredMixin, View):
    def get(self, request):
        user = get_current_user(request)
        profile = Profile.objects.filter(user=user).first()
        posts = NewsFeed.objects.filter(is_active=True).select_related('author')

        from chat.models import Group, GroupInvitation
        from assignments.models import AssignmentSubmission, Assignment
        from crm.models import Enrollment

        groups = Group.objects.filter(memberships__user=user)
        invitations = GroupInvitation.objects.filter(receiver=user, status=GroupInvitation.PENDING)

        if user.is_student:
            assignments = Assignment.objects.filter(
                group__memberships__user=user,
                is_published=True
            ).select_related('subject', 'group').order_by('-created_at')[:5]
            enrollments = Enrollment.objects.filter(
                student=user,
                status=Enrollment.APPROVED
            ).select_related('course')
        else:
            assignments = Assignment.objects.filter(
                teacher=user
            ).select_related('subject', 'group').order_by('-created_at')[:5]
            enrollments = None

        from accounts.models import Notification
        notifications = Notification.objects.filter(user=user, is_read=False).order_by('-created_at')[:5]

        return render(request, 'core/home.html', {
            'user': user,
            'profile': profile,
            'posts': posts,
            'groups': groups,
            'invitations': invitations,
            'assignments': assignments,
            'enrollments': enrollments,
            'notifications': notifications,
        })


class NewsFeedListView(SessionLoginRequiredMixin, View):
    def get(self, request):
        user = get_current_user(request)
        if user.is_admin_role:
            posts = NewsFeed.objects.select_related('author').all()
        else:
            posts = NewsFeed.objects.filter(is_active=True).select_related('author')
        return render(request, 'core/newsfeed_list.html', {
            'posts': posts,
        })


class NewsFeedCreateView(TeacherOrAdminRequiredMixin, View):
    def get(self, request):
        return render(request, 'core/newsfeed_create.html', {
            'type_choices': NewsFeed.TYPE_CHOICES,
        })

    def post(self, request):
        user = get_current_user(request)
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        post_type = request.POST.get('type', NewsFeed.TEXT)

        if not title or not content:
            messages.error(request, 'Title and content are required.')
            return render(request, 'core/newsfeed_create.html', {
                'type_choices': NewsFeed.TYPE_CHOICES,
            })

        if post_type not in [t[0] for t in NewsFeed.TYPE_CHOICES]:
            post_type = NewsFeed.TEXT

        post = NewsFeed(
            author=user,
            title=title,
            content=content,
            type=post_type,
        )

        if request.FILES.get('image'):
            post.image = request.FILES['image']

        post.save()
        messages.success(request, 'Post published.')
        return redirect('newsfeed_detail', post_id=post.id)


class NewsFeedDetailView(SessionLoginRequiredMixin, View):
    def get(self, request, post_id):
        user = get_current_user(request)
        if user.is_admin_role:
            post = get_object_or_404(NewsFeed, id=post_id)
        else:
            post = get_object_or_404(NewsFeed, id=post_id, is_active=True)
        return render(request, 'core/newsfeed_detail.html', {
            'post': post,
        })


class NewsFeedUpdateView(TeacherOrAdminRequiredMixin, View):
    def get(self, request, post_id):
        user = get_current_user(request)
        post = get_object_or_404(NewsFeed, id=post_id)

        if user.is_teacher and post.author != user:
            messages.error(request, 'Access denied.')
            return redirect('newsfeed_detail', post_id=post_id)

        return render(request, 'core/newsfeed_update.html', {
            'post': post,
            'type_choices': NewsFeed.TYPE_CHOICES,
        })

    def post(self, request, post_id):
        user = get_current_user(request)
        post = get_object_or_404(NewsFeed, id=post_id)

        if user.is_teacher and post.author != user:
            messages.error(request, 'Access denied.')
            return redirect('newsfeed_detail', post_id=post_id)

        post.title = request.POST.get('title', post.title).strip()
        post.content = request.POST.get('content', post.content).strip()
        post.type = request.POST.get('type', post.type)
        post.is_active = request.POST.get('is_active') == 'on'

        if request.FILES.get('image'):
            post.image = request.FILES['image']

        post.save()
        messages.success(request, 'Post updated.')
        return redirect('newsfeed_detail', post_id=post_id)


class NewsFeedDeleteView(TeacherOrAdminRequiredMixin, View):
    def post(self, request, post_id):
        user = get_current_user(request)
        post = get_object_or_404(NewsFeed, id=post_id)

        if user.is_teacher and post.author != user:
            messages.error(request, 'Access denied.')
            return redirect('newsfeed_detail', post_id=post_id)

        post.delete()
        messages.success(request, 'Post deleted.')
        return redirect('newsfeed_list')


class NotificationMarkReadView(SessionLoginRequiredMixin, View):
    def post(self, request, notification_id):
        user = get_current_user(request)
        from accounts.models import Notification
        notification = get_object_or_404(Notification, id=notification_id, user=user)
        notification.is_read = True
        notification.save()
        return redirect('home')


class NotificationMarkAllReadView(SessionLoginRequiredMixin, View):
    def post(self, request):
        user = get_current_user(request)
        from accounts.models import Notification
        Notification.objects.filter(user=user, is_read=False).update(is_read=True)
        return redirect('home')