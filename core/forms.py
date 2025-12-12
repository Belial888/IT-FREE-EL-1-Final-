# core/forms.py
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Beneficiary

class ResidentRegistrationForm(UserCreationForm):
    # Extra fields for the Beneficiary model
    full_name = forms.CharField(max_length=200, required=True)
    address = forms.CharField(max_length=255, required=True, widget=forms.Textarea(attrs={'rows': 3}))
    contact_no = forms.CharField(max_length=15, required=True)
    household_info = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), help_text="List family members here.")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply Bootstrap form-control class to all widgets
        for name, field in self.fields.items():
            existing = field.widget.attrs.get('class', '')
            classes = f"{existing} form-control".strip()
            field.widget.attrs.update({'class': classes})

    def save(self, commit=True):
        user = super().save(commit=commit)
        # Create the associated Beneficiary record linked to this User
        Beneficiary.objects.create(
            user=user,
            full_name=self.cleaned_data['full_name'],
            address=self.cleaned_data['address'],
            contact_no=self.cleaned_data['contact_no'],
            household_info=self.cleaned_data['household_info']
        )
        return user


from django import forms
from .models import Distribution


class BeneficiaryForm(forms.ModelForm):
    class Meta:
        model = Beneficiary
        fields = ['full_name', 'address', 'contact_no', 'household_info']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            existing = field.widget.attrs.get('class', '')
            classes = f"{existing} form-control".strip()
            field.widget.attrs.update({'class': classes})


class DistributionForm(forms.ModelForm):
    class Meta:
        model = Distribution
        fields = ['request', 'date_given', 'item_name', 'qty', 'recipient']
        widgets = {
            'date_given': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            existing = field.widget.attrs.get('class', '')
            classes = f"{existing} form-control".strip()
            field.widget.attrs.update({'class': classes})