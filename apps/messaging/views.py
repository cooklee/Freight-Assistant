from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
# TODO (style): W tym pliku używasz tylko Q z models. Czytelniej jest: from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View

from apps.messaging.forms import ConversationForm, MessageForm
from apps.messaging.models import Conversation, Message


class ConversationAddView(LoginRequiredMixin, View):
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

            # TODO (data): Rozważ zabezpieczenie przed rozmową z samym sobą (user1 == user2),

            # TODO (data): Jeśli w domenie ma istnieć tylko jedna rozmowa na parę użytkowników,
            # TODO (data): rozważ get_or_create / UniqueConstraint na (user1,user2) z normalizacją kolejności.
            # TODO (data): Inaczej łatwo powstają duplikaty A->B i B->A.

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


class ConversationDetailView(LoginRequiredMixin, View):
    def get(self, request, conversation_id):
        conversation = get_object_or_404(
            Conversation,
            id=conversation_id,
        )

        if request.user not in conversation.participants():
            # TODO (security): tutaj bym skorzystał z mechanizmów UserPassesTestMixin by nie mieszać zabezpieczeń z logiką biznesową
            return redirect('conversation-list')

        messages = conversation.messages.order_by('timestamp')
        # TODO (perf): Jeśli wiadomości może być dużo, dodaj paginację (np. ostatnie 50) lub lazy loading.

        unread = messages.filter(is_read=False).exclude(sender=request.user)
        unread.update(is_read=True)
        # TODO (perf): To robi UPDATE przy każdym wejściu do rozmowy (nawet jeśli brak nieprzeczytanych).
        #  Możesz dodać if unread.exists(): unread.update(...)


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
            # TODO (security): Analogicznie jak w GET
            return redirect('conversation-list')

        form = MessageForm(request.POST)
        if form.is_valid():
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                text=form.cleaned_data['text'],
            )
            # TODO (data): Conversation.updated_at aktualizuje się tylko gdy Conversation się zapisze.
            #  Dodanie Message nie zmienia Conversation, więc wątek może nie “podbić się” na liście.
            # TODO (data): Rozważ conversation.save(update_fields=["updated_at"]) po dodaniu wiadomości


        # TODO (ux): Jeśli form nievalid, teraz tracisz błędy (bo redirect). Lepiej wyrenderować ten sam widok
        # TODO (ux): z błędami formularza (albo chociaż dodać messages.error).
        return redirect('conversation-detail', conversation_id=conversation.id)


class ConversationListView(LoginRequiredMixin, View):
    def get(self, request):
        conversations = Conversation.objects.filter(
            models.Q(user1=request.user) | models.Q(user2=request.user)
        ).order_by('-updated_at')

        # TODO (perf): Jeśli wyświetlasz listę + ostatnia wiadomość/unread count, rozważ prefetch_related('messages')
        # TODO (perf): i/lub adnotacje, żeby uniknąć N+1 w template.
        # TODO (ux): Dodaj paginację, jeśli konwersacji może być dużo.

        return render(request, 'messaging/conversation_list.html', {'conversations': conversations})
