from django.shortcuts import redirect, render
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.db.models import Q
from flask import request
from .models import Cart, CartProduct, Product, Category
from django.views.generic import View, CreateView, TemplateView, FormView, DetailView, ListView
from .forms import CheckoutForm, CustomerRegisterForm, CustomerLoginForm
from .models import *
from django.contrib.auth import authenticate, login, logout

# Create your views here.


#verificar si esta logeado o no para añadir la orden al usuario que se logea
class EcomMixin(object):
    def dispatch(self, request, *args, **kwargs):
        cart_id = request.session.get("cart_id")
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            if request.user.is_authenticated and Customer.objects.filter(user=request.user).exists():
                cart_obj.customer = request.user.customer
                cart_obj.save()

        return super().dispatch(request, *args, **kwargs)


#todos los productos
class HomeView(EcomMixin, TemplateView):
    template_name = "store/store.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        allproducts = Product.objects.all().order_by("id")
        paginator = Paginator(allproducts, 12)
        page_number = self.request.GET.get('page')
        product_list = paginator.get_page(page_number)

        context['producto'] = product_list
        return context
    

#ver un producto por su slug
class ProductView(EcomMixin, TemplateView):
    template_name = "store/product.html"

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        slug_url = self.kwargs['slug']
        producto = Product.objects.get(slug=slug_url) 
        context['producto'] = producto

        return context


class AllProductView(EcomMixin, TemplateView):
    template_name = "store/allproducts.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['allcategoty'] = Category.objects.all()

        return context


#añadir al carrito
class AddCartView(EcomMixin, TemplateView):
    template_name = "store/addcart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #consegir el producto que viene por la url
        product_id = self.kwargs['produ_id']

        #consegir producto
        producto = Product.objects.get(id=product_id)

        #ver si existe el carrito
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            this_product_cart = cart_obj.cartproduct_set.filter(product=producto)

            #items que exsisten en el cart
            if this_product_cart.exists():
                cartprodu = this_product_cart.last()
                cartprodu.quantity += 1
                cartprodu.subtotal += producto.selling_price
                cartprodu.save()
                cart_obj.total += producto.selling_price
                cart_obj.save()
            #nuevo items es añadido al carrito
            else:
                cartprodu = CartProduct.objects.create(cart= cart_obj, product= producto, rate= producto.selling_price, quantity= 1, subtotal= producto.selling_price )
                cart_obj.total += producto.selling_price
                cart_obj.save()

        else:
            cart_obj = Cart.objects.create(total=0)
            self.request.session["cart_id"] = cart_obj.id
            cartprodu = CartProduct.objects.create(cart= cart_obj, product= producto, rate= producto.selling_price, quantity= 1, subtotal= producto.selling_price )
            cart_obj.total += producto.selling_price
            cart_obj.save()
        
        return context


#el carrito
class CartView(EcomMixin, TemplateView):
    template_name = "store/cart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
        else:
            cart = None
        context['cart'] = cart
        return context



#para verificar y hacer la orden de compra
class CheckoutView(EcomMixin, CreateView):
    template_name = "store/checkout.html"
    form_class = CheckoutForm
    success_url = reverse_lazy("ecomee:store")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Customer.objects.filter(user=request.user).exists():
            pass
        else:
            return redirect("/login/?next=/checkout/")

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
        else:
            cart_obj = None
        
        context['cart_obj'] = cart_obj
        
        return context


    def form_valid(self, form):
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            form.instance.cart = cart_obj
            form.instance.subtotal = cart_obj.total
            form.instance.discount = 0
            form.instance.total = cart_obj.total
            form.instance.order_status = "Orden Recivida"
            del self.request.session['cart_id']
            
        else:
            return redirect("ecomee:store")
        
        return super().form_valid(form)


#acciones del carrito eliminar añadir
class ManageCartView(EcomMixin, View):
    def get(self, request, *args, **kwargs):
        cap_id = self.kwargs['cap_id']
        action = request.GET.get("accion")
        cap_obj = CartProduct.objects.get(id=cap_id)
        cart_obj = cap_obj.cart
    
        if action == "inc":
            cap_obj.quantity += 1
            cap_obj.subtotal += cap_obj.rate
            cap_obj.save()
            cart_obj.total += cap_obj.rate
            cart_obj.save()

        elif action == "dcr":
            cap_obj.quantity -= 1
            cap_obj.subtotal -= cap_obj.rate
            cap_obj.save()
            cart_obj.total -= cap_obj.rate
            cart_obj.save()
            if cap_obj.quantity == 0:
                cap_obj.delete()

        elif action == "rmv":
            cart_obj.total -= cap_obj.subtotal
            cart_obj.save()
            cap_obj.delete()
            
        else:
            pass
        
        return redirect('ecomee:cart')

    
#limpiar todo el carrito
class EmpyCartView(EcomMixin, View):
    def get(self, request, *args, **kwargs):
        cart_id = request.session.get("cart_id", None)
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
            cart.cartproduct_set.all().delete()
            cart.total = 0
            cart.save()
        return redirect("ecomee:cart")


