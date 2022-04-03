from http import HTTPStatus

from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from posts.models import Group, Post, Comment

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Имя')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая пост',
        )
        cls.comment = Comment.objects.create(
            author=cls.user,
            text='Тестовый коментарий'
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_home_url_exists_at_desired_location(self):
        """Страница / доступна любому пользователю."""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_group_list_url_exists_at_desired_location(self):
        """Страница /group_list/ доступна любому пользователю."""
        response = self.guest_client.get('/group/test_slug/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_profile_url_exists_at_desired_location(self):
        """Страница /profile/ доступна любому пользователю."""
        response = self.guest_client.get('/profile/Имя/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_url_exists_at_desired_location(self):
        """Страница /posts/post_id доступна любому пользователю."""
        response = self.guest_client.get('/posts/1/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_id_detail_url_exists_at_desired_location_author(self):
        """Страница /posts/posts_id доступна автору"""
        response = self.authorized_client.get('/posts/1/edit')
        self.assertEqual(response.status_code, HTTPStatus.MOVED_PERMANENTLY)

    def test_create_url_exists_at_desired_location(self):
        """Страница /create/ доступна любому пользователю."""
        response = self.guest_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_unexisting_url_exists_at_desired_location(self):
        """Несуществующая страница"""
        response = self.guest_client.get('/unexisting/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_comment_url_exists_at_desired_location(self):
        '''Страница с коментариями'''
        response = self.guest_client.get('/posts/1/comment')
        self.assertEqual(response.status_code, HTTPStatus.MOVED_PERMANENTLY)

    def test_follow_url_exists_at_desired_location(self):
        """Страница с подписчиками"""
        response = self.guest_client.get('/follow/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_profile_url_exists_at_desired_location(self):
        """Страница /profile/follow доступна любому пользователю."""
        response = self.guest_client.get('/profile/Имя/follow/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_profile_url_exists_at_desired_location_author(self):
        """Страница /profile/follow доступна автору"""
        response = self.authorized_client.get('/profile/Имя/follow/')
        self.assertEqual(response.status_code, HTTPStatus.MOVED_PERMANENTLY)

    def test_profile_url_exists_at_desired_location(self):
        """Страница /profile/unfollow доступна любому пользователю."""
        response = self.guest_client.get('/profile/Имя/unfollow/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_profile_url_exists_at_desired_location_author(self):
        """Страница /profile/unfollow доступна автору"""
        response = self.authorized_client.get('/profile/Имя/unfollow/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test_slug/': 'posts/group_list.html',
            '/profile/Имя/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/posts/1/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
            '/follow/': 'posts/follow.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_homepage(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)
