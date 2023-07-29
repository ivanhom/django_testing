import pytest

from yanews import settings


@pytest.mark.django_db
def test_news_count(client, couple_of_news, home_url):
    """На домашнюю страницу выводится не более 10 записей с новостями."""
    response = client.get(home_url)
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, couple_of_news, home_url):
    """Новости отсортированы от самой свежей к самой старой.
    Свежие новости в начале списка.
    """
    response = client.get(home_url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(client, couple_comments, news, news_detail_url):
    """Комментарии на странице отдельной новости отсортированы в
    хронологическом порядке: старые в начале списка, новые — в конце.
    """
    response = client.get(news_detail_url)
    assert 'news' in response.context
    all_comments = news.comment_set.all()
    assert all_comments[0].created < all_comments[1].created


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, form_in_list',
    (
        (pytest.lazy_fixture('user_client'), True),
        (pytest.lazy_fixture('client'), False),
    ),
)
def test_form_availability_for_different_users(
    form_in_list, news_detail_url, parametrized_client
):
    """Анонимному пользователю недоступна форма для отправки комментария
    на странице отдельной новости, а авторизованному доступна.
    """
    response = parametrized_client.get(news_detail_url)
    assert ('form' in response.context) is form_in_list
