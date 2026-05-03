from accounts.models import Notification
from chat.models import Friendship, GroupInvitation

def notifications_count(request):
    if not request.session.get('user_id'):
        return {}
    try:
        from accounts.models import UserModel
        user = UserModel.objects.get(id=request.session['user_id'])
        count = (
            user.notifications.filter(is_read=False).count() +
            Friendship.objects.filter(receiver=user, status=Friendship.PENDING).count() +
            GroupInvitation.objects.filter(receiver=user, status=GroupInvitation.PENDING).count()
        )
        return {'unread_notifications_count': count}
    except:
        return {}