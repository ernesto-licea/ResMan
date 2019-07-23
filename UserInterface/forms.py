from django import forms


class LoginForm(forms.Form):
    Username = forms.CharField(widget=forms.TextInput(
        attrs={
            "placeholder":"Username",
            "autocomplete":"off"
        }
    ))

    password = forms.CharField(widget=forms.PasswordInput(
        attrs={
            "placeholder":u"Password",
            "autocomplete":"off"
        }
    ))

    remember_me = forms.BooleanField(widget=forms.CheckboxInput(),required=False)