import pytest
from django.urls import reverse

from apps.messaging.models import Conversation, Message


@pytest.mark.django_db
def test_conversation_add_view_get(client, user):
    client.force_login(user)
    response = client.get(reverse('conversation-add'))
    assert response.status_code == 200
    assert 'form' in response.context


@pytest.mark.django_db
def test_conversation_add_view_post(client, user, user_2):
    client.force_login(user)
    data = {
        'user2': user_2.id,
        'subject': 'Test subject',
        'text': 'Hello there',
    }
    response = client.post(reverse('conversation-add'), data)
    assert response.status_code == 302

    conversation = Conversation.objects.first()
    assert conversation.subject == 'Test subject'
    assert Message.objects.filter(conversation=conversation).exists()


@pytest.mark.django_db
def test_conversation_list_view(client, user, conversation):
    client.force_login(user)
    response = client.get(reverse('conversation-list'))
    assert response.status_code == 200
    assert conversation in response.context['conversations']


@pytest.mark.django_db
def test_conversation_detail_view_get(client, user, conversation, message):
    client.force_login(user)
    url = reverse('conversation-detail', args=[conversation.id])
    response = client.get(url)
    assert response.status_code == 200
    assert response.context['conversation'] == conversation
    assert message in response.context['messages']


@pytest.mark.django_db
def test_conversation_detail_view_post(client, user, conversation):
    client.force_login(user)
    url = reverse('conversation-detail', args=[conversation.id])
    response = client.post(url, data={'text': 'Reply message'})
    assert response.status_code == 302
    assert Message.objects.filter(conversation=conversation, text='Reply message').exists()
