from django.shortcuts import redirect
from django.contrib import messages
from accounts.models import UserModel
from .models import NewsFeed


class NewsAuthorRequiredMixin:
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

        post_id = kwargs.get('post_id')
        if post_id:
            post = NewsFeed.objects.filter(id=post_id).first()
            if not post:
                messages.error(request, 'Post not found.')
                return redirect('newsfeed_list')

            if user.is_teacher and post.author != user:
                messages.error(request, 'You are not the author of this post.')
                return redirect('newsfeed_detail', post_id=post_id)

        return super().dispatch(request, *args, **kwargs)