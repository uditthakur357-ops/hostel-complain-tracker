from django import forms
from .models import Complaint


class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = [
            "title",
            "description",
            "hostel_block",
            "room_number",
            "complaint_type",
        ]

        widgets = {
            "title": forms.TextInput(attrs={
                "placeholder": "Example: Water supply issue"
            }),
            "description": forms.Textarea(attrs={
                "placeholder": "Explain your complaint",
                "rows": 4
            }),
            "hostel_block": forms.TextInput(attrs={
                "placeholder": "Example: Block A"
            }),
            "room_number": forms.TextInput(attrs={
                "placeholder": "Enter room number"
            }),
        }