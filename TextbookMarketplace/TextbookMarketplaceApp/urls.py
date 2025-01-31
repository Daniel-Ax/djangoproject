# TextbookMarketplaceApp/urls.py
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from .views import (
    IndexView,
    MyProductsView,
    SellProductView,
    LoginView,
    RegistrationView,
    LogoutView,
    SettingsView,
    ProductDetailView,
    DeleteProductView
)

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('my_products', MyProductsView.as_view(), name='my_products'),
    path('sell_product/', SellProductView.as_view(), name='sell_product'),
    path('product/delete/<int:product_id>/', DeleteProductView.as_view(), name='delete_product'),
    path('login/', LoginView.as_view(), name='login'),
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('settings/', SettingsView.as_view(), name='settings'),
    path('product/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
