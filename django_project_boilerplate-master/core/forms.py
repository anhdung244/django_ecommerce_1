from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
PAYMENT_CHOICES = (
    ('S', 'Stripe'),
    ('P', 'PayPal')
)

class CheckoutForm(forms.Form):
    street_address=forms.CharField(widget=forms.TextInput(attrs={
        'placeholder':"1234 Street",
    }))
    apartment_address=forms.CharField( required=False,widget=forms.TextInput(attrs={
        'placeholder':"Apart osr street"
    }))
    country= CountryField(blank_label='(select country) ').formfield(widget=CountrySelectWidget(attrs={
        'class':'custom-select d-block w-100'
    }))
    zip=forms.CharField(widget=forms.TextInput(attrs={
        'class':'form-control'
    }))
    same_shipping_address=forms.BooleanField(widget=forms.CheckboxInput())
    save_info=forms.BooleanField(widget=forms.CheckboxInput())
    payment_option = forms.ChoiceField(
        widget=forms.RadioSelect, choices=PAYMENT_CHOICES)