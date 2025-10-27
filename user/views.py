from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from user.forms import CustomUserCreationForm, CustomLoginForm
from django.views.generic import CreateView

# Signup
class SignUpView(CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'signup.html'
    success_url = reverse_lazy('cars:car_list')


# Login
class CustomLoginView(LoginView):
    template_name = 'login.html'
    authentication_form = CustomLoginForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('cars:car_list')


# Logout
class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('user:login')
