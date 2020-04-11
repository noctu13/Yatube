from django.test import TestCase, Client, override_settings
from posts.models import User, Post, Group, Follow
from django.conf import settings
import time

class PostViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='duncan',
            email='duncan@macloud.hl',
            password='leyrfyvfrkfel',
            first_name='duncan',
            last_name='macloud'
        )
        self.user2 = User.objects.create_user(
            username='victor',
            email='victor@kurgan.hl',
            password='dbrnjhrehufy2',
            first_name='victor',
            last_name='kurgan'
        )
        self.user3 = User.objects.create_user(
            username='amanda',
            email='amanda@montrose.hl',
            password='fvfylfvjynhjep3',
            first_name='amanda',
            last_name='montrose'
        )

    def test_profile(self):
        response = self.client.get('/duncan/')
        self.assertEqual(response.status_code, 200)

    def test_post_creation(self):
        self.client.force_login(self.user)
        response = self.client.get('/new/')
        self.assertEqual(response.status_code, 200)

    def test_post_creation_forbidden(self):
        response = self.client.get('/new/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=%2Fnew%2F')

    @override_settings(CACHES=settings.TEST_CACHES)
    def test_post(self):
        text = 'some incoherent text'
        post = Post.objects.create(text=text, author=self.user)
        response = self.client.get('')
        self.assertContains(response, text)
        response = self.client.get('/duncan/')
        self.assertContains(response, text)
        response = self.client.get('/duncan/%s/' % post.pk)
        self.assertContains(response, text)

    @override_settings(CACHES=settings.TEST_CACHES)
    def test_post_edit(self):
        text = 'some incoherent text'
        post = Post.objects.create(text=text, author=self.user)
        text = 'soMe inCoherent ediTed teXt'
        self.client.force_login(self.user)
        self.client.post('/duncan/%s/edit/' % post.pk, {'text': text, 'group': ''})
        response = self.client.get('')
        self.assertContains(response, text)
        response = self.client.get('/duncan/')
        self.assertContains(response, text)
        response = self.client.get('/duncan/%s/' % post.pk)
        self.assertContains(response, text)

    def test_404(self):
        response = self.client.get('fakepage')
        self.assertEqual(response.status_code, 404)

    @override_settings(CACHES=settings.TEST_CACHES)
    def test_image(self):
        self.client.force_login(self.user)
        highlander = Group.objects.create(title='hl', slug='hl', description='hl group')
        Post.objects.create(text='text', author=self.user, image='posts/pic.jpg', group=highlander)
        response = self.client.get('')
        self.assertContains(response, '<img')
        response = self.client.get('/duncan/')
        self.assertContains(response, '<img')
        response = self.client.get('/group/hl/')
        self.assertContains(response, '<img')

    @override_settings(CACHES=settings.TEST_CACHES)
    def test_not_image(self):
        self.client.force_login(self.user)
        with open('yatube/tests.py', 'rb') as open_file:
            self.client.post('/new/', {'text': 'msg', 'image': open_file})
        response = self.client.get('')
        self.assertNotContains(response, '<img')

    def test_subs(self):
        self.client.force_login(self.user)
        self.client.get('/amanda/follow/')
        follow_list = Follow.objects.filter(user=self.user)
        author_list = User.objects.filter(following__in=follow_list)
        self.assertIn(self.user3, author_list)
        self.client.get('/amanda/unfollow/')
        follow_list = Follow.objects.filter(user=self.user)
        author_list = User.objects.filter(following__in=follow_list)
        self.assertNotIn(self.user2, author_list)

    def test_follow_posts(self):
        self.client.force_login(self.user)
        self.client.get('/amanda/follow/')
        text = 'interesting msg'
        Post.objects.create(text=text, author=self.user3)
        response = self.client.get('/follow/')
        self.assertContains(response, text)
        self.client.force_login(self.user3)
        response = self.client.get('/follow/')
        self.assertNotContains(response, text)

    def test_comments(self):
        post = Post.objects.create(text='post text', author=self.user)
        comment_text = 'holywar'
        self.client.post('/duncan/%s/comment/' % post.pk, {'text': comment_text})
        response = self.client.get('/duncan/%s/' % post.pk)
        self.assertNotContains(response, comment_text)

    def cleanUp(self):
        pass
