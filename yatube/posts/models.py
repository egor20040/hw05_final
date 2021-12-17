from django.db import models
from django.contrib.auth import get_user_model

from core.models import CreatedModel

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        help_text='Титил новой группы',
        verbose_name='Титл группы'
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        help_text='Уникальное имя группы',
        verbose_name='Slug группы'
    )
    description = models.TextField(
        help_text='Описание группы',
        verbose_name='Описание'
    )

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        help_text='Текст нового поста',
        verbose_name='Текст поста'
    )
    pub_date = models.DateTimeField(auto_now_add=True)
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        help_text='Группа, к которой будет относиться пост',
        verbose_name='Группа'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:30]


class Comment(CreatedModel):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        help_text='Пост к которому относится коментарий',
        related_name='comments',
        verbose_name='Пост'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField(
        help_text='Текст нового коментария',
        verbose_name='Текст коментария'
    )

    def __str__(self):
        return self.text[:15]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        help_text='Укажите подписчика',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        help_text='Укажите Автора',
        verbose_name='Автор'
    )

    def __str__(self):
        return f'{self.user} подписан на {self.author}'

    class Meta:
        constraints = (
            models.UniqueConstraint(fields=('user', 'author',),
                                    name='unique-in-module'),
        )
