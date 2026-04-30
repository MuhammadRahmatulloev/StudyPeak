from django.shortcuts import redirect
from django.contrib import messages
from accounts.models import UserModel
from .models import Product, Purchase


class ProductOwnerRequiredMixin:
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
            return redirect('product_list')

        product_id = kwargs.get('product_id')
        if product_id:
            product = Product.objects.filter(id=product_id).first()
            if not product:
                messages.error(request, 'Product not found.')
                return redirect('product_list')

            if user.is_teacher and product.created_by != user:
                messages.error(request, 'You are not the owner of this product.')
                return redirect('product_detail', product_id=product_id)

        return super().dispatch(request, *args, **kwargs)


class CourseProductAccessMixin:
    def dispatch(self, request, *args, **kwargs):
        user_id = request.session.get('user_id')
        if not user_id:
            messages.error(request, 'Please login first!')
            return redirect('login')

        user = UserModel.objects.filter(id=user_id).first()
        if not user:
            messages.error(request, 'Please login first!')
            return redirect('login')

        product_id = kwargs.get('product_id')
        if product_id:
            product = Product.objects.filter(id=product_id).first()
            if not product:
                messages.error(request, 'Product not found.')
                return redirect('product_list')

            if not product.is_active and not user.is_admin_role:
                messages.error(request, 'This product is not available.')
                return redirect('product_list')

            if product.type == Product.COURSE and user.is_student:
                from crm.models import Enrollment
                enrolled = Enrollment.objects.filter(
                    student=user,
                    course=product.course,
                    status=Enrollment.APPROVED
                ).exists()
                if not enrolled:
                    messages.error(request, 'This product is only available for course members.')
                    return redirect('product_list')

        return super().dispatch(request, *args, **kwargs)


class PurchaseOwnerRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        user_id = request.session.get('user_id')
        if not user_id:
            messages.error(request, 'Please login first!')
            return redirect('login')

        user = UserModel.objects.filter(id=user_id).first()
        if not user:
            messages.error(request, 'Please login first!')
            return redirect('login')

        purchase_id = kwargs.get('purchase_id')
        if purchase_id:
            purchase = Purchase.objects.filter(id=purchase_id).first()
            if not purchase:
                messages.error(request, 'Purchase not found.')
                return redirect('purchase_list')

            if user.is_student and purchase.user != user:
                messages.error(request, 'This is not your purchase.')
                return redirect('purchase_list')

        return super().dispatch(request, *args, **kwargs)


class CoinManagerRequiredMixin:
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
            return redirect('product_list')

        return super().dispatch(request, *args, **kwargs)