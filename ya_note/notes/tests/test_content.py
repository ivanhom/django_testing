from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestContent(TestCase):
    """Проверка контента."""

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

    def test_note_availability_in_list_different_users(self):
        """Проверка отображения созданной заметки в
        списке заметок только у автора заметки.
        """
        list_url = reverse('notes:list')
        users_check = (
            (self.user, self.assertIn),
            (self.anoter_user, self.assertNotIn),
        )
        for user, check in users_check:
            self.client.force_login(user)
            with self.subTest(user=user, check=check):
                response = self.client.get(list_url)
                object_list = response.context['object_list']
                check(self.note, object_list)

    def test_pages_contain_form(self):
        """Проверка наличия форм на страницах
        создания и редактирования заметки.
        """
        add_url = reverse('notes:add')
        edit_url = reverse('notes:edit', args=(self.note.slug,))
        self.client.force_login(self.user)
        for url in (add_url, edit_url):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertIn('form', response.context)
