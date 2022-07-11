from django import forms
from .models import Customer, Order
from django.contrib.auth.models import User



class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["ordered_by", "shipping_address", "mobile", "email"]  

        widgets = {
            'ordered_by': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Nombre cliente'
                }
            ),
            'email': forms.EmailInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Correo'
                }
            ),
            'shipping_address': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Direccion'
                }
            ),
            'mobile': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Telefono'
                }
            ),
        }



class CustomerRegisterForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'usuario'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'}))
    email = forms.CharField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo'}))
    
    class Meta:
        model = Customer
        fields = ["username", "password", "email" , "full_name", "address"]

        widgets = {
            'address': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Direccion'
                }
            ),
            'full_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Nombre Completo'
                }
            ),
        }

    def clean_username(self):
        username = self.cleaned_data['username']
        
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Ya existe un usuario con ese nombre.')
        return username
        


class CustomerLoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'usuario'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'}))














