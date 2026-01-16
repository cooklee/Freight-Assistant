from django.urls import path

from .views import ConversationListView, ConversationAddView, ConversationDetailView
#todo jak w reszcie urlsoów
urlpatterns = [
    path('', ConversationListView.as_view(), name='conversation-list'),

    # Start a new conversation
    path('new/', ConversationAddView.as_view(), name='conversation-add'),

    # View a conversation + send messages
    path('<int:conversation_id>/', ConversationDetailView.as_view(), name='conversation-detail'),
]
