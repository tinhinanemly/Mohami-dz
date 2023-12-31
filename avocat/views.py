from django.shortcuts import render,get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login , logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import *
from .forms import AvocatForm , PostForm
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.db.models.signals import post_save


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


        if user is not None:
            login(request, user)
            return redirect('home')  # Adjust the redirect URL as needed
        else:
            messages.error(request, "Invalid username or password.")
    return render(request,'avocat/login.html')


from django.contrib.auth import login
from .models import Visitor  # Assuming Visitor model is in the same app as this view

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
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')

                return redirect('home')  # Adjust the redirect URL as needed

    return render(request, 'avocat/signup.html')




# Signal to create Visitor instance after User is saved
@receiver(post_save, sender=User)
def create_visitor_for_user(sender, instance, created, **kwargs):
    if created:
        Visitor.objects.get_or_create(user=instance, defaults={'firstName': instance.username})

# Signal to create Visitor instance when user logs in
@receiver(user_logged_in)
def create_visitor_on_login(sender, request, user, **kwargs):
    visitor, created = Visitor.objects.get_or_create(user=user, defaults={'firstName': user.username})

    # Check if the user is also associated with an Avocat profile
    try:
        avocat_profile = Avocat.objects.get(user=user)
        # Update Visitor attributes based on Avocat profile
        if avocat_profile.photo:
            visitor.photo = avocat_profile.photo
        visitor.firstName = avocat_profile.firstName
        visitor.lastName = avocat_profile.lastName
        visitor.save()
    except Avocat.DoesNotExist:
        pass
    
def logoutUser(request):
    logout(request)
    return redirect('home') 
def profile(request,pk):
    avocat = get_object_or_404(Avocat, id=pk)
    specialitees =avocat.specialitees.all()
    langues = avocat.langues.all()
    phone_numbers = PhoneNumbers.objects.filter(coordonnees=avocat.coordonnees)
    posts = Post.objects.filter(host= avocat).order_by('-dateTimePub')
    comments = Comment.objects.filter(avocat=avocat).order_by('-dateTimePub')
    form = PostForm()
    context = {
     'avocat':avocat , 
     'specialitees' : specialitees,
     'langues': langues , 
     'phone_numbers':phone_numbers,
     'posts':posts,
     'comments':comments,
      'form': form,
     }
    return render(request,'avocat/profile.html',context)
@login_required(login_url='login')


def createAvocatProfile(request):
    if request.method == 'POST':
        first_name = request.POST.get('firstName')
        last_name = request.POST.get('lastName')
        adresse = request.POST.get('adresse')
        email = request.POST.get('email')
        phone_number = request.POST.get('phoneNumber')
        experience_work = request.POST.get('experienceWork')
        date_work = request.POST.get('dateWork')
        time_work = request.POST.get('timeWork')

        # Process checkboxes for specialities and languages
        specialities = [key for key in request.POST.keys() if key in [sp.title for sp in Specialite.objects.all()]]
        languages = [key for key in request.POST.keys() if key in [lan.langue for lan in Langues.objects.all()]]

        # Create and save the Avocat instance
        user = request.user  # Assuming you have a valid User instance in the request
        coordonnees = Coordonnees.objects.create(email=email)  # Assuming you want to create a new Coordonnees instance
        phone_numbers = request.POST.getlist('phoneNumbers[]')
        # Create PhoneNumbers instances for each phone number
        for phone_number in phone_numbers:
            PhoneNumbers.objects.create(phoneNumber=phone_number, coordonnees=coordonnees)
        
        avocat_instance = Avocat.objects.create(
            user=user,
            firstName=first_name,
            lastName=last_name,
            adresse=adresse,
            coordonnees=coordonnees,
            experienceWork=experience_work,
            dateWork=date_work,
            timeWork=time_work,
            evaluationStar=None  # You might want to adjust this depending on your requirements
        )
        
        if 'photo' in request.FILES:
            avocat_instance.photo = request.FILES['photo']
            avocat_instance.save()
            
        avocat_instance.specialitees.set(Specialite.objects.filter(title__in=specialities))
        avocat_instance.langues.set(Langues.objects.filter(langue__in=languages))

        return redirect('home')  # Redirect to the home page or any other desired page

    langues = Langues.objects.all()
    specialites = Specialite.objects.all()
    context = {
        'action': "CREATE",
        "langues": langues,
        'specialites': specialites,
    }
    return render(request, 'avocat/create_avocat_profile.html', context)


def updateAvocatProfile(request, pk):
    avocat_instance = get_object_or_404(Avocat, id=pk)
    
    if request.method == 'POST':
        first_name = request.POST.get('firstName')
        last_name = request.POST.get('lastName')
        adresse = request.POST.get('adresse')
        email = request.POST.get('email')
        phone_numbers = request.POST.getlist('phoneNumbers[]')
        experience_work = request.POST.get('experienceWork')
        date_work = request.POST.get('dateWork')
        time_work = request.POST.get('timeWork')

        # Process checkboxes for specialities and languages
        specialities = [key for key in request.POST.keys() if key in [sp.title for sp in Specialite.objects.all()]]
        languages = [key for key in request.POST.keys() if key in [lan.langue for lan in Langues.objects.all()]]

        # Update the Avocat instance
        avocat_instance.firstName = first_name
        avocat_instance.lastName = last_name
        avocat_instance.adresse = adresse
        avocat_instance.experienceWork = experience_work
        avocat_instance.dateWork = date_work
        avocat_instance.timeWork = time_work

        # Update Coordonnees instance
        avocat_instance.coordonnees.email = email
        avocat_instance.coordonnees.save()

        # Update or create PhoneNumbers instances for each phone number
        avocat_instance.coordonnees.phonenumbers.all().delete()  # Delete existing phone numbers
        for phone_number in phone_numbers:
            PhoneNumbers.objects.create(phoneNumber=phone_number, coordonnees=avocat_instance.coordonnees)

        # Process and save the photo
        if 'photo' in request.FILES:
            avocat_instance.photo = request.FILES['photo']

        avocat_instance.save()

        avocat_instance.specialitees.set(Specialite.objects.filter(title__in=specialities))
        avocat_instance.langues.set(Langues.objects.filter(langue__in=languages))

        return redirect('home')  # Redirect to the home page or any other desired page


    langues = Langues.objects.all()
    specialites = Specialite.objects.all()
    context = {
        'action': "UPDATE",
        'avocat_instance': avocat_instance,
        'langues': langues,
        'specialites': specialites,
    }
    return render(request, 'avocat/create_avocat_profile.html', context)
def post_create(request, pk):
    avocat = get_object_or_404(Avocat, id=pk)

    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.host = avocat
            post.save()
            return redirect('profile', pk=avocat.id)
    

    context = {
        'avocat': avocat,
       
    }

    return render(request, 'avocat/profile.html', context)
def add_comment(request, avocat_id):
    if request.method == 'POST' and request.user.is_authenticated:
        avocat = get_object_or_404(Avocat, id=avocat_id)
        content = request.POST.get('content')

        Comment.objects.create(
            avocat=avocat,
            host=request.user.visitor  ,  # Assuming Visitor is related to the User model
            content=content,
        )

    return redirect('profile', pk = avocat.id)
def delete(request, pk):
    avocat = Avocat.objects.get(id=pk)
    if request.method=='POST':
        avocat.delete()
        return redirect('home')
    context={
        'obj':avocat,
    }
    return render(request,'avocat/delete.html', context)
    