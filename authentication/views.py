from email.message import EmailMessage
from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from rac_system import settings
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site 
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .tokens import generate_token
from django.core.mail import EmailMessage




def SignupPage(request):
    if request.method=='POST':
        first_name=request.POST.get('first_name')
        last_name=request.POST.get('last_name')
        username=request.POST.get('username')
        email=request.POST.get('email')
        pass1=request.POST.get('password1')
        pass2=request.POST.get('password2')

        if User.objects.filter(username=username):
            messages.error(request, "Username already exist! Please try some other username.")
            return redirect('signup')
        
        if User.objects.filter(email=email):
            messages.error(request, "Email already registered!!")
            return redirect('signup')
        
        if not username.isalnum():
            messages.error(request, "Username must be Alpha-Numeric!")
            return redirect('signup')
        
        if len(pass1) < 8:
            messages.error(request, "Password must be atleast 8 characters!")
            return redirect('signup')
        
        if pass1!=pass2:
            messages.error(request,"Your password and confirm password are not Same!!")
            return redirect('signup')
        

        else:

            my_user=User.objects.create_user(username,email,pass1)
            my_user.first_name=first_name
            my_user.last_name=last_name
            my_user.is_active=False   
            my_user.save()
            messages.success(request, "Your Account has been successfully created. \n" + "We have sent you a confirmation email, please confirm to complete registration.")

            # Welcome Email
        
            subject = "Welcome to Match Maestro"
            message = "Welcome to Match Maestro \n" + "Please confirm your email in order to authenticate your account \n" + "Thanking you \n" + "Team Match Maestro \n"
            from_email = settings.EMAIL_HOST_USER
            to_list = [my_user.email]
            send_mail(subject, message, from_email, to_list, fail_silently=True)
        
            #Confirmation Email
        
            current_site = get_current_site(request)
            email_subject = "Confirmation Email for Match Maestro!"
            message1 = render_to_string('email_confirmation.html' , {
                'name' : my_user.first_name,
                'domain' : current_site.domain,
                'uid' : urlsafe_base64_encode(force_bytes(my_user.pk)),
                'token' : generate_token.make_token(my_user)
            })
            email = EmailMessage(subject=email_subject, body=message1, from_email=settings.EMAIL_HOST_USER, to=[my_user.email])
            email.fail_silently = True
            email.send()
    
        
        return redirect('login')

    return render (request,'authentication/signup.html')


def LoginPage(request):
    if request.method=='POST':
        username=request.POST.get('username')
        pass1=request.POST.get('password')
        user=authenticate(request,username=username,password=pass1)
        if user is not None:
            login(request,user) 
            return redirect('upload_and_match')
        else:
            messages.error(request, "Username or Password is incorrect!!!")

    return render (request,'authentication/login.html')


def activate(request, uidb64, token):
    try: 
        uid = force_str(urlsafe_base64_decode(uidb64))
        my_user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        my_user = None
    if my_user is not None and generate_token.check_token(my_user, token):
        my_user.is_active = True
        my_user.save()
        login(request, my_user)
        return redirect('upload_and_match')
    else:   
        return render(request, 'activation_failed.html')
    

def LogoutPage(request):
    logout(request)
    return redirect('login')
