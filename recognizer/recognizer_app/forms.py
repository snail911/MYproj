from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import (
    ModelForm,
    CharField,
    TextInput,
    PasswordInput,
    ImageField,
    FileInput,
)
from django.core.exceptions import ValidationError
from PIL import Image

class AnalyzeForm(forms.Form):
    image = forms.ImageField()

    def clean_image(self):
        image = self.cleaned_data.get('image')

        if image:
            try:
                img = Image.open(image)
                img.verify()  # Verify the image file

                # Additional checks if needed
                # For example, you can check the image format:
                # if img.format not in ['JPEG', 'PNG']:
                #     raise ValidationError('Invalid image format.')

            except (IOError, SyntaxError) as e:
                print(e)
                raise ValidationError('Invalid image file.')

        return image


class SignUpForm(UserCreationForm):
    username = CharField(
        min_length=3, max_length=50, required=True, widget=TextInput()
    )
    password1 = CharField(max_length=50, required=True, widget=PasswordInput())
    password2 = CharField(max_length=50, required=True, widget=PasswordInput())

    class Meta:
        model = User
        fields = ["username", "password1", "password2"]