#registro
class CustomerRegisterView(CreateView):
    template_name ="customerregister.html"
    form_class = CustomerRegisterForm
    success_url = reverse_lazy("ecomee:store") 

    def form_valid(self, form):
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        email = form.cleaned_data.get("email")
        user = User.objects.create_user(username, email, password)
        form.instance.user = user
        login(self.request, user)
        return super().form_valid(form)
    
    def get_success_url(self):
        if "next" in self.request.GET:
            next_url = self.request.GET.get("next")
            return next_url
        else:
            return self.success_url 

        return super().get_success_url()


#para salir de sesion
class CustomerLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("ecomee:store")


#control de ingreso de sesion
class CustomerLoginView(FormView):
    template_name ="customerrelogin.html"
    form_class = CustomerLoginForm
    success_url = reverse_lazy("ecomee:store") 

    #verificar si existe el nombre y contraseña para logear
    def form_valid(self, form):
        uname = form.cleaned_data.get("username")
        passw = form.cleaned_data.get("password")
        usr = authenticate(username=uname, password=passw)

        if usr is not None and Customer.objects.filter(user=usr).exists():
            login(self.request, usr)
        else:
            return render(self.request, self.template_name, {"form": self.form_class, "error": "Credenciales no validas"})

        return super().form_valid(form)


    def get_success_url(self):

        if "next" in self.request.GET:
            next_url = self.request.GET.get("next")
            return next_url
        else:
            return self.success_url 

        return super().get_success_url()


#perfil de usuario
class CustomerPerfilView(TemplateView):
    template_name = "store/customerperfil.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Customer.objects.filter(user=request.user).exists():
            pass
        else:
            return redirect("/login/?next=/perfil/")

        return super().dispatch(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = self.request.user.customer
        context["customer"] = customer
        orders = Order.objects.filter(cart__customer=customer).order_by("-id")
        context["orders"] = orders

        return context


#vista de pedidos como factura
class  CustomerOrderDetailsView(DetailView):
    template_name = "store/customerorderdatail.html"
    model = Order
    context_object_name = "ord_obj"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Customer.objects.filter(user=request.user).exists():
            order_id = self.kwargs['pk']

            if Order.objects.filter(id=order_id).exists():
                order = Order.objects.get(id=order_id)
                # resto de acciones cuando el pedido existe
            else:
                # acciones cuando el pedido no existe
                return redirect("ecomee:perfil")
                
        else:
            return redirect("/login/?next=/perfil/")

        return super().dispatch(request, *args, **kwargs)



#login para administrador
class AdminLoginView(FormView):
    template_name = "admin/adminlogin.html"
    form_class = CustomerLoginForm
    success_url = reverse_lazy("ecomee:adminhome")

    def form_valid(self, form):
        uname = form.cleaned_data.get("username")
        passw = form.cleaned_data.get("password")
        usr = authenticate(username=uname, password=passw)

        if usr is not None and Admin.objects.filter(user=usr).exists():
            login(self.request, usr)
        else:
            return render(self.request, self.template_name, {"form": self.form_class, "error": "Credenciales no validas"})

        return super().form_valid(form)



#verificar si esta logeado o no
class AdminRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Admin.objects.filter(user=request.user).exists():
            pass
        else:
            return redirect("/adminlogin/")

        return super().dispatch(request, *args, **kwargs)


#Inicio del panel admin
class AdminHomeView(AdminRequiredMixin, TemplateView):
    template_name = "admin/adminhome.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pendingorders'] = Order.objects.filter(order_status="Orden Recivida").order_by("-id")

        return context


#ver detalles de los pedidos del cliente
class AdminOrderView(AdminRequiredMixin, DetailView):
    template_name = "admin/adminorder.html"
    model = Order
    context_object_name = "ord_obj"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status"] = ORDER_STATUS 

        return context


#ver todas los pedidos existentes
class AdminAllOrderView(AdminRequiredMixin, ListView):
    template_name = "admin/adminallorder.html"
    queryset = Order.objects.all().order_by("-id")
    context_object_name = "allorder"



#cambair el estado del pedido
class AdminOrderStatusView(AdminRequiredMixin, View):
    
    def post(self, request,  *args, **kwargs):
        order_id = self.kwargs["pk"]
        order_obj = Order.objects.get(id= order_id)
        new_status = request.POST.get("status")
        order_obj.order_status = new_status
        order_obj.save()

        return redirect(reverse_lazy("ecomee:adminorder", kwargs={"pk": self.kwargs["pk"]})) 




class CustomerBuscarView(TemplateView):
    template_name = "store/buscar.html"

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        word = self.request.GET.get('keyword')
        resul = Product.objects.filter(Q(title__contains=word) | Q(description__contains=word))
        erorr = "Producto no encontrado"
        if resul.exists():
            context["resul"] = resul
        else:
            context["erorr"] = erorr
        
        return context















