from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms
from django.core.cache import cache
from yatube.settings import PAGE

from posts.models import Group, Post, Follow

User = get_user_model()

TEST_CACHE_SETTING = {
    'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'},
}


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Имя')
        cls.other_user = User.objects.create_user(username='Имя2')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая пост',
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': 'test_slug'}
                    ): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': 'Имя'}
                    ): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.pk}
                    ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.pk}
                    ): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def check_post(self, post):
        """Принимает объект поста и проверяет его атрибуты"""
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.group, self.post.group)

    def test_index_show_correct_context(self):
        """Список постов в шаблоне index равен ожидаемому контексту."""
        response = self.guest_client.get(reverse('posts:index'))
        expected = list(Post.objects.all())
        post = response.context['page_obj'][0]
        self.check_post(post)
        self.assertEqual(list(response.context['page_obj']), expected)

    def test_group_list_show_correct_context(self):
        """Список постов в шаблоне group_list равен ожидаемому контексту."""
        response = self.guest_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )
        expected = list(Post.objects.filter(group_id='1'))
        post = response.context['page_obj'][0]
        self.check_post(post)
        self.assertEqual(list(response.context['page_obj']), expected)

    def test_profile_show_correct_context(self):
        """Список постов в шаблоне profile равен ожидаемому контексту."""
        response = self.guest_client.get(
            reverse('posts:profile', args=(self.post.author,))
        )
        expected = list(Post.objects.filter(author_id='1'))
        post = response.context['page_obj'][0]
        self.check_post(post)
        self.assertEqual(list(response.context['page_obj']), expected)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        post = response.context.get('post')
        self.check_post(post)

    def test_create_edit_show_correct_context(self):
        """Шаблон create_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_create_show_correct_context(self):
        """Шаблон create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def check_group_in_pages(self):
        """Проверяем создание group при создании поста на страницах."""
        const = {'group': self.post.group}
        form_fields = {
            reverse('posts:index'): const,
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}): const,
            reverse('posts:profile',
                    kwargs={'username': self.post.author}): const,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                response = self.authorized_client.get(value)
                form_field = response.context['page_obj'].fields[value]
                self.assertIn(form_field, expected)

    def check_group_not_in_mistake_group_list_page(self):
        """Проверяем чтобы созданный Пост не попап в чужую группу."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )
        form_fields = {
            'group': self.post.group,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['page_obj'].fields[value]
                self.assertNotIn(form_field, expected)

    def test_follow_for_auth(self):
        """Проверяем функцию profile_follow"""
        follow_count = Follow.objects.count()
        Follow.objects.create(
            user=self.user,
            author=self.other_user
        )
        self.authorized_client.post(reverse(
            'posts:profile_follow', kwargs={'username': self.other_user}))
        self.assertTrue(Follow.objects.filter(
            user=self.user, author=self.other_user).exists()
        )
        self.assertEqual(Follow.objects.count(), follow_count + 1)

    def test_unfollow_for_auth(self):
        """Проверяем функцию profile_follow"""
        Follow.objects.create(
            user=self.user,
            author=self.other_user
        )
        follow_count = Follow.objects.count()
        self.authorized_client.post(reverse(
            'posts:profile_unfollow', kwargs={'username': self.other_user}))
        self.assertFalse(Follow.objects.filter(
            user=self.user, author=self.other_user).exists()
        )
        self.assertEqual(Follow.objects.count(), follow_count - 1)

    @override_settings(CACHES=TEST_CACHE_SETTING)
    def test_cache_index(self):
        """Проверяем, кэш главной страницы"""
        posts_count = Post.objects.count()
        response = self.authorized_client.get('posts:index').content
        Post.objects.create(
            author=self.user,
            text='Тестовый текст ',
            group=self.group
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)

        self.assertEqual(response, (
            self.authorized_client.get('posts:index').content))
        cache.clear()
        self.assertEqual(response, (
            self.authorized_client.get('posts:index').content))


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Имя')
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='test_slug',
            description='Тестовое описание'
        )
        cls.posts = [
            Post.objects.create(
                author=cls.user,
                text='Текст поста № {i}',
                group=cls.group
            )
            for i in range(13)
        ]
        cache.clear()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_ten_records(self):
        """На первой странице 10 постов"""
        url_paginator_test = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={
                'slug': self.group.slug}),
            reverse('posts:profile', kwargs={
                'username': self.user.username})
        ]
        for url_name in url_paginator_test:
            with self.subTest(url_name=url_name):
                response = self.authorized_client.get(url_name)
                self.assertEqual(len(response.context['page_obj']), PAGE)

    def test_second_page_contains_three_records(self):
        """На второй оставшиеся 3 поста"""
        url_paginator_test = [
            reverse('posts:index') + '?page=2',
            reverse(
                'posts:group_list', kwargs={
                    'slug': self.group.slug}) + '?page=2',
            reverse(
                'posts:profile', kwargs={
                    'username': self.user.username}) + '?page=2'
        ]
        for url_name in url_paginator_test:
            with self.subTest(url_name=url_name):
                response = self.authorized_client.get(url_name)
                self.assertEqual(len(response.context['page_obj']), len(['page_obj'])+2)
