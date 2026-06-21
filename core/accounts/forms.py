from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Profile
from django.contrib.auth import authenticate

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(label='email', widget=forms.EmailInput(attrs={'autocomplete': 'email'}))

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = True
        user.is_verified = True
        if commit:
            user.save()
        return user

class CustomAuthenticationForm(forms.Form):
    email = forms.EmailField(label='email', widget=forms.EmailInput(attrs={'autocomplete': 'email'}))
    password = forms.CharField(label='password', widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'}))

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email and password:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise forms.ValidationError("Invalid email or password")

            self.user_cache = authenticate(self.request, username=user.email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError("Invalid email or password")
        return self.cleaned_data

    def get_user(self):
        return self.user_cache


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'image', 'description']
