from django.db import models
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View

from apps.messaging.forms import ConversationForm, MessageForm
from apps.messaging.models import Conversation, Message


class ConversationAddView(View):
    def get(self, request):
        form = ConversationForm(request_user=request.user)
        return render(request, 'messaging/conversation_add.html', {'form': form})

    def post(self, request):
        form = ConversationForm(request.POST, request_user=request.user)
        if form.is_valid():
            user1 = request.user
            user2 = form.cleaned_data['user2']
            subject = form.cleaned_data['subject']
            text = form.cleaned_data['text']

            conversation = Conversation.objects.create(
                user1=user1,
                user2=user2,
                subject=subject,
            )

            Message.objects.create(
                conversation=conversation,
                sender=user1,
                text=text,
            )
            return redirect('conversation-detail', conversation_id=conversation.id)
        return render(request, 'messaging/conversation_add.html', {'form': form})


class ConversationDetailView(View):
    def get(self, request, conversation_id):
        conversation = get_object_or_404(
            Conversation,
            id=conversation_id,
        )

        if request.user not in conversation.participants():
            return redirect('conversation-list')

        messages = conversation.messages.order_by('timestamp')

        unread = messages.filter(is_read=False).exclude(sender=request.user)
        unread.update(is_read=True)

        form = MessageForm()

        return render(
            request,
            'messaging/conversation_detail.html',
            {'conversation': conversation, 'messages': messages, 'form': form},
        )

    def post(self, request, conversation_id):
        conversation = get_object_or_404(
            Conversation,
            id=conversation_id,
        )

        if request.user not in conversation.participants():
            return redirect('conversation-list')

        form = MessageForm(request.POST)
        if form.is_valid():
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                text=form.cleaned_data['text'],
            )
        return redirect('conversation-detail', conversation_id=conversation.id)


class ConversationListView(View):
    def get(self, request):
        conversations = Conversation.objects.filter(
            models.Q(user1=request.user) | models.Q(user2=request.user)
        ).order_by('-updated_at')

        return render(request, 'messaging/conversation_list.html', {'conversations': conversations})
