from django.shortcuts import render, redirect, HttpResponse
from .forms import UserForm, UserProfileForm, PasswordResetForm, LoginForm
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.contrib.auth.models import User

# Create your views here.
def register(request):

    # if request is POST
    if request.method == 'POST':
        #grab information from the raw form information.
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)
        # If the two forms are valid...
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save() # save to database
            user.set_password(user.password)
            user.save()
            #until we are ready to avoid integrity problems we set commit=False
            profile = profile_form.save(commit=False)
            #set user instance for profile
            profile.user = user
            # If profile picture was provided we need to get it from the input form and put it in the UserProfile model.
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
                profile.save()   #saving the UserProfile model instance
        return redirect("/authenticate/login") # return user to login page
    else:
        # Not a HTTP POST,so we render the same empty  form
        user_form = UserForm()
        profile_form = UserProfileForm()
    return render(request,'authentication/signup.html',
        {
            'user_form': user_form,
            'profile_form': profile_form,
        })


def user_login(request):
    # If the request is a HTTP POST, try to pull out the relevant information.  
    login_form = LoginForm()
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            #attempt to see if the username/password
            # combination is valid -
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    # Login if user is active and valid 
                    # Redirecting user back to home page 
                    login(request, user)
                    return redirect('/')
    return render(request, 'authentication/login.html', {
        "form": login_form
    })


def home(request):
   #rendering our home page
    return redirect('/')


def password_reset(request):
    form = PasswordResetForm()
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            new_password = form.cleaned_data['new_password']
            stored_user = User.objects.filter(email=email)
            if stored_user:
                stored_user[0].set_password(new_password)
                stored_user[0].save()
            return redirect('/authenticate/login/')
    return render(request, "authentication/reset_password.html", {
        "re_password_form": form
    })




def logout_user(request):
    logout(request)
    return redirect('/')


# an authenticator to secure route in other apps
def authenticated(func):
    def test_auth(*args, **kwargs):
        request = args[0]
        user = request.user
        if user.is_authenticated:
            return func(*args, **kwargs)
        else:
            return redirect('/authenticate/login')
    return test_auth