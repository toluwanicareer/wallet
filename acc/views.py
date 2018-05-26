from django.shortcuts import render
import account.views
import account.forms
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.contrib import auth
from .forms import ProfileForm
from .models import Profile
from django.core.mail import EmailMessage
import pdb
from django.http import HttpResponseRedirect



# Create your views here.


class LoginView(account.views.LoginView):
    def form_invalid(self, form):
        messages.warning(self.request, 'Wrong username or password')
        return super(LoginView, self).form_invalid(form)

    def form_valid(self, form):
        super(LoginView, self).form_valid(form)
        return HttpResponseRedirect('/office/')

    # return HttpResponseRedirect(reverse('office:invest'))


class LogoutView(account.views.LogoutView):
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            auth.logout(self.request)
            return HttpResponseRedirect('/account/login/')


class SignupView(account.views.SignupView):
    def form_invalid(self, form):
        errors=''
        pdb.set_trace()
        for error in form.errors.get('__all__'):
            errors += error+', '
        messages.warning(self.request, errors)
        return super(SignupView, self).form_invalid(form)

    def form_valid(self, form):
        a = super(SignupView, self).form_valid(form)
        messages.success(self.request,
                         'Account Created. Please Login to start investing. Thank you ')
        self.created_user.is_active = True
        self.created_user.save()
        try:
            profile = Profile.objects.get(user=self.created_user)
            form = ProfileForm(instance=profile,  data=self.request.POST)
        except Profile.DoesNotExist:
            form=ProfileForm(data=self.request.POST)

        if form.is_valid():
            form.save()
            subject = 'User Registration on Xenos'
            message = ' A user with email ' + self.created_user.email + ' just registered on xenos. Please Login Activate'
            email2 = EmailMessage(subject, message, 'contact@xenos.com', to=['xeotrading@gmail.com'],
                                  reply_to=['no-reply@avetiz.com'], )
            try:
                email2.send()
            except:
                messages.warning(self.request,
                                 'Network error, Admin was not notified of you registration, Please contact admin directly with your registration email')
        else:
            pass

        # profile.passport=request.POST.get('passport')
        return HttpResponseRedirect('/account/signup/')