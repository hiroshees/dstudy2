from django import forms
from django.utils.translation import ugettext as _
from django.contrib.auth.forms import AuthenticationForm 
from django.contrib.auth.forms import UsernameField
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.forms import SetPasswordForm


from django.forms import ModelForm

from .models import User

class LoginForm(AuthenticationForm):
    """ログインフォーム"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['placeholder'] = field.label
            field.label = ""
    
    username = forms.EmailField(
        label=_("メールアドレス"),
        widget=forms.EmailInput(attrs={
            'autofocus': True,
        }),
        error_messages={
            "required": "必須項目です",
            'invalid': "メールアドレスを入力してください",
        }
    )

    password = forms.CharField(
        label=_("パスワード"),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'current-password',
        }),
        error_messages={
            "required": "必須項目です",
        }
    )

    error_messages = {
        'invalid_login': _(
            "ユーザ名とパスワードが間違いです"
        ),
        'inactive': _(
            "無効です"
        ),
    }


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email','password1','password2','last_name', 'first_name')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label
            field.label = ""

    email = forms.EmailField(
        label=_("メールアドレス"),
        widget=forms.EmailInput(attrs={
            'autofocus': True,
        }),
        error_messages={
            "required": "必須項目です",
            'unique': "ユーザ名が重複しています",
            'invalid': "メールアドレスを入力してください",
        },
    )

    password1 = forms.CharField(
        label=_("パスワード"),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'current-password',
        }),
        error_messages={
            "required": "必須項目です",
        }
    )

    password2 = forms.CharField(
        label=_("パスワード再確認用"),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'current-password',
        }),
        error_messages={
            "required": "必須項目です",
        }
    )
    
    last_name = forms.CharField(
        label="姓",
        error_messages={
            "required": "必須項目です",
        }
    )
    
    first_name = forms.CharField(
        label="名",
        error_messages={
            "required": "必須項目です",
        }
    )
    
    error_messages = {
        'password_mismatch': _('パスワードが異なります'),
    }


class UserCreateForm(UserCreationForm):
    """
    ユーザー仮登録フォーム
    """
    class Meta:
        model = User
        fields = ('email',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['placeholder'] = field.label
            field.label = ""

    def clean_email(self):
        email = self.cleaned_data['email']
        User.objects.filter(email=email, is_active=False).delete()
        return email


class UserUpdateForm(ModelForm):
    """
    ユーザー情報更新フォーム
    """

    class Meta:
        model = User
        fields = ('last_name', 'first_name',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    last_name = forms.CharField(
        label="姓",
        widget=forms.TextInput(attrs={
            'autofocus': True,
            "placeholder":"姓を入力してください"
        }),
        error_messages={
            "required" : "入力してください",
        }
    )
    
    first_name = forms.CharField(
        label="名",
        widget=forms.TextInput(attrs={
            "placeholder":"名を入力してください"
        }),
        error_messages={
            "required" : "入力してください",
        }
    )


class MyPasswordChangeForm(PasswordChangeForm):
    """
    パスワード変更フォーム
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    old_password = forms.CharField(
        label="パスワード",
        widget=forms.PasswordInput(attrs={
            "placeholder": "現在のパスワードを入力",
        }),
        error_messages={
            "required" : "入力してください",
        },
    )
    
    new_password1 = forms.CharField(
        label="新パスワード",
        widget=forms.PasswordInput(attrs={
            "placeholder": "新しいパスワードを入力",
        }),
        error_messages={
            "required" : "入力してください",
        },
    )

    new_password2 = forms.CharField(
        label="新パスワード2",
        widget=forms.PasswordInput(attrs={
            "placeholder": "確認のため、同じパスワードを入力",
        }),
        error_messages={
            "required" : "入力してください",
        },
    )


class MyPasswordResetForm(PasswordResetForm):
    """
    パスワード忘れたときのフォーム
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class MySetPasswordForm(SetPasswordForm):
    """
    パスワード再設定用フォーム(パスワード忘れて再設定)
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
