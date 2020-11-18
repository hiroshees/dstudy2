from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import resolve_url
from django.http import HttpResponse
from django.http import Http404, HttpResponseBadRequest
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, DetailView, UpdateView

from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.views import (
    LoginView, 
    LogoutView, 
    PasswordChangeView,
    PasswordResetView, 
    PasswordResetDoneView, 
    PasswordResetConfirmView, 
    PasswordResetCompleteView,
    PasswordResetConfirmView,
)
from django.contrib.auth import get_user_model
from django.contrib.auth import login
from django.core.signing import BadSignature, SignatureExpired, loads, dumps
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import BadHeaderError, send_mail

from .forms import (
    LoginForm,
    RegisterForm,
    UserCreateForm,
    UserUpdateForm,
    MyPasswordChangeForm,
    MyPasswordResetForm,
    MySetPasswordForm,
)


class IndexView(TemplateView):
    template_name = "chapter01/index.html"
    
    def get(self, request, **kwargs):
        """題名"""
        subject = "this is subject"
        """本文"""
        message = "本文です\nこんにちは。メールを送信しました"
        """送信元メールアドレス"""
        from_email = "fujiwara@no1s.biz"
        """宛先メールアドレス"""
        recipient_list = [
            "hiroshi.829f@gmail.com"
        ]
        send_mail(subject, message, from_email, recipient_list)
        return super().get(request, **kwargs)

    def get_context_data(self):
        context = super().get_context_data()
        context["title"] = "Index"
        return context


class LoginView(SuccessMessageMixin, LoginView):
    """ログインページ"""
    form_class = LoginForm
    template_name = 'chapter01/login.html'
    success_url = "chapter01:dashboard"
    success_message = "ログインしました"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "ログイン"
        return context


class LogoutView(LoginRequiredMixin, LogoutView):
    """ログアウトページ"""
    success_message = "ログアウトしました"
    
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        messages.error(request, self.success_message)
        return response


class RegisterView(SuccessMessageMixin, CreateView):
    form_class = RegisterForm
    template_name = "chapter01/register.html"
    success_url = reverse_lazy("chapter01:dashboard")
    success_message = "新規ユーザを作成しました"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "新規ユーザ作成"
        return context

    def form_valid(self, form):
        # formの情報を保存
        user = form.save() 
        # 認証
        login(self.request, user)
        self.object = user 
        # メッセージ代入
        messages.success(self.request, self.success_message)
        # リダイレクト
        return redirect(self.get_success_url()) 


class DashboardView(LoginRequiredMixin, TemplateView):
    """ダッシュボード"""
    template_name = 'chapter01/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Dashboard"
        return context

######


User = get_user_model()

class UserCreate(CreateView):
    """ユーザー仮登録"""
    template_name = 'chapter01/user_create.html'
    form_class = UserCreateForm

    def form_valid(self, form):
        """仮登録と本登録用メールの発行."""
        """
        仮登録と本登録の切り替えは、is_active属性を使うと簡単です。
        退会処理も、is_activeをFalseにするだけにしておくと捗ります
        """
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        
        # アクティベーションURLの送付
        current_site = get_current_site(self.request)
        domain = current_site.domain
        protocol = self.request.META["HTTP_X_FORWARDED_PROTO"]

        context = {
            'protocol': protocol,
            'domain': domain,
            'token': dumps(user.pk),
            'user': user,
        }

        subject = render_to_string('chapter01/mail/user_create_subject.txt', context)
        message = render_to_string('chapter01/mail/user_create_message.txt', context)

        user.email_user(subject, message)
        return redirect('chapter01:user_create_done')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "新規ユーザ仮登録"
        return context


class UserCreateDone(TemplateView):
    """
    ユーザー仮登録完了
    """
    template_name = 'chapter01/user_create_done.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "新規ユーザ仮登録完了"
        return context


class UserCreateComplete(TemplateView):
    """
    メール内URLアクセス後のユーザー本登録
    """
    
    template_name = 'chapter01/user_create_complete.html'
    # デフォルトでは1日以内
    timeout_seconds = getattr(settings, 'ACTIVATION_TIMEOUT_SECONDS', 60*60*24)

    def get(self, request, **kwargs):
        """
        tokenが正しければ本登録
        """
        token = kwargs.get('token')
        try:
            user_pk = loads(token, max_age=self.timeout_seconds)

        # 期限切れ
        except SignatureExpired:
            return HttpResponseBadRequest()
        # tokenが間違っている
        except BadSignature:
            return HttpResponseBadRequest()
        # tokenは問題なし
        else:
            try:
                user = User.objects.get(pk=user_pk)
            except User.DoesNotExist:
                # ユーザが存在しないのでエラー
                return HttpResponseBadRequest()
            else:
                if not user.is_active:
                    # 問題なければ本登録とする
                    user.is_active = True
                    user.save()
                    return super().get(request, **kwargs)
        # 何らかのエラー
        return HttpResponseBadRequest()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "新規ユーザ登録完了"
        return context


class OnlyYouMixin(UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        user = self.request.user
        return user.pk == self.kwargs['pk'] or user.is_superuser


class UserDetail(OnlyYouMixin, SuccessMessageMixin, DetailView):
    model = User
    template_name = 'chapter01/user_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "ユーザ情報"
        return context


class UserUpdate(OnlyYouMixin, SuccessMessageMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'chapter01/user_update.html'
    success_message = "ユーザー情報を更新しました"
    
    def get_success_url(self):
        return resolve_url('chapter01:user_detail', pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "ユーザ更新"
        return context


class UserPassWord(SuccessMessageMixin, PasswordChangeView):
    """
    パスワード変更
    """
    form_class = MyPasswordChangeForm
    success_url = reverse_lazy('chapter01:dashboard')
    template_name = 'chapter01/user_password.html'
    success_message = "パスワードを更新しました"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "パスワード変更"
        return context


class PasswordReset(PasswordResetView):
    """
    パスワード変更用URLの送付ページ
    """
    
    subject_template_name = 'chapter01/mail/password_reset_subject.txt'
    email_template_name = 'chapter01/mail/password_reset_message.txt'
    template_name = 'chapter01/password_reset.html'
    form_class = MyPasswordResetForm
    success_url = reverse_lazy('chapter01:password_reset_done')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "パスワード再設定"
        return context


class PasswordResetDone(PasswordResetDoneView):
    """
    パスワード変更用URLを送りましたページ
    """
    template_name = 'chapter01/password_reset_done.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "再設定メール送信送信完了"
        return context


class PasswordResetConfirm(PasswordResetConfirmView):
    """
    新パスワード入力ページ
    """
    form_class = MySetPasswordForm
    success_url = reverse_lazy('chapter01:password_reset_complete')
    template_name = 'chapter01/password_reset_confirm.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "新パスワード入力"
        return context


class PasswordResetComplete(PasswordResetCompleteView):
    """新パスワード設定しましたページ"""
    template_name = 'chapter01/password_reset_complete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "新パスワード設定完了"
        return context

