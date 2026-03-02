from django import forms

from .models import PetRequest, Comment


class PetRequestForm(forms.ModelForm):
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
            'location',
            'description',
            'contact_information',
            'image',
            ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
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
    pet_type = forms.ChoiceField(choices=[('', 'Any')] + PetRequest.PET_TYPES, required=False)
    breed = forms.CharField(max_length=100, required=False)
    location = forms.CharField(max_length=255, required=False)
    gender = forms.ChoiceField(
    choices=[('', 'Any')] + PetRequest.GENDER_CHOICES,
    required=False)
    size = forms.ChoiceField(
    choices=[('', 'Any')] + PetRequest.SIZE_CHOICES,
    required=False)
    request_type = forms.ChoiceField(
    choices=[('', 'All'), ('Lost', 'Lost'), ('Found', 'Found')],
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
