from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from django.contrib import messages
from accounts.permissions import SessionLoginRequiredMixin, TeacherOrAdminRequiredMixin, get_current_user
from accounts.models import UserModel, Profile
from .models import Product, Purchase, CoinTransaction, Achievement, UserAchievement


class ProductListView(SessionLoginRequiredMixin, View):
    def get(self, request):
        user = get_current_user(request)
        if user.is_admin_role:
            products = Product.objects.all().select_related('course', 'created_by')
        elif user.is_teacher:
            products = Product.objects.filter(
                is_active=True
            ).select_related('course', 'created_by')
        else:
            from crm.models import Enrollment
            enrolled_course_ids = Enrollment.objects.filter(
                student=user, status=Enrollment.APPROVED
            ).values_list('course_id', flat=True)
            products = Product.objects.filter(
                is_active=True
            ).filter(
                models_q_global_or_enrolled(enrolled_course_ids)
            ).select_related('course', 'created_by')

        profile = Profile.objects.filter(user=user).first()
        return render(request, 'shop/product_list.html', {
            'products': products,
            'profile': profile,
        })


def models_q_global_or_enrolled(enrolled_course_ids):
    from django.db.models import Q
    return Q(type=Product.GLOBAL) | Q(course_id__in=enrolled_course_ids)


class ProductDetailView(SessionLoginRequiredMixin, View):
    def get(self, request, product_id):
        user = get_current_user(request)
        product = get_object_or_404(Product, id=product_id)

        if not user.is_admin_role:
            if not product.is_active:
                messages.error(request, 'This product is not available.')
                return redirect('product_list')

            if product.type == Product.COURSE:
                from crm.models import Enrollment
                enrolled = Enrollment.objects.filter(
                    student=user,
                    course=product.course,
                    status=Enrollment.APPROVED
                ).exists()
                if not enrolled and not user.is_teacher:
                    messages.error(request, 'This product is only available for course members.')
                    return redirect('product_list')

        profile = Profile.objects.filter(user=user).first()
        already_purchased = Purchase.objects.filter(
            user=user, product=product, status=Purchase.COMPLETED
        ).exists()

        return render(request, 'shop/product_detail.html', {
            'product': product,
            'profile': profile,
            'already_purchased': already_purchased,
        })


class ProductCreateView(TeacherOrAdminRequiredMixin, View):
    def get(self, request):
        user = get_current_user(request)
        from crm.models import Course
        if user.is_teacher:
            courses = Course.objects.filter(teacher=user, is_active=True)
        else:
            courses = Course.objects.filter(is_active=True)
        return render(request, 'shop/product_create.html', {
            'courses': courses,
            'type_choices': Product.TYPE_CHOICES,
        })

    def post(self, request):
        user = get_current_user(request)
        from crm.models import Course

        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        price = request.POST.get('price', 0)
        product_type = request.POST.get('type', Product.GLOBAL)
        course_id = request.POST.get('course_id') or None
        stock = request.POST.get('stock', 0)

        if not name:
            messages.error(request, 'Product name is required.')
            return redirect('product_create')

        if product_type not in [Product.GLOBAL, Product.COURSE]:
            product_type = Product.GLOBAL

        course = None
        if product_type == Product.COURSE and course_id:
            course = get_object_or_404(Course, id=course_id)
            if user.is_teacher and course.teacher != user:
                messages.error(request, 'Access denied.')
                return redirect('product_list')

        product = Product(
            name=name,
            description=description,
            price=int(price),
            type=product_type,
            course=course,
            stock=int(stock),
            created_by=user,
        )

        if request.FILES.get('image'):
            product.image = request.FILES['image']

        product.save()
        messages.success(request, f'Product "{product.name}" created.')
        return redirect('product_detail', product_id=product.id)


