from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.forms import ModelForm

from .models import Profile

User = get_user_model()


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['name', 'email']
        widgets = {
            'name': forms.TextInput(attrs={'type': "text", 'class': "form-control"}),
            'email': forms.TextInput(attrs={'type': "text", 'class': "form-control mb-1", 'value': 'email'}),
        }


class UserAvatar(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image']
        widgets = {
            'image': forms.FileInput(attrs={'type': "file", 'class': "account-settings-fileinput"})
        }


class UserRegisterForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(
        attrs={'type': "text", 'class': "form-control", 'name': "username",
               'required': "required"})),
    email = forms.CharField(widget=forms.EmailInput(
        attrs={'type': "text", 'class': "form-control", 'name': "email",
               'required': "required", 'style': "border: black;"})),
    password1 = forms.CharField(widget=forms.PasswordInput(
        attrs={'type': "password", 'class': "form-control", 'name': "password",
               'required': "required"})),
    password2 = forms.CharField(widget=forms.PasswordInput(
        attrs={'type': "password", 'class': "form-control", 'name': "password",
               'required': "required"})),

    class Meta:
        model = User
        fields = UserCreationForm.Meta.fields + ('username', 'email', 'password1', 'password2')




class RegisterForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    # fields = ['password1', 'password2']
    # widgets = {
    #     'password1': forms.CharField(attrs={
    #         'label': 'Password', }),
    #     'password2': forms.CharField(attrs={'label': 'Password confirmation'})
    # }
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'email',)

    def clean_email(self):
        email = self.cleaned_data.get("email")
        qs = User.objects.filter(email__iexact=email)
        if qs.exists():
            raise forms.ValidationError('Cannot use this email. It\'s already registered.')
        return email

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(RegisterForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.is_active = False
        # create a new user hash for activating email.

        if commit:
            user.save()
            user.profile.send_activation_email()
        return user
