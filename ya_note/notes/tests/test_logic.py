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

    def check_note(self, note_obj, form_data):
        self.assertEqual(note_obj.title, form_data['title'])
        self.assertEqual(note_obj.text, form_data['text'])
        self.assertEqual(note_obj.slug, form_data['slug'])
        self.assertEqual(note_obj.author, self.user)

    def test_user_can_create_note(self):
        """Пользователь может создать заметку."""
        add_url = reverse('notes:add')
        done_url = reverse('notes:success')
        self.client.force_login(self.user)
        response = self.client.post(add_url, data=self.new_form_data)
        self.assertRedirects(response, done_url)
        self.assertEqual(Note.objects.count(), (self.db_obj_default + 1))
        new_note = Note.objects.get(slug=self.new_form_data['slug'])
        self.check_note(new_note, self.new_form_data)

    def test_anonymous_user_can_not_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        add_url = reverse('notes:add')
        login_url = reverse('users:login')
        response = self.client.post(add_url, data=self.form_data)
        redirect_url = f'{login_url}?next={add_url}'
        self.assertRedirects(response, redirect_url)
        self.assertEqual(Note.objects.count(), self.db_obj_default)

    def test_not_unique_slug(self):
        """Нельзя создать заметку, если slug неуникален."""
        add_url = reverse('notes:add')
        self.client.force_login(self.user)
        response = self.client.post(add_url, data=self.form_data)
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
        add_url = reverse('notes:add')
        done_url = reverse('notes:success')
        self.form_data.pop('slug')
        self.client.force_login(self.user)
        response = self.client.post(add_url, data=self.form_data)
        self.assertRedirects(response, done_url)
        self.assertEqual(Note.objects.count(), (self.db_obj_default + 1))
        new_note = Note.objects.get(id=(self.db_obj_default + 1))
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_user_can_edit_note(self):
        """Автор заметки может её отредактировать."""
        edit_url = reverse('notes:edit', args=(self.note.slug,))
        done_url = reverse('notes:success')
        self.client.force_login(self.user)
        response = self.client.post(edit_url, self.new_form_data)
        self.assertRedirects(response, done_url)
        self.note.refresh_from_db()
        self.check_note(self.note, self.new_form_data)

    def test_another_user_cant_edit_note(self):
        """Пользователь не может редактировать чужую заметку."""
        edit_url = reverse('notes:edit', args=(self.note.slug,))
        self.client.force_login(self.anoter_user)
        response = self.client.post(edit_url, self.new_form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.check_note(self.note, self.form_data)

    def test_user_can_delete_note(self):
        """Автор заметки может её удалить."""
        delete_url = reverse('notes:delete', args=(self.note.slug,))
        done_url = reverse('notes:success')
        self.client.force_login(self.user)
        response = self.client.post(delete_url)
        self.assertRedirects(response, done_url)
        self.assertEqual(Note.objects.count(), (self.db_obj_default - 1))

    def test_other_user_cant_delete_note(self):
        """Пользователь не может удалить чужую заметку."""
        delete_url = reverse('notes:delete', args=(self.note.slug,))
        self.client.force_login(self.anoter_user)
        response = self.client.post(delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), self.db_obj_default)
