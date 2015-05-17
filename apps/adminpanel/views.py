from datetime import date, timedelta

from mongoengine import *
from mongoengine.queryset import Q

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic import View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render_to_response

import logging
logger = logging.getLogger(__name__)

from apps.chat.models import Chats, Messages


class ManagerChatsView(View):

    def get(self, request, *args, **kwargs):
        chats_list = Chats.objects.get_all()
        paginator = Paginator(chats_list, 15) # Show 25 contacts per page

        page = request.GET.get('page')
        try:
            chats = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            chats = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            chats = paginator.page(paginator.num_pages)
        return render_to_response('managechats.html', {'chats': chats, })

    @method_decorator(login_required(login_url='/admin'))
    def dispatch(self, *args, **kwargs):
        return super(ManagerChatsView, self).dispatch(*args, **kwargs)


class ClearChatsView(View):
    # chat lifetime in days
    CHAT_LIFETIME = 1

    def get(self, request, *args, **kwargs):
        try:
            # delete closed chats
            msg = Chats.delete_closed_chat() + ' chat(s) deleted!'
            logger.info(msg)

            # auto close chats by time limit
            chats = Chats.objects.get_old_chat(self.CHAT_LIFETIME)
            for chat in chats:
                chat.close_auto_chat()
        except Exception as err:
            # @TODO Fix. Error: Chats matching query does not exist.
            msg = 'Error: ' + str(err)
            logger.error(msg)

        return render_to_response('clearchats.html', {'msg': msg, })

    @method_decorator(login_required(login_url='/admin'))
    def dispatch(self, *args, **kwargs):
         return super(ClearChatsView, self).dispatch(*args, **kwargs)