from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import QuerySet
from django.shortcuts import render, redirect, reverse

from contrib import ids_lite


@login_required()
def index(request):
    return render(request, 'account/index.html')


def login_view(request):
    next_url = request.GET.get('next', '')

    sso_redirect_url = reverse('account:login-sso')
    sso_redirect_url = request.build_absolute_uri(sso_redirect_url)
    ctx = {
        'sso_url': ids_lite.get_authorize_url(sso_redirect_url, state=next_url),
    }

    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in.')
        if next_url:
            return redirect(next_url)
        else:
            return redirect(reverse('index'))

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            messages.success(request, f'Welcome {user.username}')
            login(request, user)
            if next_url:
                return redirect(next_url)
            else:
                return redirect(reverse('index'))
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'account/login.html', ctx)


def login_sso(request):
    code = request.GET.get('code', None)
    state = request.GET.get('state', None)

    userinfo = {
        'id': '',
        'phoneNumber': '',
        'userName': ''
    }

    if not code:
        messages.error(request, 'Invalid code.')
        return redirect(reverse('account:login'))

    try:
        userinfo = ids_lite.get_user_info(code)
    except Exception as e:
        messages.error(request, f'SSO login failed. {e}')
        return redirect(reverse('account:login'))

    user_queryset: QuerySet[User] = User.objects.filter(username=userinfo['userName'])

    if user_queryset.exists():
        user = user_queryset.first()
    else:
        user: User = User.objects.create_user(
            username=userinfo['userName'],
        )
        user.profile.phone = userinfo['phoneNumber']
        user.profile.save()

    login(request, user)
    messages.success(request, f'Welcome {user.username}')
    if state:
        return redirect(state)
    else:
        return redirect(reverse('index'))


def signup_view(request):
    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in.')
        return redirect(reverse('index'))

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.warning(request, 'Username already taken.')
            return render(request, 'account/sign-up.html')

        user: User = User.objects.create_user(username=username, password=password)
        messages.success(request, f'Welcome {user.username}')
        login(request, user)
        return redirect(reverse('index'))

    return render(request, 'account/sign-up.html')


@login_required()
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect(reverse('index'))
