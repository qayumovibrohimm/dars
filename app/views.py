from django.views.generic import (
    ListView, DetailView, CreateView,
    UpdateView, DeleteView, FormView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.db.models import Q, Avg
from django.db.models.functions import Round
from django.contrib import messages
from django.core.mail import EmailMessage

from .models import Category, Product
from app.forms import (
    ProductModelForm,
    OrderModelForm,
    CommentModelForm,
    ContactForm
)
from app.utils import filter_by_price
from config.settings import DEFAULT_FROM_EMAIL


class IndexView(ListView):
    model = Product
    template_name = 'app/home.html'
    context_object_name = 'products'

    def get_queryset(self):
        queryset = Product.objects.all()
        category_id = self.kwargs.get('category_id')
        search_query = self.request.GET.get('q', '')
        filter_type = self.request.GET.get('filter_type', '')

        if category_id:
            queryset = queryset.filter(category=category_id)

        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        queryset = filter_by_price(filter_type, queryset)

        return queryset.annotate(
            avg_rating=Round(Avg('comments__rating'))
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class ProductDetailView(DetailView):
    model = Product
    pk_url_kwarg = 'product_id'
    template_name = 'app/detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object

        context['comments'] = product.comments.filter(is_handle=False)
        context['related_products'] = Product.objects.filter(
            category=product.category
        ).exclude(id=product.id)

        context['order_form'] = OrderModelForm()
        context['comment_form'] = CommentModelForm()

        return context


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductModelForm
    template_name = 'app/create.html'
    login_url = '/admin/'
    success_url = reverse_lazy('app:create')

    def form_valid(self, form):
        messages.success(self.request, "Product successfully created ✅")
        return super().form_valid(form)


class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductModelForm
    template_name = 'app/update.html'
    pk_url_kwarg = 'pk'

    def get_success_url(self):
        return reverse_lazy('app:detail', kwargs={'product_id': self.object.id})


class ProductDeleteView(DeleteView):
    model = Product
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('app:index')


class OrderCreateView(FormView):
    form_class = OrderModelForm
    template_name = 'app/detail.html'

    def form_valid(self, form):
        product = get_object_or_404(Product, pk=self.kwargs['pk'])
        order = form.save(commit=False)
        order.product = product

        if order.quantity > product.stock:
            messages.error(self.request, 'Dont enough quantity')
            return redirect('app:detail', product.id)

        product.stock -= order.quantity
        product.save()
        order.save()

        messages.success(self.request, 'Order successfully sent ✅')
        return redirect('app:detail', product.id)


class CommentCreateView(FormView):
    form_class = CommentModelForm
    template_name = 'app/detail.html'

    def form_valid(self, form):
        product = get_object_or_404(Product, pk=self.kwargs['product_id'])
        comment = form.save(commit=False)
        comment.product = product
        comment.save()
        return redirect('app:detail', product.id)


class ContactView(FormView):
    form_class = ContactForm
    template_name = 'app/contact.html'
    success_url = reverse_lazy('app:index')

    def form_valid(self, form):
        name = form.cleaned_data['name']
        email = form.cleaned_data['email']
        message = form.cleaned_data['message']

        subject = f"New message from: {name}"
        html_content = f"""
        <h3>New Contact Message</h3>
        <p><strong>Name:</strong> {name}</p>
        <p><strong>Email:</strong> {email}</p>
        <p><strong>Message:</strong><br>{message}</p>
        """

        email_message = EmailMessage(
            subject=subject,
            body=html_content,
            from_email='Portfolio Contact <onboarding@resend.dev>',
            to=[DEFAULT_FROM_EMAIL],
            reply_to=[email],
        )
        email_message.content_subtype = 'html'
        email_message.send()

        return super().form_valid(form)


