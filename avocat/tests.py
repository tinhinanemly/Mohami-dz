from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import *
from django.urls import reverse
from django.contrib.messages import get_messages
from django.test import Client
from django.utils import timezone
from django.core import mail

class HomeViewTest(TestCase):
    def setUp(self):
        # Create test data for avocats
        self.specialite = Specialite.objects.create(title='Criminal Law')
        self.langue = Langues.objects.create(langue='English')
        self.coordonnees = Coordonnees.objects.create(email='avocat@example.com')

        self.avocat = Avocat.create_avocat_profile(
            user=User.objects.create_user(username='avocat_user', password='testpassword'),
            first_name='John',
            last_name='Doe',
            adresse='123 Main St',
            email='avocat@example.com',
            phone_numbers=['123456789'],
            experience_work='2022-02-01',
            date_work='Monday, Saturday',
            time_work_start='09:00:00',
            time_work_end='17:00:00',
            specialities=['Criminal Law'],
            languages=['English'],
            photo=None
        )

    def test_home_view_search(self):
        url = reverse('home') 
        search_params = {'name': 'John', 'specialite': 'Criminal Law', 'location': 'Main St'}
        response = self.client.get(url, search_params)

        self.assertEqual(response.status_code, 200)
        
        self.assertContains(response, 'John Doe')
        self.assertContains(response, 'Criminal Law')


    def test_home_view_no_results(self):
        url = reverse('home')
        search_params = {'name': 'Nonexistent', 'specialite': 'Nonexistent', 'location': 'Nowhere'}
        response = self.client.get(url, search_params)

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, 'No avocats found')
        

class LoginPageTest(TestCase):
    def setUp(self):

        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_login_successful(self):
        url = reverse('login')  
        data = {'username': 'testuser', 'password': 'testpassword'}

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 302)

        # Check that the user is redirected to the 'home' page
        self.assertRedirects(response, reverse('home'))

    def test_login_unsuccessful(self):
        url = reverse('login')
        data = {'username': 'invaliduser', 'password': 'invalidpassword'}

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 200)

        # Check that the 'Invalid username or password' message is present in the response
        self.assertContains(response, "Invalid username or password.")

class SignupViewTest(TestCase):
    def test_signup_successful(self):
        url = reverse('signup') 
        data = {
            'username': 'newuser',
            'password': 'testpassword',
            'cpassword': 'testpassword',
            'email': 'newuser@example.com',
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 302)

        self.assertRedirects(response, reverse('home'))

        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_signup_passwords_do_not_match(self):
        url = reverse('signup')
        data = {
            'username': 'userwithmismatchedpasswords',
            'password': 'testpassword',
            'cpassword': 'mismatchedpassword',
            'email': 'userwithmismatchedpasswords@example.com',
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, "Passwords do not match. Please enter them again.")

        self.assertFalse(User.objects.filter(username='userwithmismatchedpasswords').exists())

    def test_signup_username_already_taken(self):

        existing_user = User.objects.create_user(username='existinguser', password='testpassword')

        url = reverse('signup')
        data = {
            'username': 'existinguser',
            'password': 'testpassword',
            'cpassword': 'testpassword',
            'email': 'existinguser@example.com',
        }

        response = self.client.post(url, data)

        # Check that the response status code is 200 (no redirect for unsuccessful signup)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Username is already taken. Please choose a different one.")

class LogoutUserViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_logout_user(self):
        self.client.login(username='testuser', password='testpassword')

        # Make a request to the logout view
        url = reverse('logout') 
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)

        self.assertRedirects(response, reverse('home'))

        user = self.client.session.get('_auth_user_id')
        self.assertIsNone(user) 

class SignalsTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_create_visitor_for_user_signal(self):

        user = User.objects.create_user(username='testuser', password='testpassword')

        visitor = Visitor.objects.get(user=user)
        self.assertEqual(visitor.firstName, 'testuser')

    def test_create_visitor_on_login_signal(self):
        user = User.objects.create_user(username='testuser', password='testpassword')

        self.client.login(username='testuser', password='testpassword')

        visitor = Visitor.objects.get(user=user)
        self.assertEqual(visitor.firstName, 'testuser')

        avocat_profile = Avocat.objects.create(user=user, firstName='John', lastName='Doe', adresse='Test Address')
        avocat_profile.photo = 'path/to/photo.jpg'
        avocat_profile.save()

        self.client.login(username='testuser', password='testpassword')

        visitor.refresh_from_db()
        self.assertEqual(visitor.photo, 'path/to/photo.jpg')
        self.assertEqual(visitor.firstName, 'John')
        self.assertEqual(visitor.lastName, 'Doe')


