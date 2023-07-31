from time import sleep

from django.urls import reverse
from django.utils import timezone
import pytest

from news.models import Comment, News
from yanews import settings


@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create(username='Пользователь')


@pytest.fixture
def another_user(django_user_model):
    return django_user_model.objects.create(username='Другой пользователь')


@pytest.fixture
def user_client(user, client):
    client.force_login(user)
    return client


@pytest.fixture
def another_user_client(another_user, client):
    client.force_login(another_user)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Текст заголовка',
        text='Текст новости'
    )
    return news


@pytest.fixture
def news_id_for_args(news):
    return news.id,


@pytest.fixture
def news_id_for_url(news):
    return f'{news.id}/'


@pytest.fixture
def comment(news, user):
    comment = Comment.objects.create(
        news=news,
        text='Текст комментария',
        author=user
    )
    return comment


@pytest.fixture
def comment_id_for_args(comment):
    return comment.id,


@pytest.fixture
def couple_of_news():
    today = timezone.now()
    couple_of_news = News.objects.bulk_create(
        News(
            title=f'Новость {index}',
            text='Просто текст',
            date=today - timezone.timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )
    return couple_of_news


@pytest.fixture
def couple_of_comments(news, user):
    couple_of_comments = []
    for index in range(3):
        couple_of_comments.append(Comment.objects.create(
            news=news, author=user, text=f'Tекст №{index}'
        ))
        sleep(0.000001)
    return couple_of_comments


@pytest.fixture
def form_data():
    return {
        'text': 'Новый текст комментария'
    }


@pytest.fixture
def home_url():
    url = reverse('news:home')
    return url


@pytest.fixture
def login_url():
    url = reverse('users:login')
    return url


@pytest.fixture
def news_detail_url(news_id_for_args):
    url = reverse('news:detail', args=news_id_for_args)
    return url


@pytest.fixture
def delete_comment_url(comment_id_for_args):
    url = reverse('news:delete', args=comment_id_for_args)
    return url


@pytest.fixture
def edit_comment_url(comment_id_for_args):
    url = reverse('news:edit', args=comment_id_for_args)
    return url
