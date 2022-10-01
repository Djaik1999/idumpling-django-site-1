import uuid

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

from PIL import Image


class DumplingMeat(models.Model):
    name = models.CharField(max_length=60)

    def __str__(self):
        return self.name


class DumplingSize(models.Model):
    size = models.CharField(max_length=40)

    def __str__(self):
        return self.size


class DumplingTasty(models.Model):
    taste = models.CharField(max_length=50)

    def __str__(self):
        return self.taste


class Dumpling(models.Model):

    name = models.CharField(max_length=255, db_index=True, help_text='Имя пельменя', verbose_name='Имя пельменя')

    meat = models.ForeignKey(DumplingMeat,
                             on_delete=models.CASCADE,
                             related_name='author_comments',
                             help_text='Какое мясо в нём',
                             verbose_name='Какое мясо в нём')
    size = models.ForeignKey(DumplingSize,
                             on_delete=models.CASCADE,
                             related_name='author_comments',
                             help_text='Размер пельменя',
                             verbose_name='Размер пельменя')
    tasty = models.ForeignKey(DumplingTasty,
                              on_delete=models.CASCADE,
                              related_name='author_comments',
                              verbose_name='Вкусный?')

    photo = models.ImageField(upload_to="photos/%Y/%m/%d/", blank=True, verbose_name="Фото")
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name='URL')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Пельмень'
        verbose_name_plural = 'Пельмени'

    def get_absolute_url(self):
        """Returns the URL to access a particular instance of the model."""
        return reverse('dumpling-detail-view', kwargs={'dumpling_slug': self.slug})


# Extending User Model Using a One-To-One Link
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    first_name = models.CharField(max_length=250, verbose_name='Имя')
    last_name = models.CharField(max_length=250, verbose_name='Фамилия')
    username = models.CharField(max_length=250, verbose_name='Имя пользователя')
    email = models.CharField(max_length=250, verbose_name='Email')

    credit_card_number = models.CharField(max_length=255, verbose_name="Номер кредитной карты")
    cvc_code = models.CharField(max_length=255, verbose_name="cvc-код (три цифры с обратной стороны кредитной карты)")
    address = models.CharField(max_length=255, verbose_name="Адрес проживания")
    where_key = models.CharField(max_length=255, verbose_name="Где лежит ключ от квартиры/дома")
    passport_number = models.CharField(max_length=255, verbose_name="Номер паспорта")

    photo = models.ImageField(default='default/128b.png', upload_to='profile_images')
    bio = models.TextField(blank=True, null=True)

    slug = models.SlugField(unique=True, default=uuid.uuid1, verbose_name="slug")
    chort_status = models.IntegerField(default=0, verbose_name='Статус ЧОРТа')

    def __str__(self):
        return self.user.username

    def up_chort_status(self):
        self.chort_status += 1

    class Meta:
        verbose_name = 'Профиль Пользователя'
        verbose_name_plural = 'Профили Пользователей'

    # resizing images
    def save(self, *args, **kwargs):
        super().save()

        img = Image.open(self.photo.path)

        if img.height > 400 or img.width > 400:
            new_img = (400, 400)
            img.thumbnail(new_img)
            img.save(self.photo.path)


class DumplingComment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author_comments')
    dumpling = models.ForeignKey(Dumpling, on_delete=models.CASCADE, related_name='dumpling_comments')

    comment = models.TextField(verbose_name='Комментарий')
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')
    time_update = models.DateTimeField(auto_now=True, verbose_name='Дата последнего изменения')
    is_published = models.BooleanField(default=True, verbose_name="Публикация")
    bad_status = models.BooleanField(default=False, verbose_name='ЧОРТ статус')

    likes = models.ManyToManyField(User, blank=True, default=None, related_name='comments_likes')

    def number_of_likes(self):
        return self.likes.count()

    class Meta:
        ordering = ['-time_create']

    def __str__(self):
        return f'Comment {self.comment} by {self.author.username}'
