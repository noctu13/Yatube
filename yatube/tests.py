from django.test import TestCase, Client
from posts.models import User, Post

class TestCoverage(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='duncan',
            email='duncan@macloud.hl',
            password='leyrfyvfrkfel0',
            first_name='duncan',
            last_name='macloud'
        )

    def test_Profile(self):
        response = self.client.get('/duncan/')
        self.assertEqual(response.status_code, 200)

    def test_newPostCreation(self):
        self.client.force_login(self.user)
        response = self.client.get('/new/')
        self.assertEqual(response.status_code, 200)

    def test_newPostCreationForbidden(self):
        response = self.client.get('/new/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=%2Fnew%2F')
        
    def test_newPost(self):
        text = 'some incoherent text'
        Post.objects.create(text=text, author=self.user)
        response = self.client.get('')
        self.assertContains(response, text)
        response = self.client.get('/duncan/')
        self.assertContains(response, text)
        response = self.client.get('/duncan/0/')
        self.assertContains(response, text)

    def test_postEdit(self):
        text = 'some incoherent text'
        Post.objects.create(text=text, author=self.user)
        text = 'soMe inCoherent ediTed teXt'
        self.client.force_login(self.user)
        self.client.post('/duncan/0/edit/', {'text': text, 'group': ''})
        response = self.client.get('')
        self.assertContains(response, text)
        response = self.client.get('/duncan/')
        self.assertContains(response, text)
        response = self.client.get('/duncan/0/')
        self.assertContains(response, text)

    def cleanUp(self):
        pass
