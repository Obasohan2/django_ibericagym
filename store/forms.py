from django import forms
from .models import ProductReview


class AddToCartForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=1,
        max_value=10,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'style': 'width: 60px'})
    )


class ProductReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ['rating', 'review']
        widgets = {
            'review': forms.Textarea(attrs={'rows': 3}),
        }