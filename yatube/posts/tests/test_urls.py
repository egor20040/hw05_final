from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from http import HTTPStatus

from posts.models import Group, Post, Comment

User = get_user_model()


class StaticURLTests(TestCase):

    def setUp(self):
        self.guest_client = Client()

    def test_about(self):
        response = self.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_technologies(self):
        response = self.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, HTTPStatus.OK)


class TaskURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user1 = User.objects.create_user(username='admin')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
        )
        cls.post1 = Post.objects.create(
            author=cls.user1,
            text='Тестовый текст',
        )
        cls.comment = Comment.objects.create(
            text='Тестовый коментарий',
            author=cls.user,
            post=cls.post
        )

    def setUp(self):
        self.user = TaskURLTests.user
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        group = TaskURLTests.group
        post = TaskURLTests.post
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{group.slug}/': 'posts/group_list.html',
            f'/profile/{post.author}/': 'posts/profile.html',
            f'/posts/{post.pk}/': 'posts/post_detail.html',
            f'/posts/{post.pk}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }

        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_unexising_url(self):
        """Страница / доступна любому пользователю."""
        response = self.guest_client.get('/unexising_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_task_create_url(self):
        """Страница /create/ доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_group_url(self):
        group = TaskURLTests.group
        """Страница /group/<slug>/ доступна любому пользователю."""
        response = self.guest_client.get(f'/group/{group.slug}/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_profile_url(self):
        post = TaskURLTests.post
        """Страница /profile/<username>/ доступна любому пользователю."""
        response = self.guest_client.get(f'/profile/{post.author}/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_url(self):
        """Страница /posts/<post_id>/ доступна любому пользователю."""
        post = TaskURLTests.post
        response = self.guest_client.get(f'/posts/{post.pk}/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_url(self):
        """Страница /edit/ доступна авторизованному пользователю."""
        post = TaskURLTests.post
        response = self.authorized_client.get(f'/posts/{post.pk}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_comment_url(self):
        """Страница /comment/ доступна авторизованному пользователю."""
        post = TaskURLTests.post
        response = self.guest_client.get(f'/posts/{post.pk}/comment/')
        self.assertRedirects(
            response,
            f'/auth/login/?next=/posts/{post.pk}/comment/'
        )

    def test_user_follow_url(self):
        """Страница /follow/ доступна авторизованному пользователю."""
        user = TaskURLTests.user1
        response = self.authorized_client.get(
            f'/profile/{user.username}/follow/'
        )
        self.assertRedirects(response, f'/profile/{user.username}/')
        response = self.authorized_client.get(
            f'/profile/{user.username}/unfollow/'
        )
        self.assertRedirects(response, f'/profile/{user.username}/')
