from django import forms
from .models import Contact, Comment, NewsletterSubscription, Order

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Message', 'rows': 8}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = True

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['author', 'email', 'website', 'content']
        widgets = {
            'author': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Your Website (optional)'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Your Comment', 'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = False
        self.fields['website'].required = False

class NewsletterForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscription
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email address'}),
        }

class CartItemForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}))
    size = forms.CharField(max_length=50, required=False, widget=forms.Select(attrs={'class': 'form-control'}))

class BillingForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'city', 'state', 'postcode', 'payment_method']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Street Address'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Town / City'}),
            'state': forms.Select(attrs={'class': 'form-control'}),
            'postcode': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Postcode / ZIP'}),
            'payment_method': forms.RadioSelect(),
        }

    PAYMENT_METHODS = (
        ('bank_transfer', 'Direct Bank Transfer'),
        ('check', 'Check Payment'),
        ('paypal', 'PayPal'),
    )

    payment_method = forms.ChoiceField(choices=PAYMENT_METHODS, widget=forms.RadioSelect(attrs={'class': 'form-check-input'}))
    terms_accepted = forms.BooleanField(required=True, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['state'].choices = [
            ('', 'Select State / Country'),
            ('FR', 'France'),
            ('IT', 'Italy'),
            ('PH', 'Philippines'),
            ('KR', 'South Korea'),
            ('HK', 'Hongkong'),
            ('JP', 'Japan'),
        ]