class AvocatModelTest(TestCase):
        def setUp(self):
            self.user_avocat = User.objects.create_user(username='avocat_user', password='testpassword')
            self.specialite1 = Specialite.objects.create(title='Criminal Law')
            self.specialite2 = Specialite.objects.create(title='Family Law')

            self.langue1 = Langues.objects.create(langue='English')
            self.langue2 = Langues.objects.create(langue='French')

            self.coordonnees = Coordonnees.objects.create(email='avocat@example.com')

            self.avocat = Avocat.create_avocat_profile(
                user=self.user_avocat,
                first_name='John',
                last_name='Doe',
                adresse='123 Main St',
                email='avocat@example.com',
                phone_numbers=['123456789', '987654321'],
                experience_work='2022-02-01',
                date_work='Mondey, Saturday',
                time_work_start='09:00:00',
                time_work_end='17:00:00',
                specialities=[self.specialite1.title, self.specialite2.title],
                languages=[self.langue1.langue, self.langue2.langue],
                photo=None 
            )
        def test_create_post(self):
            post_title = 'Test Post Title'
            post_content = 'Test Post Content'

            self.avocat.create_post(title=post_title, content=post_content)
            post = Post.objects.filter(host=self.avocat)
            # Check if the post is created for the avocat
            self.assertEqual(post.count(), 1)
            created_post = post.first()
            self.assertEqual(created_post.title, post_title)
            self.assertEqual(created_post.content, post_content)
        
        def test_delete_avocat(self):
            self.client.login(username='avocat_user', password='testpassword')

            url = reverse('delete', kwargs={'pk': self.avocat.id})
            response = self.client.post(url)
            print(response)
            self.assertEqual(response.status_code, 200)

            self.assertRedirects(response, reverse('home'))
            
            self.assertFalse(Avocat.objects.filter(id=self.avocat.id).exists())

            visitor = Visitor.objects.get(user=self.user_avocat)
            self.assertEqual(visitor.photo, 'visitor.png')

            self.assertContains(response, 'Avocat deleted successfully.')


class EvaluateViewTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='testpassword')

        # Create an Avocat instance for testing
        self.avocat = Avocat.objects.create(
            user=self.user,
            firstName='John',
            lastName='Doe',
            adresse='123 Main St',
            experienceWork='2022-02-01',
            dateWork='Mondey, Saturday',
            timeWorkStart='09:00:00',
            timeWorkEnd='17:00:00',
        )

    def test_evaluate_view_authenticated_user(self):
        self.client.login(username='testuser', password='testpassword')

        url = reverse('evaluate', kwargs={'pk': self.avocat.id})
        data = {'evaluationStar': 4}  
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('profile', kwargs={'pk': self.avocat.id}))

        self.assertTrue(evalutationAvocatVisitor.objects.filter(avocat=self.avocat, host=self.user.visitor).exists())

        self.avocat.refresh_from_db()
        self.assertIsNotNone(self.avocat.evaluationStar)

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Evaluation submitted successfully.')

    def test_evaluate_view_authenticated_user_already_evaluated(self):

        self.client.login(username='testuser', password='testpassword')

        existing_evaluation = evalutationAvocatVisitor.objects.create(avocat=self.avocat, host=self.user.visitor, evaluationStar=3)

        url = reverse('evaluate', kwargs={'pk': self.avocat.id})
        data = {'evaluationStar': 4}  
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('profile', kwargs={'pk': self.avocat.id}))

        self.assertTrue(evalutationAvocatVisitor.objects.filter(avocat=self.avocat, host=self.user.visitor).exists())

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'You have already evaluated this avocat.')

    def test_evaluate_view_unauthenticated_user(self):
        url = reverse('evaluate', kwargs={'pk': self.avocat.id})
        data = {'evaluationStar': 4}  
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login') + f'?next={url}')

        self.assertFalse(evalutationAvocatVisitor.objects.filter(avocat=self.avocat, host=self.user.visitor).exists())


class ListRendezVousViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')

        self.avocat = Avocat.objects.create(
            user=self.user,
            firstName='John',
            lastName='Doe',
            adresse='123 Main St',
            experienceWork='2022-02-01',
            dateWork='Mondey, Saturday',
            timeWorkStart='09:00:00',
            timeWorkEnd='17:00:00',
        )

        self.rendezvous = RendezVous.objects.create(
            avocat=self.avocat,
            utilisateur=self.user.visitor,
            date_heure=timezone.now(),
            statut='pending',
        )

    def test_list_rendezvous_view_rendering(self):

        self.client.login(username='testuser', password='testpassword')


        url = reverse('ListRendezVous', args=[self.avocat.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)


        self.assertTemplateUsed(response, 'avocat/listRV.html')


        self.assertIn('listRendezVous', response.context)
        list_rendezvous = response.context['listRendezVous']
        self.assertEqual(list_rendezvous.count(), 1)
        self.assertEqual(list_rendezvous.first(), self.rendezvous)

    def test_list_rendezvous_view_post_request(self):

        self.client.login(username='testuser', password='testpassword')

        url = reverse('ListRendezVous', args=[self.avocat.id])
        data = {'rv': self.rendezvous.id, 'statut': 'confirmed'}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 302)


        self.rendezvous.refresh_from_db()
        self.assertEqual(self.rendezvous.statut, 'confirmed')
        self.assertRedirects(response, reverse('ListRendezVous', args=[self.avocat.id]))


class PrendreRendezVousViewTest(TestCase):
    def setUp(self):

        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.avocat = Avocat.objects.create(
            user=self.user,
            firstName='John',
            lastName='Doe',
            adresse='123 Main St',
            experienceWork='2022-02-01',
            dateWork='Mondey, Saturday',
            timeWorkStart='09:00:00',
            timeWorkEnd='17:00:00',
        )

    def test_prendre_rendezvous_view_rendering(self):
        self.client.login(username='testuser', password='testpassword')

        url = reverse('prendreRendezVous', args=[self.avocat.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'avocat/prendreRendezVous.html')

        self.assertIn('avocat', response.context)
        avocat = response.context['avocat']
        self.assertEqual(avocat, self.avocat)

    def test_prendre_rendezvous_view_post_request(self):
        self.client.login(username='testuser', password='testpassword')

        url = reverse('prendreRendezVous', args=[self.avocat.id])
        data = {
            'title': 'Meeting Title',
            'content': 'Meeting Content',
            'dateTime': timezone.now(),  
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 302)


        rendezvous = RendezVous.objects.last()
        self.assertIsNotNone(rendezvous)
        self.assertEqual(rendezvous.avocat, self.avocat)
        self.assertEqual(rendezvous.utilisateur, self.user.visitor)
        self.assertEqual(rendezvous.cause, 'Meeting Content')
        self.assertEqual(rendezvous.title, 'Meeting Title')
        self.assertEqual(rendezvous.statut, 'pending')


        # self.assertEqual(len(mail.outbox), 1)
        # sent_email = mail.outbox[0]
        # self.assertIn('Meeting Request Notification', sent_email.subject)
        # self.assertIn('You have scheduled your meeting!', sent_email.body)

        self.assertRedirects(response, reverse('home'))



class VisitorModelTest(TestCase):
        def setUp(self):
            self.user_avocat = User.objects.create_user(username='avocat_user', password='testpassword')
            self.user_visitor = User.objects.create_user(username='testuser', password='testpassword_visitor')

        def test_add_comment_to_avocat(self):
            avocat = Avocat.objects.create(user=self.user_avocat, firstName='John', lastName='Doe', adresse='Test Address')
            visitor = Visitor.objects.create(user=self.user_visitor, firstName='Test', lastName='Visitor')

            comment_content = 'Test Comment Content'


            visitor.add_comment_to_avocat(avocat=avocat, content=comment_content)

            self.assertEqual(avocat.comments.count(), 1)
            created_comment = avocat.comments.first()
            self.assertEqual(created_comment.host, visitor)
            self.assertEqual(created_comment.content, comment_content)
