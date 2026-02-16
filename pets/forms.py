from django import forms

from .models import PetRequest


class PetRequestForm(forms.ModelForm):
    class Meta:
        model = PetRequest
        fields = [
            'pet_type',
            'breed',
            'color',
            'location',
            'description',
            'contact_information',
            'request_type',
            'image',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class PetSearchForm(forms.Form):
    pet_type = forms.ChoiceField(choices=[('', 'Any')] + PetRequest.PET_TYPES, required=False)
    breed = forms.CharField(max_length=100, required=False)
    location = forms.CharField(max_length=255, required=False)

    def clean(self):
        cleaned_data = super().clean()
        if not any(cleaned_data.values()):
            raise forms.ValidationError('Please provide at least one search criteria.')
        return cleaned_data
