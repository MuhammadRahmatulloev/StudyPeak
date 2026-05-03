from .models import Notification


def create_notification(user, notif_type, message):
    Notification.objects.create(
        user=user,
        type=notif_type,
        message=message,
    )


def notify_enrollment_request(student, course_title, teacher):
    create_notification(
        user=teacher,
        notif_type=Notification.ENROLLMENT_REQUEST,
        message=f'{student.username} has requested to enroll in "{course_title}".',
    )


def notify_enrollment_invite(student, course_title):
    create_notification(
        user=student,
        notif_type=Notification.ENROLLMENT_INVITE,
        message=f'You have been invited to enroll in "{course_title}".',
    )


def notify_enrollment_approved(student, course_title):
    create_notification(
        user=student,
        notif_type=Notification.ENROLLMENT_APPROVED,
        message=f'Your enrollment in "{course_title}" has been approved! 🎉',
    )


def notify_enrollment_rejected(student, course_title):
    create_notification(
        user=student,
        notif_type=Notification.ENROLLMENT_REJECTED,
        message=f'Your enrollment request for "{course_title}" was declined.',
    )