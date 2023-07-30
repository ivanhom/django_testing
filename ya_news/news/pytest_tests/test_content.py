import pytest

from news.models import Comment, News
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
    object_list_from_db = News.objects.all().order_by('-date')
    all_dates = [news.date for news in object_list]
    all_dates_from_db = [news.date for news in object_list_from_db]
    assert all_dates == all_dates_from_db[:settings.NEWS_COUNT_ON_HOME_PAGE]


@pytest.mark.django_db
def test_comments_order(client, couple_of_comments, news, news_detail_url):
    """Комментарии на странице отдельной новости отсортированы в
    хронологическом порядке: старые в начале списка, новые — в конце.
    """
    response = client.get(news_detail_url)
    assert 'news' in response.context
    all_comments = news.comment_set.all()
    all_comments_from_db = Comment.objects.all().order_by('created')
    all_dates = [comment.created for comment in all_comments]
    all_dates_from_db = [comment.created for comment in all_comments_from_db]
    assert all_dates == all_dates_from_db


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