class ProductUpdateView(TeacherOrAdminRequiredMixin, View):
    def get(self, request, product_id):
        user = get_current_user(request)
        product = get_object_or_404(Product, id=product_id)

        if user.is_teacher and product.created_by != user:
            messages.error(request, 'Access denied.')
            return redirect('product_detail', product_id=product_id)

        from crm.models import Course
        if user.is_teacher:
            courses = Course.objects.filter(teacher=user, is_active=True)
        else:
            courses = Course.objects.filter(is_active=True)

        return render(request, 'shop/product_update.html', {
            'product': product,
            'courses': courses,
            'type_choices': Product.TYPE_CHOICES,
        })

    def post(self, request, product_id):
        user = get_current_user(request)
        product = get_object_or_404(Product, id=product_id)

        if user.is_teacher and product.created_by != user:
            messages.error(request, 'Access denied.')
            return redirect('product_detail', product_id=product_id)

        product.name = request.POST.get('name', product.name).strip()
        product.description = request.POST.get('description', product.description)
        product.price = int(request.POST.get('price', product.price))
        product.stock = int(request.POST.get('stock', product.stock))
        product.is_active = request.POST.get('is_active') == 'on'

        if request.FILES.get('image'):
            product.image = request.FILES['image']

        product.save()
        messages.success(request, 'Product updated.')
        return redirect('product_detail', product_id=product_id)


class ProductDeleteView(TeacherOrAdminRequiredMixin, View):
    def post(self, request, product_id):
        user = get_current_user(request)
        product = get_object_or_404(Product, id=product_id)

        if user.is_teacher and product.created_by != user:
            messages.error(request, 'Access denied.')
            return redirect('product_detail', product_id=product_id)

        product.delete()
        messages.success(request, 'Product deleted.')
        return redirect('product_list')


class PurchaseProductView(SessionLoginRequiredMixin, View):
    def post(self, request, product_id):
        user = get_current_user(request)
        product = get_object_or_404(Product, id=product_id, is_active=True)
        profile = Profile.objects.filter(user=user).first()

        if not profile:
            messages.error(request, 'Profile not found.')
            return redirect('product_detail', product_id=product_id)

        if Purchase.objects.filter(user=user, product=product, status=Purchase.COMPLETED).exists():
            messages.warning(request, 'You have already purchased this product.')
            return redirect('product_detail', product_id=product_id)

        if product.type == Product.COURSE:
            from crm.models import Enrollment
            enrolled = Enrollment.objects.filter(
                student=user,
                course=product.course,
                status=Enrollment.APPROVED
            ).exists()
            if not enrolled:
                messages.error(request, 'This product is only available for course members.')
                return redirect('product_list')

        if product.stock <= 0:
            messages.error(request, 'This product is out of stock.')
            return redirect('product_detail', product_id=product_id)

        if profile.coins < product.price:
            messages.error(request, f'Not enough coins. You need {product.price} coins.')
            return redirect('product_detail', product_id=product_id)

        profile.coins -= product.price
        profile.save()

        product.stock -= 1
        product.save()

        Purchase.objects.create(user=user, product=product, status=Purchase.COMPLETED)

        CoinTransaction.objects.create(
            user=user,
            type=CoinTransaction.SPEND,
            reason=CoinTransaction.PURCHASE,
            amount=product.price,
            description=f'Purchased: {product.name}',
        )

        messages.success(request, f'You successfully purchased "{product.name}"!')
        return redirect('purchase_list')


class PurchaseListView(SessionLoginRequiredMixin, View):
    def get(self, request):
        user = get_current_user(request)
        if user.is_admin_role:
            purchases = Purchase.objects.select_related('user', 'product').all().order_by('-purchased_at')
        else:
            purchases = Purchase.objects.filter(user=user).select_related('product').order_by('-purchased_at')

        return render(request, 'shop/purchase_list.html', {
            'purchases': purchases,
        })


class CoinTransactionListView(SessionLoginRequiredMixin, View):
    def get(self, request):
        user = get_current_user(request)
        if user.is_admin_role:
            transactions = CoinTransaction.objects.select_related('user').all().order_by('-created_at')
        else:
            transactions = CoinTransaction.objects.filter(user=user).order_by('-created_at')

        profile = Profile.objects.filter(user=user).first()
        return render(request, 'shop/coin_transaction_list.html', {
            'transactions': transactions,
            'profile': profile,
        })


