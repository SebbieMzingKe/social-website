from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.shortcuts import render

from .forms import LoginForm, UserRegistrationForm

# Create your views here.


def user_login(request):
    if request.method == 'POST':
        form = LoginForm()
        if form.is_valid():
            cd = form.changed_data
            user = authenticate(
                request,
                username = cd['username'],
                password = cd['password']
            )

            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Authenticated Successfully')
                else:
                    return HttpResponse('Disabled Account')
            else:
                return HttpResponse('Invalid Login')
            
    else:
        form = LoginForm()
    return render(request, 'account/login.html', {
        'form': form,
    })

@login_required
def dashboard(request):
    return render(
        request,
        'account/dashboard.html',
        {
            'section': 'dashboard'
        }
    )


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():

            # create new user
            new_user = user_form.save(commit = False)
            new_user.set_password(
                user_form.cleaned_data['password']
            )

            # save user object
            new_user.save()

            return render(
                request,
                'account/register_done.html',
                {
                    'new_user': new_user
                }
            )
        
    else:
        user_form = UserRegistrationForm()
    return render(
        request,
        'account/register.html',
        {
            'user_form': user_form
        }
    )