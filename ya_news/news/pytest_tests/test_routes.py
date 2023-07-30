from http import HTTPStatus

from pytest_django.asserts import assertRedirects
import pytest


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('/', ''),
        ('/news/', pytest.lazy_fixture('news_id_for_url')),
        ('/auth/login/', ''),
        ('/auth/logout/', ''),
        ('/auth/signup/', '')
    ),
)
def test_pages_availability_for_anonymous_user(args, client, name, news):
    """Проверка доступа к URL адресам анонимного пользователя."""
    url = name + args
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
    ('/edit_comment/', '/delete_comment/'),
)
def test_pages_availability_for_comment_edit_and_delete(
    parametrized_client, comment, expected_status, name
):
    """Проверка доступа к редактированию и удалению комментария
    автором и проверка запрета доступа другому пользователю.
    """
    url = f'{name}{comment.id}/'
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('/edit_comment/', '/delete_comment/'),
)
def test_redirect_for_anonymous_user(client, comment, name):
    """Проверка переадресации закрытых для
    анонимного пользователя URL адресов.
    """
    login_url = '/auth/login/'
    url = f'{name}{comment.id}/'
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
