from django.db import models

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
    adresse = models.CharField(max_length=255)
    coordonnees = models.ForeignKey(Coordonnees, on_delete=models.CASCADE)
    experienceWork = models.DateField(null=True) 
    specialitees = models.ManyToManyField(Specialite, through='AvocatSpecialitePrice', related_name='avocats', blank=True)
    langues = models.ManyToManyField(Langues, blank=True)
    dateWork = models.DateField()
    timeWork = models.TimeField()
    evaluationStar = models.IntegerField()
    
    def __str__(self):
        return self.firstName
    
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
    coordonnees = models.ForeignKey(Coordonnees, on_delete=models.CASCADE)
    def __str__(self):
        return self.phoneNumber
    class Meta:
        db_table = 'phoneNumbers'

class Post(models.Model):
    host = models.ForeignKey(Avocat, on_delete=models.CASCADE)
    dateTimePub = models.DateTimeField()
    title = models.CharField(max_length=300)
    content = models.TextField(null=True)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    class Meta:
        db_table = 'posts'

class Files(models.Model):
    source = models.TextField()
    rendezvous = models.ForeignKey('RendezVous',null = True, blank=True , on_delete= models.CASCADE)
      
    def __str__(self):
        return self.id

    class Meta:
        db_table = 'files'
    
class Visitor(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    firstName = models.CharField(max_length=20)
    lastName = models.CharField(max_length=20)
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
    dateTimePub = models.DateTimeField()
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.content[:30]
    class Meta:
        db_table = 'comment'
