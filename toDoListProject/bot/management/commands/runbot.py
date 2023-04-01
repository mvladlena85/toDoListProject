from django.core.management import BaseCommand

from toDoListProject.bot.models import TgUser
from toDoListProject.bot.tg.client import TgClient
from toDoListProject.bot.tg.commands import BotCommands
from toDoListProject.bot.tg.dc import Message


class Command(BaseCommand):

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.tg_client = TgClient()
        self.offset = 0

    def handle(self, *args, **options):

        while True:
            res = self.tg_client.get_updates(offset=self.offset)
            for item in res.result:
                self.offset = item.update_id + 1
                print(item.message)
                self.handle_message(item.message)

    def handle_message(self, message: Message):
        tg_user, _created = TgUser.objects.get_or_create(chat_id=message.chat.id)

        if tg_user.user:
            self.handle_authorized_user(tg_user, message)
        else:
            self.handle_unauthorized_user(tg_user)

    def handle_unauthorized_user(self, tg_user: TgUser):
        self.tg_client.send_message(tg_user.chat_id, f'Здравствуйте!')

        verification_code = tg_user.set_verification_code()
        self.tg_client.send_message(tg_user.chat_id, f'Подтвердите, пожалуйста, свой аккаунт. '
                                                     f'Для подтверждения необходимо ввести код:'
                                                     f' {verification_code} на сайте.')

    def handle_authorized_user(self, tg_user: TgUser, message: Message):
        client = self.tg_client
        bot_commander = BotCommands(tg_user, client)
        if message.text == '/goals':
            bot_commander.get_goals_list()
        elif message.text == '/create':
            self.offset = bot_commander.create_goal(offset=self.offset)
        else:
            self.tg_client.send_message(tg_user.chat_id, f'Неизвестная команда')
