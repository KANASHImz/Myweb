from django.views.generic import CreateView, UpdateView, TemplateView, FormView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

from .forms import CustomUserCreationForm, CustomAuthenticationForm, ProfileUpdateForm
from blog.models import Post, Comment, Like
# Create your views here.
class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        user = form.save()
        user.is_verified = True
        user.is_active = True
        user.save()
        messages.success(self.request, 'Account created, you can now log in.')
        return super().form_valid(form)
class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = CustomAuthenticationForm
class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('accounts:login')
class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    form_class = ProfileUpdateForm
    template_name = 'accounts/profileUpdate.html'
    success_url = reverse_lazy('accounts:profile')

    def get_object(self):
        return self.request.user.profile

    def form_valid(self, form):
        messages.success(self.request, 'Your profile has been successfully updated')
        return super().form_valid(form)
class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.request.user.profile
        context['posts'] = Post.objects.filter(author=self.request.user)
        context['form'] = ProfileUpdateForm(instance=self.request.user.profile)
        return context  
class ChangePasswordView(LoginRequiredMixin, FormView):
    template_name = 'accounts/change_password.html'
    form_class = PasswordChangeForm
    success_url = reverse_lazy('accounts:profile')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        user = form.save()
        update_session_auth_hash(self.request, user)
        messages.success(self.request, 'رمز عبور با موفقیت تغییر کرد.')
        return super().form_valid(form)
    
class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.request.user.profile
        context['form'] = ProfileUpdateForm(instance=self.request.user.profile)
        
        if self.request.user.is_staff:
            context['posts'] = Post.objects.filter(author=self.request.user)

        context['user_comments'] = Comment.objects.filter(author=self.request.user).select_related('post')[:5]
        context['user_likes'] = Like.objects.filter(user=self.request.user).select_related('post')[:5]
        
        return context