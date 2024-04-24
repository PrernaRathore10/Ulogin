from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from ulogin import settings
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from . tokens import generate_token
from django.template.loader import render_to_string
from django.core.mail import EmailMessage, send_mail


# Create your views here.

def home(request):
    return render(request, 'authentication\index.html')

def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        pass1 = request.POST['pass1']

        user = authenticate(username=username, password=pass1)

        if user is not None:
            login(request, user)
            fname = user.first_name
            return render(request, 'authentication/index.html',{'fname':fname})

        else:
            message.error(request,'Invalid credentials, Please try again')
            return redirect('signin')


    return render(request, 'authentication\signin.html')

def signup(request):
    if request.method =='POST':
        # username = request.POST.get('username')
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email= request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        if User.objects.filter(username=username):
            messages.error(request, 'Username already exists, try some other username')
            return redirect('signup')
        
        if User.objects.filter(email=email):
            messages.error(request, 'email already exists, try some other email')
            return redirect('signup')
        
        if len(username)>10:
            messages.error(request, 'username must be under 10 characters')
            return redirect('signup')
        
        if pass1 != pass2:
            messages.error(request, "passwords didn't match, try again")
            return redirect('signup')

        if not username.isalnum():
            messages.error(request, 'Username should only contain letters and numbers')
            return redirect('signup')

        myuser = User.objects.create_user(username,email,pass1)
        myuser.first_name = fname
        myuser.last_name = lname

        myuser.is_active = False

        myuser.save()

        messages.success (request,'Your account has been created successfully. We have sent you a confirmation email, please confirm your email in order to activate your account.')


        # Welcome email

        subject = "Welcome to Rental Axis !!!"
        message = "Hello " + myuser.first_name + ",\n\nWelcome to Rental Axis. We are glad to have you on board. \n we have sent you an email, please confirm your email account to proceed further \n\nThank you for choosing Rental Axis. \n\nRegards, \nTeam Rental Axis" 
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message, from_email, to_list, fail_silently = False)


        # Email Address Confirmation Email

        current_site = get_current_site(request)
        subject2 = 'Confirm your email @ Rental Axis'
        message2 = render_to_string('emailconfirmation.html', {
            'name' : myuser.first_name,
            'domain' : current_site.domain,
            'uid' : urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token' : generate_token.make_token(myuser),
            }
        )

        email = EmailMessage(subject2, message2, settings.EMAIL_HOST_USER, [myuser.email])
        email.fail_silently = False
        email.send()

        return redirect('signin')

    return render(request, 'authentication\signup.html')

def signout(request):
    logout(request)
    messages.success(request,'Successfully logged out')

    return redirect('home')


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)

    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser, token):
        myuser.is_active = True
        myuser.save()

        login(request, myuser)
        
        return redirect('signin')
    else :
        return render( request, 'activation_failed.html')