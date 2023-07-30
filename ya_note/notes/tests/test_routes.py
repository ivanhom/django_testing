from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    """Проверка маршрутов."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='Valera')
        cls.anoter_user = User.objects.create(username='Igor')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='the_slug',
            author=cls.user
        )

    def test_pages_availability_for_anonymous_user(self):
        """Проверка доступа к URL адресам анонимного пользователя."""
        urls = (
            '/',
            '/auth/login/',
            '/auth/logout/',
            '/auth/signup/',
        )
        for name in urls:
            with self.subTest(name=name):
                response = self.client.get(name)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_user(self):
        """Проверка доступа к URL адресам залогиненного пользователя."""
        urls = (
            '/',
            '/add/',
            '/notes/',
            '/done/',
            '/auth/login/',
            '/auth/logout/',
            '/auth/signup/',
        )
        self.client.force_login(self.user)
        for name in urls:
            with self.subTest(name=name):
                response = self.client.get(name)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_note_edit_watch_and_delete(self):
        """Проверка доступа к просмотру, редактированию и удалению автором
        заметки и проверка запрета доступа к заметке другого пользователя.
        """
        users_statuses = (
            (self.user, HTTPStatus.OK),
            (self.anoter_user, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('/edit/', '/note/', '/delete/'):
                with self.subTest(user=user, name=name):
                    url = f'{name}{self.note.slug}/'
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_user(self):
        """Проверка переадресации закрытых для
        анонимного пользователя URL адресов.
        """
        redirecting_urls = (
            '/add/',
            (f'/edit/{self.note.slug}/'),
            (f'/note/{self.note.slug}/'),
            (f'/delete/{self.note.slug}/'),
            '/notes/',
            '/done/'
        )
        login_url = '/auth/login/'
        for name in redirecting_urls:
            with self.subTest(name=name):
                redirect_url = f'{login_url}?next={name}'
                response = self.client.get(name)
                self.assertRedirects(response, redirect_url)
