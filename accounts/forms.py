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
    DISTRICTS_TN = [
        ('', 'Select District'),
        ('Ariyalur', 'Ariyalur'), ('Chengalpattu', 'Chengalpattu'), ('Chennai', 'Chennai'),
        ('Coimbatore', 'Coimbatore'), ('Cuddalore', 'Cuddalore'), ('Dharmapuri', 'Dharmapuri'),
        ('Dindigul', 'Dindigul'), ('Erode', 'Erode'), ('Kallakurichi', 'Kallakurichi'),
        ('Kanchipuram', 'Kanchipuram'), ('Kanyakumari', 'Kanyakumari'), ('Karur', 'Karur'),
        ('Krishnagiri', 'Krishnagiri'), ('Madurai', 'Madurai'), ('Mayiladuthurai', 'Mayiladuthurai'),
        ('Nagapattinam', 'Nagapattinam'), ('Namakkal', 'Namakkal'), ('Nilgiris', 'Nilgiris'),
        ('Perambalur', 'Perambalur'), ('Pudukkottai', 'Pudukkottai'), ('Ramanathapuram', 'Ramanathapuram'),
        ('Ranipet', 'Ranipet'), ('Salem', 'Salem'), ('Sivaganga', 'Sivaganga'),
        ('Tenkasi', 'Tenkasi'), ('Thanjavur', 'Thanjavur'), ('Theni', 'Theni'),
        ('Thoothukudi', 'Thoothukudi'), ('Tiruchirappalli', 'Tiruchirappalli'),
        ('Tirunelveli', 'Tirunelveli'), ('Tirupattur', 'Tirupattur'), ('Tiruppur', 'Tiruppur'),
        ('Tiruvallur', 'Tiruvallur'), ('Tiruvannamalai', 'Tiruvannamalai'), ('Tiruvarur', 'Tiruvarur'),
        ('Vellore', 'Vellore'), ('Viluppuram', 'Viluppuram'), ('Virudhunagar', 'Virudhunagar')
    ]

    email = forms.EmailField(required=True)
    phone = forms.CharField(required=True)
    district = forms.ChoiceField(choices=DISTRICTS_TN, required=True, label="District")
    area = forms.CharField(required=True, label="Area / Landmark")
    preferred_pet_type = forms.ChoiceField(choices=[('Dog', 'Dog'), ('Cat', 'Cat'), ('Other', 'Other'), ('None', 'None')], required=False)
    profile_image = forms.ImageField(required=False)
    
    is_staff_registration = forms.BooleanField(required=False, label="Staff Registration (Requires Invite Code)")
    invite_code = forms.CharField(required=False, max_length=50, help_text="Enter valid invite code if registering as staff")

    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'district', 'area', 'preferred_pet_type', 'profile_image', 'password1', 'password2']

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

    def clean(self):
        cleaned_data = super().clean()
        is_staff = cleaned_data.get('is_staff_registration')
        invite_code = cleaned_data.get('invite_code')

        if is_staff:
            if not invite_code:
                self.add_error('invite_code', 'An invite code is required for staff registration.')
            else:
                from .models import StaffInviteCode
                try:
                    code_obj = StaffInviteCode.objects.get(code=invite_code)
                    if not code_obj.is_active:
                        self.add_error('invite_code', 'This invite code is no longer active.')
                except StaffInviteCode.DoesNotExist:
                    self.add_error('invite_code', 'Invalid invite code.')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        
        if self.cleaned_data.get('is_staff_registration'):
            user.is_staff = True
            
        if commit:
            user.save()

        # Safely get or create profile
        from .models import Profile
        profile, _ = Profile.objects.get_or_create(user=user)
        
        district = self.cleaned_data.get('district', '')
        area = self.cleaned_data.get('area', '')
        
        profile.phone = self.cleaned_data['phone']
        profile.city = f"{area}, {district}" if area and district else area or district
        profile.preferred_pet_type = self.cleaned_data.get('preferred_pet_type', 'None')
        if self.cleaned_data.get('profile_image'):
            profile.profile_image = self.cleaned_data['profile_image']
            
        if commit:
            profile.save()

        return user


class AdminRequestForm(forms.ModelForm):
    class Meta:
        from .models import AdminRequest
        model = AdminRequest
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Please explain why you want to join the staff team...'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    is_staff_registration = forms.BooleanField(required=False, label="Staff Registration (Requires Invite Code)")
    invite_code = forms.CharField(required=False, max_length=50)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean(self):
        cleaned_data = super().clean()
        is_staff = cleaned_data.get('is_staff_registration')
        invite_code = cleaned_data.get('invite_code')

        if is_staff:
            if not invite_code:
                self.add_error('invite_code', 'An invite code is required for staff registration.')
            else:
                from .models import StaffInviteCode
                try:
                    code_obj = StaffInviteCode.objects.get(code=invite_code)
                    if not code_obj.is_active:
                        self.add_error('invite_code', 'This invite code is no longer active.')
                except StaffInviteCode.DoesNotExist:
                    self.add_error('invite_code', 'Invalid invite code.')
        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Override help texts here as well
        self.fields['username'].help_text = "Required. 150 chars or fewer. Letters/digits/@/./+/-/_ only."
        if 'password1' in self.fields:
            self.fields['password1'].help_text = "Your password must contain at least 8 characters and not be entirely numeric."
            
    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data.get('is_staff_registration'):
            user.is_staff = True
        
        if commit:
            user.save()
            # Safely create the profile as well
            from .models import Profile
            Profile.objects.get_or_create(user=user)
            
        return user


class ProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=False)
    district = forms.ChoiceField(choices=CustomUserRegisterForm.DISTRICTS_TN, required=False, label="District")
    area = forms.CharField(max_length=150, required=False, label="Area / Landmark")
    preferred_pet_type = forms.ChoiceField(choices=[('Dog', 'Dog'), ('Cat', 'Cat'), ('Other', 'Other'), ('None', 'None')], required=False)
    profile_image = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'profile'):
            self.fields['phone'].initial = self.instance.profile.phone
            
            # Split city into area and district if possible
            if self.instance.profile.city:
                parts = self.instance.profile.city.rsplit(", ", 1)
                if len(parts) == 2:
                    self.fields['area'].initial = parts[0]
                    self.fields['district'].initial = parts[1]
                else:
                    self.fields['area'].initial = self.instance.profile.city
                    
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
        
        district = self.cleaned_data.get('district', '')
        area = self.cleaned_data.get('area', '')
        profile.city = f"{area}, {district}" if area and district else area or district
        
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
