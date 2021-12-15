from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from django import forms
from django.conf import settings
import tempfile
import shutil

from posts.models import Group, Post, Comment, Follow

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class TaskPagesTests(TestCase):
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
            text='Тестовая группа',
            group=cls.group
        )
        cls.post1 = Post.objects.create(
            author=cls.user1,
            text='Тестовая группа 1',
            group=cls.group
        )
        cls.comment = Comment.objects.create(
            text='Тестовый коментарий',
            author=cls.user,
            post=cls.post
        )
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.user1,
        )

    def setUp(self):
        self.user = TaskPagesTests.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def post_object_check(self, obj):
        post = TaskPagesTests.post
        self.assertEqual(post.text, obj.text)
        self.assertEqual(post.author, obj.author)
        self.assertEqual(post.group, obj.group)
        self.assertEqual(post.pk, obj.pk)
        return True

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        group = TaskPagesTests.group
        post = TaskPagesTests.post
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': group.slug}): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': post.author}): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': post.pk}): 'posts/post_detail.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': post.pk}): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html'

        }

        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""

        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        self.assertTrue(self.post_object_check(first_object))

    def test_group_page_show_correct_context(self):
        """Шаблон group сформирован с правильным контекстом."""
        group = TaskPagesTests.group
        revrs = reverse('posts:group_list', kwargs={'slug': f'{group.slug}'})
        response = self.authorized_client.get(revrs)
        group_list = response.context['page_obj']
        for post in group_list:
            self.assertEqual(post.group.title, group.title)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        post = TaskPagesTests.post
        revrs = reverse('posts:profile', kwargs={'username': f'{post.author}'})
        response = self.authorized_client.get(revrs)
        group_list = response.context['page_obj']
        for obj in group_list:
            self.assertTrue(self.post_object_check(obj))

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post detail сформирован с правильным контекстом."""
        comment = TaskPagesTests.comment
        post = TaskPagesTests.post
        revrs = reverse('posts:post_detail', kwargs={'post_id': f'{post.pk}'})
        response = self.authorized_client.get(revrs)
        obj = response.context['post']
        second_object = response.context['comments'][0]
        self.assertEqual(comment.text, second_object.text)
        self.assertTrue(self.post_object_check(obj))

    def test_post_create_page_show_correct_context(self):
        """Шаблон post create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post edit сформирован с правильным контекстом."""
        post = TaskPagesTests.post
        revrs = reverse('posts:post_edit', kwargs={'post_id': f'{post.pk}'})
        response = self.authorized_client.get(revrs)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_user_follow_page_show_correct_context(self):
        """Шаблон post follow_index сформирован с правильным контекстом."""
        post = TaskPagesTests.post1
        revrs = reverse('posts:follow_index')
        response = self.authorized_client.get(revrs)
        obj = response.context['page_obj'][0]
        self.assertEqual(post.text, obj.text)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        for i in range(0, 13):
            cls.post = Post.objects.create(
                author=cls.user,
                text=f'Тестовая группа {i}',
                group=cls.group
            )

    def setUp(self):
        self.user = PaginatorViewsTest.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_index_page_contains_ten_records(self):
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_index_page_contains_three_records(self):
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_first_group_page_contains_ten_records(self):
        group = PaginatorViewsTest.group
        response = self.client.get(reverse('posts:group_list',
                                           kwargs={'slug': f'{group.slug}'}))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_group_page_contains_three_records(self):
        group = PaginatorViewsTest.group
        rvrs = reverse('posts:group_list', kwargs={'slug': f'{group.slug}'})
        response = self.client.get(rvrs + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_first_profile_page_contains_ten_records(self):
        post = PaginatorViewsTest.post
        rvrs = reverse('posts:profile', kwargs={'username': f'{post.author}'})
        response = self.client.get(rvrs)
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_profile_page_contains_three_records(self):
        post = PaginatorViewsTest.post
        rvrs = reverse('posts:profile', kwargs={'username': f'{post.author}'})
        response = self.client.get(rvrs + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)


class PostCreateViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая группа',
            group=cls.group
        )

    def setUp(self):
        self.user = PostCreateViewsTest.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_index_post(self):
        group = PostCreateViewsTest.group

        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        task_text_0 = first_object.group.pk
        self.assertEqual(task_text_0, group.pk)

    def test_group_post(self):
        group = PostCreateViewsTest.group
        rvrs = reverse('posts:group_list', kwargs={'slug': f'{group.slug}'})
        response = self.authorized_client.get(rvrs)
        first_object = response.context['page_obj'][0]
        task_text_0 = first_object.group.pk
        self.assertEqual(task_text_0, group.pk)

    def test_profile_post(self):
        group = PostCreateViewsTest.group
        post = PostCreateViewsTest.post
        rvrs = reverse('posts:profile', kwargs={'username': f'{post.author}'})
        response = self.authorized_client.get(rvrs)
        first_object = response.context['page_obj'][0]
        task_text_0 = first_object.group.pk
        self.assertEqual(task_text_0, group.pk)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateImageTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        # Создаем запись в базе данных для проверки сушествующего slug
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая группа',
            group=cls.group,
            image=uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.user = PostCreateImageTest.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_index_image_context(self):
        """В context шаблона index передана картинка."""
        post = PostCreateImageTest.post
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        self.assertEqual(post.image, first_object.image)

    def test_profile_image_context(self):
        """В context шаблона profile передана картинка."""
        post = PostCreateImageTest.post
        response = self.authorized_client.get(reverse('posts:profile', kwargs={'username': f'{post.author}'}))
        first_object = response.context['page_obj'][0]
        self.assertEqual(post.image, first_object.image)

    def test_group_image_context(self):
        """В context шаблона group передана картинка."""
        post = PostCreateImageTest.post
        group = PostCreateImageTest.group
        response = self.authorized_client.get(reverse('posts:group_list', kwargs={'slug': f'{group.slug}'}))
        first_object = response.context['page_obj'][0]
        self.assertEqual(post.image, first_object.image)

    def test_detail_image_context(self):
        """В context шаблона post_detail передана картинка."""
        post = PostCreateImageTest.post
        response = self.authorized_client.get(reverse('posts:post_detail', kwargs={'post_id': f'{post.pk}'}))
        first_object = response.context['post']
        self.assertEqual(post.image, first_object.image)
