from django.db import models
from django.contrib import messages
from django.shortcuts import redirect, render
from django.db import models
from django.contrib.auth.models import User


class Langues(models.Model):
    langue = models.CharField(max_length = 100)
    def __str__(self):
        return self.langue
    class Meta:
        db_table = 'langues'

class Specialite(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    def __str__(self):
        return self.title
    class Meta:
        db_table = 'specialite'

class Coordonnees(models.Model):
    email= models.CharField(max_length=200)
    def __str__(self):
        return self.email
    class Meta:
        db_table = 'coordonnees'

class Experience(models.Model):
    description = models.TextField(blank=True, null=True)
    host = models.ForeignKey('Avocat', on_delete=models.CASCADE)
    def __str__(self):
        return self.description[:20]
    class Meta:
        db_table = 'experience'
  
class Avocat(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    firstName = models.CharField(max_length=100)
    lastName = models.CharField(max_length=100)
    adresse = models.CharField(max_length=100)
    mapsAdr = models.CharField(null=True,default='',max_length=1000)
    coordonnees = models.ForeignKey(Coordonnees, on_delete=models.CASCADE , null=True)
    experienceWork = models.DateField(null=True) 
    specialitees = models.ManyToManyField(Specialite, through='AvocatSpecialitePrice', related_name='avocats', blank=True,null=True)
    langues = models.ManyToManyField(Langues, blank=True , null=True)

    dateWork = models.CharField(null=True, default='all the days',max_length=200)

    timeWorkStart = models.TimeField(null=True)
    timeWorkEnd = models.TimeField(null=True)
    
    evaluationStar = models.IntegerField(null=True , default=0)
    photo = models.ImageField( null=True, blank=True , default='avatar.png')  # Add this line for the photo

    def __str__(self):
        return self.firstName
    @classmethod
    def create_avocat_profile(cls, user, first_name, last_name, adresse, email, phone_numbers, experience_work, date_work, time_work_start,time_work_end, specialities, languages, photo=None):
        coordonnees = Coordonnees.objects.create(email=email)

        avocat_instance = cls.objects.create(
            user=user,
            firstName=first_name,
            lastName=last_name,
            adresse=adresse,
            coordonnees=coordonnees,
            experienceWork=experience_work,
            dateWork=date_work,
            timeWorkStart=time_work_start,
            timeWorkEnd=time_work_end,
            evaluationStar=None
        )

        for phone_number in phone_numbers:
            PhoneNumbers.objects.create(phoneNumber=phone_number, coordonnees=coordonnees)

        if photo:
            avocat_instance.photo = photo
            avocat_instance.save()

        avocat_instance.specialitees.set(Specialite.objects.filter(title__in=specialities))
        avocat_instance.langues.set(Langues.objects.filter(langue__in=languages))

        return avocat_instance
    
    def create_post(self, title, content):
        post = Post.objects.create(host=self, title=title, content=content)
        return post
    
    def delete_avocat(self, request):
        if request.method == 'POST':
            visitor = self.user.visitor
            visitor.photo = 'visitor.png'
            visitor.save()
            self.delete()

            messages.success(request, 'Avocat deleted successfully.')

            return redirect('home')

        context = {
            'obj': self,
        }
        return render(request, 'avocat/delete.html', context)

    def update_evaluation(self):
       
        evaluations = evalutationAvocatVisitor.objects.filter(avocat=self)
        total_evaluations = evaluations.count()

        if total_evaluations > 0:
            sum_evaluations = evaluations.aggregate(models.Sum('evaluationStar'))['evaluationStar__sum']
            average_evaluation = sum_evaluations / total_evaluations
            self.evaluationStar = average_evaluation
            self.save()
    class Meta:
        db_table = 'avocat'



class AvocatSpecialitePrice(models.Model):
    avocat = models.ForeignKey(Avocat, on_delete=models.CASCADE)
    specialite = models.ForeignKey(Specialite, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2 , null=True, blank= True)

    class Meta:
        db_table = 'avocat_specialite_price'

class PhoneNumbers(models.Model):
    phoneNumber = models.CharField(max_length=20)
    coordonnees = models.ForeignKey(Coordonnees,related_name='phonenumbers', on_delete=models.CASCADE)
    def __str__(self):
        return self.phoneNumber
    class Meta:
        db_table = 'phoneNumbers'

class Post(models.Model):
    host = models.ForeignKey(Avocat, on_delete=models.CASCADE)
    dateTimePub = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=300)
    content = models.TextField(null=True)

    
    def __str__(self):
        return self.title
    class Meta:
        db_table = 'posts'

class Files(models.Model):
    source = models.TextField()
    rendezvous = models.ForeignKey('RendezVous',null = True, blank=True , on_delete= models.CASCADE)
      
    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'files'
    
class Visitor(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    firstName = models.CharField(max_length=20)
    lastName = models.CharField(max_length=20,null=True)
    photo = models.ImageField( null=True, blank=True , default='visitor.png' )
    
    def add_comment_to_avocat(self, avocat, content):
        Comment.objects.create(
            avocat=avocat,
            host=self,
            content=content,
        )
        
    def __str__(self):
        return self.firstName
    class Meta:
        db_table = 'visitor'
        

class RendezVous(models.Model):
    avocat = models.ForeignKey(Avocat, on_delete=models.CASCADE)
    utilisateur = models.ForeignKey(Visitor, on_delete=models.CASCADE)
    date_heure = models.DateTimeField()
    statut = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    cause = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.title
    class Meta:
        db_table = 'rendezvous'
        
class Comment(models.Model):
    avocat = models.ForeignKey(Avocat , on_delete = models.CASCADE)
    host = models.ForeignKey(Visitor, on_delete=models.CASCADE)
    dateTimePub = models.DateTimeField(auto_now_add=True)
    content = models.TextField()

    def __str__(self):
        return self.content[:30]
    class Meta:
        db_table = 'comment'

class evalutationAvocatVisitor(models.Model):
    avocat = models.ForeignKey(Avocat , on_delete = models.CASCADE)
    host = models.ForeignKey(Visitor, on_delete=models.CASCADE)
    evaluationStar = models.IntegerField(null=True)
    def __str__(self):
        return str(self.evaluationStar)
    class Meta:
        db_table = 'evalutationAvocatVisitor'