class GiveCoinsView(TeacherOrAdminRequiredMixin, View):
    def get(self, request):
        user = get_current_user(request)
        from crm.models import Course, Enrollment
        if user.is_teacher:
            students = UserModel.objects.filter(
                enrollments__course__teacher=user,
                enrollments__status=Enrollment.APPROVED,
                role=UserModel.STUDENT
            ).distinct()
        else:
            students = UserModel.objects.filter(role=UserModel.STUDENT)

        return render(request, 'shop/give_coins.html', {
            'students': students,
        })

    def post(self, request):
        user = get_current_user(request)
        student_id = request.POST.get('student_id')
        amount = request.POST.get('amount', 0)
        description = request.POST.get('description', '').strip()

        student = get_object_or_404(UserModel, id=student_id, role=UserModel.STUDENT)

        if user.is_teacher:
            from crm.models import Enrollment
            enrolled = Enrollment.objects.filter(
                student=student,
                course__teacher=user,
                status=Enrollment.APPROVED
            ).exists()
            if not enrolled:
                messages.error(request, 'This student is not in your course.')
                return redirect('give_coins')

        amount = int(amount)
        if amount <= 0:
            messages.error(request, 'Amount must be greater than 0.')
            return redirect('give_coins')

        profile = Profile.objects.filter(user=student).first()
        if not profile:
            messages.error(request, 'Student profile not found.')
            return redirect('give_coins')

        profile.coins += amount
        profile.save()

        CoinTransaction.objects.create(
            user=student,
            type=CoinTransaction.EARN,
            reason=CoinTransaction.TEACHER_GIFT,
            amount=amount,
            description=description or f'Gift from {user.username}',
        )

        messages.success(request, f'{amount} coins given to {student.username}.')
        return redirect('give_coins')


class AchievementListView(SessionLoginRequiredMixin, View):
    def get(self, request):
        user = get_current_user(request)
        achievements = Achievement.objects.all()
        user_achievement_ids = UserAchievement.objects.filter(user=user).values_list('achievement_id', flat=True)

        return render(request, 'shop/achievement_list.html', {
            'achievements': achievements,
            'user_achievement_ids': user_achievement_ids,
        })


class AchievementCreateView(TeacherOrAdminRequiredMixin, View):
    def get(self, request):
        return render(request, 'shop/achievement_create.html')

    def post(self, request):
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        coin_reward = request.POST.get('coin_reward', 0)

        if not name or not description:
            messages.error(request, 'Name and description are required.')
            return render(request, 'shop/achievement_create.html')

        achievement = Achievement(
            name=name,
            description=description,
            coin_reward=int(coin_reward),
        )

        if request.FILES.get('icon'):
            achievement.icon = request.FILES['icon']

        achievement.save()
        messages.success(request, f'Achievement "{achievement.name}" created.')
        return redirect('achievement_list')


class AchievementDeleteView(TeacherOrAdminRequiredMixin, View):
    def post(self, request, achievement_id):
        achievement = get_object_or_404(Achievement, id=achievement_id)
        achievement.delete()
        messages.success(request, 'Achievement deleted.')
        return redirect('achievement_list')


class GrantAchievementView(TeacherOrAdminRequiredMixin, View):
    def post(self, request, achievement_id):
        user = get_current_user(request)
        achievement = get_object_or_404(Achievement, id=achievement_id)
        student_id = request.POST.get('student_id')
        student = get_object_or_404(UserModel, id=student_id, role=UserModel.STUDENT)

        if user.is_teacher:
            from crm.models import Enrollment
            enrolled = Enrollment.objects.filter(
                student=student,
                course__teacher=user,
                status=Enrollment.APPROVED
            ).exists()
            if not enrolled:
                messages.error(request, 'This student is not in your course.')
                return redirect('achievement_list')

        _, created = UserAchievement.objects.get_or_create(user=student, achievement=achievement)

        if not created:
            messages.warning(request, f'{student.username} already has this achievement.')
            return redirect('achievement_list')

        if achievement.coin_reward > 0:
            profile = Profile.objects.filter(user=student).first()
            if profile:
                profile.coins += achievement.coin_reward
                profile.save()

                CoinTransaction.objects.create(
                    user=student,
                    type=CoinTransaction.EARN,
                    reason=CoinTransaction.ACHIEVEMENT,
                    amount=achievement.coin_reward,
                    description=f'Achievement unlocked: {achievement.name}',
                )

        messages.success(request, f'Achievement "{achievement.name}" granted to {student.username}.')
        return redirect('achievement_list')


class UserAchievementListView(SessionLoginRequiredMixin, View):
    def get(self, request):
        user = get_current_user(request)
        if user.is_admin_role:
            user_achievements = UserAchievement.objects.select_related('user', 'achievement').all().order_by('-earned_at')
        else:
            user_achievements = UserAchievement.objects.filter(user=user).select_related('achievement').order_by('-earned_at')

        return render(request, 'shop/user_achievement_list.html', {
            'user_achievements': user_achievements,
        })