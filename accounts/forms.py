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
    city = forms.CharField(required=False)
    preferred_pet_type = forms.ChoiceField(choices=[('Dog', 'Dog'), ('Cat', 'Cat'), ('Other', 'Other'), ('None', 'None')], required=False)
    profile_image = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'city', 'preferred_pet_type', 'profile_image', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Override help texts to be shorter
        self.fields['username'].help_text = "Required. 150 chars or fewer. Letters/digits/@/./+/-/_ only."
        if 'password1' in self.fields:
            self.fields['password1'].help_text = "Your password must contain at least 8 characters and not be entirely numeric."
            
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
            elif hasattr(field.widget, 'choices') or isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select'})
            else:
                field.widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        user = super().save(commit)
        user.email = self.cleaned_data['email']
        user.save()

        profile = user.profile
        profile.phone = self.cleaned_data['phone']
        profile.city = self.cleaned_data.get('city', '')
        profile.preferred_pet_type = self.cleaned_data.get('preferred_pet_type', 'None')
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Override help texts here as well
        self.fields['username'].help_text = "Required. 150 chars or fewer. Letters/digits/@/./+/-/_ only."
        if 'password1' in self.fields:
            self.fields['password1'].help_text = "Your password must contain at least 8 characters and not be entirely numeric."


class ProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=False)
    city = forms.CharField(max_length=100, required=False)
    preferred_pet_type = forms.ChoiceField(choices=[('Dog', 'Dog'), ('Cat', 'Cat'), ('Other', 'Other'), ('None', 'None')], required=False)
    profile_image = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'profile'):
            self.fields['phone'].initial = self.instance.profile.phone
            self.fields['city'].initial = self.instance.profile.city
            self.fields['preferred_pet_type'].initial = self.instance.profile.preferred_pet_type
            self.fields['profile_image'].initial = self.instance.profile.profile_image
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
            elif hasattr(field.widget, 'choices') or isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select'})
            else:
                field.widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        user = super().save(commit=commit)
        profile, created = Profile.objects.get_or_create(user=user)
        
        profile.phone = self.cleaned_data.get('phone', '')
        profile.city = self.cleaned_data.get('city', '')
        profile.preferred_pet_type = self.cleaned_data.get('preferred_pet_type', 'None')
        
        # Only update image if a new one was uploaded, or keep existing if it's there
        if self.cleaned_data.get('profile_image'):
            profile.profile_image = self.cleaned_data['profile_image']
        # If clear checkbox is used (which django adds for ImageFields), it will be handled
        
        if commit:
            profile.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
