from django.urls import path
from .views import (
    IndexView,
    ProductDetailView,
    ProductCreateView,
    ProductUpdateView,
    ProductDeleteView,
    OrderCreateView,
    CommentCreateView,
    ContactView,
)

app_name = 'app'

urlpatterns = [

    path('', IndexView.as_view(), name='index'),
    path('category/<int:category_id>/', IndexView.as_view(), name='products_of_category'),

    path('detail/<int:product_id>/', ProductDetailView.as_view(), name='detail'),

    path('create/', ProductCreateView.as_view(), name='create'),
    path('update/<int:pk>/', ProductUpdateView.as_view(), name='update'),
    path('delete/<int:pk>/', ProductDeleteView.as_view(), name='delete'),

    path('detail/<int:pk>/orders/', OrderCreateView.as_view(), name='create_order'),
    path('detail/<int:product_id>/comments/', CommentCreateView.as_view(), name='create_comment'),

    path('contact/', ContactView.as_view(), name='contact_view'),
]
