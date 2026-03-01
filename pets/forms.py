from django import forms

from .models import PetRequest


class PetRequestForm(forms.ModelForm):
    class Meta:
        model = PetRequest
        fields = [
            'request_type',
            'pet_type',
            'breed',
            'gender',
            'age',
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

    def clean(self):
        cleaned_data = super().clean()
        if not any(cleaned_data.values()):
            raise forms.ValidationError('Please provide at least one search criteria.')
        return cleaned_data
