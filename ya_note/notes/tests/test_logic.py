from http import HTTPStatus
from pytils.translit import slugify

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestLogic(TestCase):
    """Проверка логики."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='Valera')
        cls.anoter_user = User.objects.create(username='Igor')
        cls.form_data = {
            'title': 'Пятница',
            'text': 'Впереди выходные',
            'slug': 'friday'
        }
        cls.new_form_data = {
            'title': 'Суббота',
            'text': 'Настали выходные',
            'slug': 'saturday'
        }
        cls.note = Note.objects.create(**cls.form_data, author=cls.user)
        cls.db_obj_default = Note.objects.count()
        cls.add_url = reverse('notes:add')
        cls.done_url = reverse('notes:success')
        cls.login_url = reverse('users:login')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))

    def test_user_can_create_note(self):
        """Пользователь может создать заметку."""
        self.client.force_login(self.user)
        response = self.client.post(self.add_url, data=self.new_form_data)
        self.assertRedirects(response, self.done_url)
        self.assertEqual(Note.objects.count(), (self.db_obj_default + 1))
        new_note = Note.objects.get(slug=self.new_form_data['slug'])
        self.assertEqual(new_note.title, self.new_form_data['title'])
        self.assertEqual(new_note.text, self.new_form_data['text'])
        self.assertEqual(new_note.slug, self.new_form_data['slug'])
        self.assertEqual(new_note.author, self.user)

    def test_anonymous_user_can_not_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        response = self.client.post(self.add_url, data=self.form_data)
        redirect_url = f'{self.login_url}?next={self.add_url}'
        self.assertRedirects(response, redirect_url)
        self.assertEqual(Note.objects.count(), self.db_obj_default)

    def test_not_unique_slug(self):
        """Нельзя создать заметку, если slug неуникален."""
        self.client.force_login(self.user)
        # note = Note.objects.create(**self.form_data, author=self.user)
        response = self.client.post(self.add_url, data=self.form_data)
        self.assertFormError(
            response,
            'form',
            'slug',
            errors=(self.note.slug + WARNING)
        )
        self.assertEqual(Note.objects.count(), self.db_obj_default)

    def test_empty_slug(self):
        """При создании заметки, поле slug заполняется
        автоматически, если оно не было заполнено.
        """
        self.form_data.pop('slug')
        self.client.force_login(self.user)
        response = self.client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, self.done_url)
        self.assertEqual(Note.objects.count(), (self.db_obj_default + 1))
        new_note = Note.objects.get(id=(self.db_obj_default + 1))
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_user_can_edit_note(self):
        """Автор заметки может её отредактировать."""
        self.client.force_login(self.user)
        response = self.client.post(self.edit_url, self.new_form_data)
        self.assertRedirects(response, self.done_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.new_form_data['title'])
        self.assertEqual(self.note.text, self.new_form_data['text'])
        self.assertEqual(self.note.slug, self.new_form_data['slug'])
        self.assertEqual(self.note.author, self.user)

    def test_another_user_cant_edit_note(self):
        """Пользователь не может редактировать чужую заметку."""
        self.client.force_login(self.anoter_user)
        response = self.client.post(self.edit_url, self.new_form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.slug, self.form_data['slug'])
        self.assertEqual(self.note.author, self.user)

    def test_user_can_delete_note(self):
        """Автор заметки может её удалить."""
        self.client.force_login(self.user)
        response = self.client.post(self.delete_url)
        self.assertRedirects(response, self.done_url)
        self.assertEqual(Note.objects.count(), (self.db_obj_default - 1))

    def test_other_user_cant_delete_note(self):
        """Пользователь не может удалить чужую заметку."""
        self.client.force_login(self.anoter_user)
        response = self.client.post(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), self.db_obj_default)
