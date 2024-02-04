from django.shortcuts import render,get_object_or_404, redirect 
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
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
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from rest_framework import generics , status
from rest_framework.authtoken.models import Token  
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import *

def home(request):

    name = request.GET.get('name', '')
    specialite = request.GET.get('specialite', '')
    location = request.GET.get('location', '')

    avocats_query = Q()
    name_parts = name.split()
    if name:
        for part in name_parts:
            avocats_query |= Q(firstName__icontains=part) | Q(lastName__icontains=part)
    if name:
        avocats_query |= Q(firstName__icontains=name) | Q(lastName__icontains=name)

    if specialite:
        avocats_query &= Q(specialitees__title__icontains=specialite)

    if location:
        avocats_query &= Q(adresse__icontains=location)

    avocats = Avocat.objects.filter(avocats_query).distinct()
    if request.user.is_authenticated:
        existing_avocat = Avocat.objects.filter(user=request.user).first()  # Use .first() to get a single instance
        rv_count = RendezVous.objects.filter(avocat=existing_avocat).exclude(statut="rejecting").count()
    else:
        existing_avocat = None
        rv_count = 0  

    context = {'avocats': avocats, "existing_avocat":existing_avocat ,'rv_count' :rv_count }
    return render(request, "avocat/home.html", context)

@api_view(['GET'])
def home_api(request):
    name = request.GET.get('name', '')
    specialite = request.GET.get('specialite', '')
    location = request.GET.get('location', '')

    avocats_query = Q()
    name_parts = name.split()

    if name:
        for part in name_parts:
            avocats_query |= Q(firstName__icontains=part) | Q(lastName__icontains=part)
    if name:
        avocats_query |= Q(firstName__icontains=name) | Q(lastName__icontains=name)

    if specialite:
        avocats_query &= Q(specialitees__title__icontains=specialite)

    if location:
        avocats_query &= Q(adresse__icontains=location)

    avocats = Avocat.objects.filter(avocats_query).distinct()

    existAvSerial = None  
    if request.user.is_authenticated:
        existing_avocat = Avocat.objects.filter(user=request.user).first()
        existAvSerial = AvocatSerializer(existing_avocat)

    rv_count = 0
    if existAvSerial:
        rv_count = RendezVous.objects.filter(avocat=existing_avocat).exclude(statut="rejecting").count()

    serializer = AvocatSerializer(avocats, many=True)

    response_data = {
        'avocats': serializer.data,
        'existing_avocat': existAvSerial.data if existAvSerial else None ,
        'rv_count': rv_count,
    }

    return Response(response_data, status=status.HTTP_200_OK)



def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)


        if user is not None:
            login(request, user)
            return redirect('home') 
        else:
            messages.error(request, "Invalid username or password.")
    return render(request,'avocat/login.html')

