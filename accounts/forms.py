from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

def register(request):
    if request.method == 'POST':
        form = CustomUserRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()

            # Save profile image if provided
            profile = user.profile
            if 'photo' in request.FILES:
                profile.photo = request.FILES['photo']
                profile.save()

            return redirect('login')
    else:
        form = CustomUserRegisterForm()

    return render(request, 'registration/register.html', {'form': form})

class CustomUserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(required=True)
    profile_image = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'profile_image', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit)
        user.email = self.cleaned_data['email']
        user.save()

        profile = user.profile
        profile.phone = self.cleaned_data['phone']
        if self.cleaned_data.get('profile_image'):
            profile.profile_image = self.cleaned_data['profile_image']
        profile.save()

        return user


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already in use.')
        return email


class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
