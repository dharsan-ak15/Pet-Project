from django import forms

from .models import PetRequest, Comment, ReportAbuse
from accounts.models import SystemComplaint


class PetRequestForm(forms.ModelForm):
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
    
    district = forms.ChoiceField(choices=DISTRICTS_TN, required=True, label="District")
    area = forms.CharField(max_length=150, required=True, label="Area / Landmark", widget=forms.TextInput(attrs={'placeholder': 'e.g., Near Gandhipuram Bus Stand'}))

    class Meta:
        model = PetRequest
        fields = [
            'request_type',
            'pet_type',
            'breed',
            'gender',
            'age',
            'age_unit',
            'size',
            'color',
            'vaccination_status',
            'medical_conditions',
            'description',
            'contact_information',
            'image',
            ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'medical_conditions': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
            elif hasattr(field.widget, 'choices') or isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select'})
            else:
                field.widget.attrs.update({'class': 'form-control'})


class PetSearchForm(forms.Form):
    DISTRICTS_TN = PetRequestForm.DISTRICTS_TN
    
    pet_type = forms.ChoiceField(choices=[('', 'Any')] + PetRequest.PET_TYPES, required=False)
    breed = forms.CharField(max_length=100, required=False)
    district = forms.ChoiceField(choices=[('', 'Any District')] + DISTRICTS_TN[1:], required=False)
    area = forms.CharField(max_length=150, required=False, label="Area/Landmark")
    gender = forms.ChoiceField(
    choices=[('', 'Any')] + PetRequest.GENDER_CHOICES,
    required=False)
    size = forms.ChoiceField(
    choices=[('', 'Any')] + PetRequest.SIZE_CHOICES,
    required=False)
    request_type = forms.ChoiceField(
    choices=[('', 'All'), ('Lost', 'Lost'), ('Found', 'Found'), ('Adoption', 'Adoption')],
    required=False)

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 3, 
                'placeholder': 'Add a comment or share a sighting...',
                'class': 'form-control rounded-3 bg-light border-0'
            }),
        }
        labels = {
            'content': ''
        }


class ContactRequestForm(forms.ModelForm):
    class Meta:
        from .models import PetContactRequest
        model = PetContactRequest
        fields = ['reason', 'message', 'image']
        widgets = {
            'reason': forms.Select(attrs={'class': 'form-select'}),
            'message': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Provide details (e.g., matching characteristics, where/when you saw it, etc.)...',
                'class': 'form-control'
            }),
            'image': forms.FileInput(attrs={'class': 'form-control'})
        }

from .models import PetRequest, Comment, ReportAbuse

class AbuseReportForm(forms.ModelForm):
    class Meta:
        model = ReportAbuse
        fields = ['reason', 'location', 'image']
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Please describe exactly why this profile is fraudulent, abusive, or fake...', 'class': 'form-control'}),
            'location': forms.TextInput(attrs={'placeholder': 'City or area where the incident occurred', 'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'})
        }

class SystemComplaintForm(forms.ModelForm):
    class Meta:
        model = SystemComplaint
        fields = ['complaint_text']
        widgets = {
            'complaint_text': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Please tell us what went wrong...',
                'class': 'form-control'
            }),
        }