class LoginAPI(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        print(request)
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        confirm_password = request.POST.get('cpassword')
        email = request.POST.get('email')

        if password != confirm_password:
            messages.error(request, "Passwords do not match. Please enter them again.")
        else:

            if User.objects.filter(username=username).exists():
                messages.error(request, "Username is already taken. Please choose a different one.")
            else:
                user = User.objects.create_user(username=username, password=password, email=email)

                login(request, user, backend='django.contrib.auth.backends.ModelBackend')

                return redirect('home')  

    return render(request, 'avocat/signup.html')





@api_view(['POST'])
def signup_api(request):
    if request.method == 'POST':
        username = request.data.get('username').lower()
        password = request.data.get('password')
        confirm_password = request.data.get('cpassword')
        email = request.data.get('email')

        if password != confirm_password:
            return Response({'error': "Passwords do not match. Please enter them again."}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({'error': "Username is already taken. Please choose a different one."}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.create_user(username=username, password=password, email=email)
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        user_serializer = UserSerializer(user)  

        return Response({'user': user_serializer.data}, status=status.HTTP_201_CREATED)

    return Response({'error': "Invalid request method"}, status=status.HTTP_400_BAD_REQUEST)


@receiver(post_save, sender=User)
def create_visitor_for_user(sender, instance, created, **kwargs):
    if created:
        Visitor.objects.get_or_create(user=instance, defaults={'firstName': instance.username })

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
    rendezVousList = RendezVous.objects.filter(avocat=avocat)
    daysOfWork = avocat.dateWork
    timeWorkStart = avocat.timeWorkStart
    timeWorkEnd = avocat.timeWorkEnd

    form = PostForm()
    context = {
     'avocat':avocat , 
     'specialitees' : specialitees,
     'langues': langues , 
     'phone_numbers':phone_numbers,
     'posts':posts,
     'comments':comments,
      'form': form,
      'rendezVousList':rendezVousList ,
      'daysOfWork':daysOfWork ,
      'timeWorkStart':timeWorkStart,
      'timeWorkEnd':timeWorkEnd ,
     }
    return render(request,'avocat/profile.html',context)

@api_view(['GET'])
def profile_api(request, pk):
    avocat = get_object_or_404(Avocat, id=pk)
    specialitees = avocat.specialitees.all()
    langues = avocat.langues.all()
    phone_numbers = PhoneNumbers.objects.filter(coordonnees=avocat.coordonnees)
    posts = Post.objects.filter(host=avocat).order_by('-dateTimePub')
    comments = Comment.objects.filter(avocat=avocat).order_by('-dateTimePub')
    rendezVousList = RendezVous.objects.filter(avocat=avocat)
    daysOfWork = avocat.dateWork
    timeWorkStart = avocat.timeWorkStart
    timeWorkEnd = avocat.timeWorkEnd

    avocat_serializer = AvocatSerializer(avocat)
    specialitees_serializer = SpecialiteSerializer(specialitees, many=True) 
    langues_serializer = langueSerializer(langues, many=True)  
    phone_numbers_serializer = PhoneNumberSerializer(phone_numbers, many=True)
    posts_serializer = PostSerializer(posts, many=True)
    comments_serializer = CommentSerializer(comments, many=True)
    rendezVous_serializer = RendezVousSerializer(rendezVousList, many=True)

    response_data = {
        'avocat': avocat_serializer.data,
        'specialitees': specialitees_serializer.data,
        'langues': langues_serializer.data,
        'phone_numbers': phone_numbers_serializer.data,
        'posts': posts_serializer.data,
        'comments': comments_serializer.data,
        'rendezVousList': rendezVous_serializer.data,
        'daysOfWork': daysOfWork,
        'timeWorkStart': timeWorkStart,
        'timeWorkEnd': timeWorkEnd,
    }

    return Response(response_data, status=status.HTTP_200_OK)


@login_required(login_url='login')
def createAvocatProfile(request):
    existing_avocat = Avocat.objects.filter(user=request.user)
    if existing_avocat.exists():
        return redirect("home")

    if request.method == 'POST':
        # Collect form data
        first_name = request.POST.get('firstName')
        last_name = request.POST.get('lastName')
        adresse = request.POST.get('adresse')
        email = request.POST.get('email')
        phone_numbers = request.POST.getlist('phoneNumbers[]')
        experience_work = request.POST.get('experienceWork')
        
        selected_days = request.POST.getlist('day')
        date_work = ", ".join(selected_days) if selected_days else 'all the days'
        
        timeWorkStart = request.POST.get('timeWorkStart')
        timeWorkEnd=request.POST.get('timeWorkEnd')
        
        specialities = [key for key in request.POST.keys() if key in [sp.title for sp in Specialite.objects.all()]]
        languages = [key for key in request.POST.keys() if key in [lan.langue for lan in Langues.objects.all()]]

        # Call the create_avocat_profile method
        Avocat.create_avocat_profile(
            user=request.user,
            first_name=first_name,
            last_name=last_name,
            adresse=adresse,
            email=email,
            phone_numbers=phone_numbers,
            experience_work=experience_work,
            date_work=date_work,
            time_work_start=timeWorkStart,
            time_work_end=timeWorkEnd,
            specialities=specialities,
            languages=languages,
            photo=request.FILES.get('photo')
        )

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
        selected_days = request.POST.getlist('day')
        
        date_work = ", ".join(selected_days) if selected_days else 'all the days'
        
        timeWorkStart = request.POST.get('timeWorkStart')
        timeWorkEnd=request.POST.get('timeWorkEnd')

        specialities = [key for key in request.POST.keys() if key in [sp.title for sp in Specialite.objects.all()]]
        languages = [key for key in request.POST.keys() if key in [lan.langue for lan in Langues.objects.all()]]

        avocat_instance.firstName = first_name
        avocat_instance.lastName = last_name
        avocat_instance.adresse = adresse
        avocat_instance.experienceWork = experience_work
        avocat_instance.dateWork = date_work
        avocat_instance.timeWorkStart = timeWorkStart
        avocat_instance.timeWorkEnd = timeWorkEnd

        avocat_instance.coordonnees.email = email
        avocat_instance.coordonnees.save()

        avocat_instance.coordonnees.phonenumbers.all().delete() 
        for phone_number in phone_numbers:
            PhoneNumbers.objects.create(phoneNumber=phone_number, coordonnees=avocat_instance.coordonnees)

        if 'photo' in request.FILES:
            avocat_instance.photo = request.FILES['photo']

        avocat_instance.save()

        avocat_instance.specialitees.set(Specialite.objects.filter(title__in=specialities))
        avocat_instance.langues.set(Langues.objects.filter(langue__in=languages))

        return redirect('home')  


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
            title = form.cleaned_data['title']
            content = form.cleaned_data['content']
            
            avocat.create_post(title=title, content=content)

            return redirect('profile', pk=avocat.id)

    context = {
        'avocat': avocat,
    }
    return render(request, 'avocat/profile.html', context)

def add_comment(request, avocat_id):
    if request.method == 'POST' and request.user.is_authenticated:
        avocat = get_object_or_404(Avocat, id=avocat_id)
        content = request.POST.get('content')
        request.user.visitor.add_comment_to_avocat(avocat=avocat, content=content)

    return redirect('profile', pk=avocat.id)

def delete(request, pk):
    avocat = Avocat.objects.get(id=pk)
    return avocat.delete_avocat(request)


from django.contrib import messages
@login_required(login_url='login')
def evaluate(request, pk):
    avocat = get_object_or_404(Avocat, id=pk)
    if request.method == 'POST' and request.user.is_authenticated:
        avocat = get_object_or_404(Avocat, id=pk)
        evaluation_star = int(request.POST.get('evaluationStar'))
        host = request.user.visitor

        existing_evaluation = evalutationAvocatVisitor.objects.filter(avocat=avocat, host=host).first()

        if existing_evaluation:
            messages.error(request, 'You have already evaluated this avocat.')
        else:
            new_evaluation = evalutationAvocatVisitor(avocat=avocat, host=host, evaluationStar=evaluation_star)
            new_evaluation.save()
            
            avocat.update_evaluation()

            messages.success(request, 'Evaluation submitted successfully.')

    return redirect('profile', pk=avocat.id)


    

def listRendezVous(request, avocat_id):
    avocat = get_object_or_404(Avocat, id=avocat_id)
    listRendezVous = RendezVous.objects.filter(avocat=avocat).exclude(statut="rejecting").order_by('created')

    if request.method == 'POST':
        rv_id = request.POST.get('rv')
        statut = request.POST.get('statut')

        if rv_id:
            rv = get_object_or_404(RendezVous, id=rv_id)
            
            # Update the status of the RendezVous object
            rv.statut = statut
            rv.save()
            send_confirmation_email(rv)
            # Redirect to the same page to avoid form resubmission
            return HttpResponseRedirect(reverse('ListRendezVous', args=[avocat_id]))

    context = {
        'listRendezVous': listRendezVous,
    }
    return render(request, 'avocat/listRV.html', context)


def send_confirmation_email(rv):
    subject = 'Meeting Request Confirmation'
    sender_email = settings.EMAIL_HOST_USER  
    recipient_email = 'mohamedouaddane48@gmail.com'  


    message = render_to_string('email/confirm.html', {'rv': rv})

    send_mail(subject, message, sender_email, [recipient_email] ,  fail_silently=False,
    html_message=message ) 
    
@login_required(login_url='login')   
def prendreRendezVous(request, avocat_id):
    avocat = get_object_or_404(Avocat, id=avocat_id)

    if request.method == 'POST' and request.user.is_authenticated:
        title = request.POST.get('title')
        content = request.POST.get('content')
        date_heure = request.POST.get('dateTime')
        files = request.FILES.get('files')  

        rendezvous = RendezVous.objects.create(
            avocat=avocat,
            utilisateur=request.user.visitor,  # Assuming Visitor is related to the User model
            cause=content,
            title=title,
            date_heure=date_heure,
            statut="pending",
        )

        if files:
            file_instance = Files.objects.create(
                source=files,
                rendezvous=rendezvous,
            )

        avocat = avocat  
        visitor = request.user.visitor 
        rendezvous = rendezvous  

        subject = 'Meeting Request Notification'
        message = render_to_string('email/meeting_request.html', {'avocat': avocat, 'visitor': visitor, 'rendezvous': rendezvous})
        from_email = settings.EMAIL_HOST_USER   
        to_email = ["androandrobiert@gmail.com"] 

        send_mail(
            subject,
            '', 
            from_email,
            to_email,
            html_message=message,
        )

        messages.success(request, "You have scheduled your meeting!")
        return redirect('home')

    context = {'avocat': avocat}
    return render(request, "avocat/prendreRendezVous.html", context)


class AvocatListAPIView(generics.ListAPIView):
    queryset = Avocat.objects.all()
    serializer_class = AvocatSerializer
    

def avocatDetails(request, pk):
    avocat = get_object_or_404(Avocat, id=pk)
    serializer = AvocatSerializer(avocat)
    avocat_serialized = serializer.data  # Use serializer.data instead of the serializer object
    return Response(avocat_serialized, safe=False)



@api_view(['POST'])
@login_required
def add_Rendez_Vous_api(request, avocat_id):
    avocat = get_object_or_404(Avocat, id=avocat_id)
    serializerRv = RendezVousSerializer(data=request.data)
    
    if serializerRv.is_valid():
        title = serializerRv.validated_data.get('title')
        cause = serializerRv.validated_data.get('cause')
        date_heure = serializerRv.validated_data.get('date_heure')

        rendezvous = RendezVous.objects.create(
            avocat=avocat,
            utilisateur=request.user.visitor,
            cause=cause,
            title=title,
            date_heure=date_heure,
            statut="pending",
        )

        return Response({'message': "You have scheduled your meeting!"}, status=status.HTTP_201_CREATED)

    return Response({'error': "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)
   
@api_view(['POST'])
def addLangues(request):
    serializer = langueSerializer(data= request.data)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)

@api_view(['GET','PUT','DELETE'])
def langues(request,pk):
    lan = Langues.objects.get(id=pk)
    if request.method=='GET':
        serializer  = langueSerializer(lan,many=False)
        return Response(serializer.data)
    
    elif request.method=='PUT':
        serializer  = langueSerializer(instance=lan, data = request.data)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data)
       
    elif request.method=='DELETE':
        lan.delete()
        return Response("langue is deleted !")
