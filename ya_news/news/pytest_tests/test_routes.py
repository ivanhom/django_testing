from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertRedirects
import pytest


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('news_id_for_args')),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None)
    ),
)
def test_pages_availability_for_anonymous_user(args, client, name):
    """Проверка доступа к URL адресам анонимного пользователя."""
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('user_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('another_user_client'), HTTPStatus.NOT_FOUND),
    ),
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_pages_availability_for_comment_edit_and_delete(
    parametrized_client, comment_id_for_args, expected_status, name
):
    """Проверка доступа к редактированию и удалению комментария
    автором и проверка запрета доступа другому пользователю.
    """
    url = reverse(name, args=comment_id_for_args)
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_redirect_for_anonymous_user(client, comment_id_for_args, name):
    """Проверка переадресации закрытых для
    анонимного пользователя URL адресов.
    """
    login_url = reverse('users:login')
    url = reverse(name, args=comment_id_for_args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
