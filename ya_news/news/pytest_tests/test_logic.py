from http import HTTPStatus

from pytest_django.asserts import assertRedirects, assertFormError
import pytest

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
    client, form_data, news_detail_url
):
    """Анонимный пользователь не может отправить комментарий."""
    client.post(news_detail_url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_can_create_comment(
    user_client, form_data, news, news_detail_url, user
):
    """Авторизованный пользователь может отправить комментарий."""
    response = user_client.post(news_detail_url, data=form_data)
    assertRedirects(response, f'{news_detail_url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == user


def test_user_cant_use_bad_words(user_client, news_detail_url):
    """Если комментарий содержит запрещённые слова,
    он не будет опубликован, а форма вернёт ошибку.
    """
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = user_client.post(news_detail_url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_delete_comment(
    user_client, delete_comment_url, news_detail_url
):
    """Авторизованный пользователь может удалять свои комментарии."""
    comments_count_before = Comment.objects.count()
    response = user_client.delete(delete_comment_url)
    assertRedirects(response, f'{news_detail_url}#comments')
    comments_count_after = Comment.objects.count()
    assert comments_count_before != comments_count_after


def test_user_cant_delete_comment_of_another_user(
    another_user_client, delete_comment_url
):
    """Авторизованный пользователь не может удалять чужие комментарии."""
    comments_count_before = Comment.objects.count()
    response = another_user_client.delete(delete_comment_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count_after = Comment.objects.count()
    assert comments_count_before == comments_count_after


def test_author_can_edit_comment(
    user, user_client, comment, edit_comment_url, form_data, news_detail_url
):
    """Авторизованный пользователь может редактировать свои комментарии."""
    response = user_client.post(edit_comment_url, data=form_data)
    assertRedirects(response, f'{news_detail_url}#comments')
    comment.refresh_from_db()
    assert comment.text == form_data['text']
    assert comment.author == user


def test_user_cant_edit_comment_of_another_user(
    another_user, another_user_client, comment, edit_comment_url, form_data
):
    """Авторизованный пользователь не может редактировать чужие комментарии."""
    response = another_user_client.post(edit_comment_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text != form_data['text']
    assert comment.author != another_user
