import datetime
from bson.objectid import ObjectId
from bson.errors import InvalidId
from mongoengine import *
from django.utils.translation import ugettext as _
from apps.chat.querysets import ChatsQuerySet


class Messages(EmbeddedDocument):
    _id = ObjectIdField(required=True)
    user_token = ObjectIdField(required=True)
    msg = StringField(min_length=1, max_length=144, required=True)
    system = BooleanField(default=False)
    created = DateTimeField(default=datetime.datetime.utcnow())

    @staticmethod
    def prepare_message(msg, user_token, system=True):
        """
        Gets message
        :param msg: String message text
        :param system: Boolean true as default
        :param user_token: ObjectId
        :return: Messages
        """
        message = Messages(_id=ObjectId(), user_token=user_token, msg=msg, system=system)
        message.validate()
        return message


class LongPolling(EmbeddedDocument):
    _id = ObjectIdField(required=True)
    user_token = ObjectIdField(required=True)


class Chats(Document):
    STATUS_DRAFT = 'draft'
    STATUS_READY = 'ready'
    STATUS_CLOSED = 'closed'
    HTTP_CODE = 200
    HTTP_MSG = 'Ok'

    MSG_CREATE_CHAT = 'Welcome to SFChat! <br> Please send code: <mark>%(chat_token)s</mark> to Talker'
    MSG_JOIN_CHAT_YOU = 'Talker was successfully joined to chat'
    MSG_JOIN_CHAT_TALKER = 'Chat is ready to use'
    MSG_CHAT_CLOSE_TALKER = 'Thank you for using SFChat.<br> Chat was successfully closed by Talker.'
    MSG_CHAT_CLOSE_YOU = 'Thank you for using SFChat<br>Current chat was successfully closed.'


    # it's used for authentication
    is_staff = True

    status = StringField(max_length=8,
                         choices=((STATUS_DRAFT, STATUS_DRAFT),
                                  (STATUS_READY, STATUS_READY),
                                  (STATUS_CLOSED, STATUS_CLOSED)), default=STATUS_DRAFT)
    user_tokens = ListField(ObjectIdField())
    messages = ListField(EmbeddedDocumentField(Messages))
    long_polling = ListField(EmbeddedDocumentField(LongPolling))
    created = DateTimeField(default=datetime.datetime.utcnow())

    meta = {'queryset_class': ChatsQuerySet}

    @property
    def count(self):
        return len(self.messages)

    def code(self):
        return self.HTTP_CODE

    def msg(self):
        return self.HTTP_MSG

    def clean(self):
        if len(self.user_tokens) > 2:
            msg = 'Length user_tokens must be equal or less then 2.'
            raise ValidationError(msg)

    @staticmethod
    def create_chat():
        """
        Create chat
        :return: Dictionary {'chat_token': '', 'user_token': ''}
        """
        chat_token = ObjectId()
        user_token = ObjectId()
        msg = _(Chats.MSG_CREATE_CHAT) % {'chat_token': str(chat_token)}
        message = Messages.prepare_message(msg=msg, user_token=user_token)
        chat = Chats(id=chat_token, messages=[message], user_tokens=[user_token])
        chat.save()
        return {'chat_token': str(chat_token), 'user_token': str(user_token)}

    @staticmethod
    def join_to_chat(chat_token):
        """
        Join to chat
        :param chat_token: String
        :return: Mix false or user_token if ok
        """
        try:
            chat = Chats.objects.get_all_by_token(chat_token)
        except (TypeError, InvalidId, DoesNotExist) as ex:
            return False

        if len(chat.user_tokens) > 1:
            return False

        user_token = ObjectId()
        prepared_messages = [
            Messages.prepare_message(msg=_(Chats.MSG_JOIN_CHAT_TALKER), user_token=user_token),
            Messages.prepare_message(msg=_(Chats.MSG_JOIN_CHAT_YOU), user_token=chat.user_tokens[0])
        ]
        chat.update(set__status=Chats.STATUS_READY, push__user_tokens=user_token, push_all__messages=prepared_messages)

        return str(user_token)

    @staticmethod
    def validate_chat_token(chat_token):
        """
        Validate chat token
        :param chat_token: String
        :return: Boolean
        """
        try:
            chat = Chats.objects.get_id_by_token(chat_token)
            result = True
        except (TypeError, InvalidId, DoesNotExist) as ex:
            result = False
        return result

    @staticmethod
    def get_chat(chat_token, user_token):
        """
        Gets data that's related to current user
        :param chat_token: String
        :param user_token: String
        :return: Boolean
        """
        try:
            result = Chats.objects.get_chat(chat_token, user_token)
            result.messages = list(filter(lambda item: user_token == str(item.user_token), result.messages))
        except (TypeError, InvalidId, DoesNotExist) as ex:
            result = False

        return result

    def add_message(self, user_token, messages=[], system=False):
        """
        Add messages
        :param user_token: String
        :param messages: Array
        :param system: Boolean
        :return: Boolean
        """
        talker_token = list(filter(lambda item: user_token != str(item), self.user_tokens))
        if not talker_token:
            return False

        try:
            prepared_messages = []
            for item in messages:
                prepared_messages.append(Messages.prepare_message(msg=item['msg'], user_token=talker_token[0], system=system))

            self.update(push_all__messages=prepared_messages)
            result = True
        except (TypeError, InvalidId, ValidationError) as ex:
            result = False

        return result

    def delete_message(self, messages):
        """
         Delete messages
         :param messages: Array
         :return: Boolean
        """
        try:
            for item in messages:
                # pull_all supports only a single field depth
                self.update(pull__messages___id=ObjectId(item['_id']))
            result = True
        except (TypeError, InvalidId, ValidationError) as ex:
            result = False

        return result

    def delete_chat(self, user_token):
        """
         User init delete chat
         :param user_tocken: ObjectId
         :return: Boolean
        """
        try:
            prepared_messages = [
                Messages.prepare_message(msg=_(self.MSG_CHAT_CLOSE_YOU), user_token=ObjectId(user_token))
            ]
            # it's possible to close "draft" chat
            talker_token = list(filter(lambda item: user_token != str(item), self.user_tokens))
            if talker_token:
                prepared_messages.append(
                    Messages.prepare_message(msg=_(self.MSG_CHAT_CLOSE_TALKER), user_token=talker_token[0])
                )

            self.update(set__status=self.STATUS_CLOSED, push_all__messages=prepared_messages)
            result = True
        except (TypeError, InvalidId, ValidationError) as ex:
            result = False

        return result

    def create_long_polling(self, user_token):
        """
        Create new long polling process and terminate all older one
        :param user_token: String
        :return: String|False process identifier, false if failed
        """
        try:
            # delete all processes
            self.delete_long_polling(user_token)

            process = {'_id': ObjectId(), 'user_token': ObjectId(user_token)}
            self.update(push__long_polling=process)
        except (TypeError, InvalidId, DoesNotExist) as ex:
            return False

        return str(process['_id'])

    def delete_long_polling(self, user_token):
        """
        Delete all processes linked to user_token
        :param user_token:
        """
        self.update(pull__long_polling__user_token=ObjectId(user_token))

    def get_long_polling(self, user_token):
        """
        Gets actual process
        :param user_token: String
        :return: LongPolling|False
        """
        long_polling = list(filter(lambda item: user_token == str(item.user_token), self.long_polling))
        if not long_polling:
            return False

        return long_polling[0]