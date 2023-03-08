from django.contrib.auth.password_validation import validate_password
from rest_framework.fields import CharField


class PasswordField(CharField):
    def __init__(self, **kwargs):
        self.style = {'input_type': 'password'}
        self.write_only = True
        super().__init__(**kwargs)
        self.validators.append(validate_password)
