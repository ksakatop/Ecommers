from django.urls import  path
from .views import *




app_name = "ecomee"
urlpatterns = [
    path('', HomeView.as_view(), name='store'),
    path('product/<slug:slug>/', ProductView.as_view(), name='product'),
    path('allproducts/', AllProductView.as_view(), name='allproducts'),

    path('checkout/', CheckoutView.as_view(), name='checkout'),

    #carrito y funciones
    path('cart/', CartView.as_view(), name='cart'),
    path('addcart/<int:produ_id>/', AddCartView.as_view(), name='addcart'),
    path('managecart/<int:cap_id>/', ManageCartView.as_view(), name='managecart'),
    path('empycart/', EmpyCartView.as_view(), name='empycart'),

    #registro y login usuario
    path('register/', CustomerRegisterView.as_view(),name='register'),
    path('logout/', CustomerLogoutView.as_view(),name='logout'),
    path('login/', CustomerLoginView.as_view(),name='login'),

    #perfil de usuario
    path('perfil/', CustomerPerfilView.as_view(),name='perfil'),
    path('perfil/order-<int:pk>/', CustomerOrderDetailsView.as_view(),name='orderdetails'),
    
    #buscador
    path('buscar/', CustomerBuscarView.as_view(),name='buscar'),
    
    #admin urls
    path('adminlogin/', AdminLoginView.as_view(), name='adminlogin'),
    path('adminhome/', AdminHomeView.as_view(), name='adminhome'),
    path('adminorder/<int:pk>/', AdminOrderView.as_view(),name='adminorder'),
    path('adminallorder/', AdminAllOrderView.as_view(),name='adminallorder'),
    path('adminorder-<int:pk>-change/', AdminOrderStatusView.as_view(),name='adminorderstatus'),

]