from django.shortcuts import render,get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login , logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import *
from .forms import AvocatForm
from django.contrib.auth.models import User


def home(request):
    # Get search parameters from the request
    name = request.GET.get('name', '')
    specialite = request.GET.get('specialite', '')
    location = request.GET.get('location', '')

    # Start with an empty query
    avocats_query = Q()
    # Split the name into first name and last name
    name_parts = name.split()

    # Add conditions to the query based on provided parameters
    if name:
        # Match each part of the name independently
        for part in name_parts:
            avocats_query |= Q(firstName__icontains=part) | Q(lastName__icontains=part)
    # Add conditions to the query based on provided parameters
    if name:
        avocats_query |= Q(firstName__icontains=name) | Q(lastName__icontains=name)

    if specialite:
        avocats_query &= Q(specialitees__title__icontains=specialite)

    if location:
        avocats_query &= Q(adresse__icontains=location)

    # Filter avocats based on the constructed query
    avocats = Avocat.objects.filter(avocats_query).distinct()

    context = {'avocats': avocats}
    return render(request, "avocat/home.html", context)

# def loginPage():
    
def loginPage(request):
    # if request.user.authenticated 

    #     return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        print(f"Attempting to authenticate with username: {username}, password: {password}")

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome, {username}!")
            return redirect('home')  # Adjust the redirect URL as needed
        else:
            messages.error(request, "Invalid username or password.")
    return render(request,'avocat/login.html')


from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib import messages

def get_app(self, request, sociallogin):
    app = sociallogin.app
    print(f"Social app: {app}")
    # rest of the function
def login_page(request):
    sociallogin = request.socialaccount.sociallogin
    print(f"Social login object: {sociallogin}")
    # rest of the view code

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        confirm_password = request.POST.get('cpassword')
        email = request.POST.get('email')
        # Verify if passwords match
        if password != confirm_password:
            messages.error(request, "Passwords do not match. Please enter them again.")
        else:
            # Check if the username is already taken
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username is already taken. Please choose a different one.")
            else:
                # Create the user
                user = User.objects.create_user(username=username, password=password, email=email)

                # Log in the user
                login(request, user)

                messages.success(request, f"Welcome, {username}! Your account has been created.")
                return redirect('home')  # Adjust the redirect URL as needed

    return render(request, 'avocat/signup.html')


def logoutUser(request):
    logout(request)
    return redirect('home') 
def profile(request,pk):
    avocat = get_object_or_404(Avocat, id=pk)
    specialitees =avocat.specialitees.all()
    langues = avocat.langues.all()
    phone_numbers = PhoneNumbers.objects.filter(coordonnees=avocat.coordonnees)
    posts = Post.objects.filter(host= avocat)
    comments = Comment.objects.filter(avocat=avocat)

    context = {
     'avocat':avocat , 
     'specialitees' : specialitees,
     'langues': langues , 
     'phone_numbers':phone_numbers,
     'posts':posts,
     'comments':comments,
     }
    return render(request,'avocat/profile.html',context)
@login_required(login_url='login')
def createAvocatProfile(request):
    form = AvocatForm()
    if request.method == 'POST':
        form = AvocatForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    context = {
        'action':"CREATE" , 
        'form':form  
        
    }
    return render(request,'avocat/create_avocat_profile.html', context)


def updateAvocatProfile(request,pk):
    avocat = Avocat.objects.get(id= pk)
    form = AvocatForm(instance=avocat)
    if request.method == 'post':
        form = AvocatForm(request.POST,instance=avocat)
        if form.is_valid():
            form.save()
            return redirect('home')
    context={
        'form':form ,
        'action':"UPDATE" , 
    }
    return render(request,'avocat/create_avocat_profile.html', context)

def delete(request, pk):
    avocat = Avocat.objects.get(id=pk)
    if request.method=='POST':
        avocat.delete()
        return redirect('home')
    context={
        'obj':avocat,
    }
    return render(request,'avocat/delete.html', context)
    