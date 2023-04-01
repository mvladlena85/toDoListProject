import datetime

from toDoListProject.bot.models import TgUser
from toDoListProject.bot.tg.client import TgClient
from toDoListProject.goals.models import Goal, GoalCategory


class BotCommands:

    def __init__(self, user: TgUser, client: TgClient):
        self.user = user
        self.client = client

    def get_goals_list(self):
        goals = Goal.objects.filter(user_id=self.user.user_id)
        message_text = ''
        for goal in goals:
            message_text += f'#{goal.id} {goal.title} \n'
        self.client.send_message(self.user.chat_id, message_text)
        return message_text

    def create_goal(self, offset) -> int:
        self.goal_category: GoalCategory
        self.goal_title: str
        self.goal_description: str

        #Шаг 1: выбор категории
        categories = GoalCategory.objects.filter(user_id=self.user.user_id,
                                                 is_deleted=False)
        dict_categories = {item.title: item for item in categories}
        text = f''
        for category in categories:
            text += f'{category.title}\n'
        message_text = f'Выберите категорию: \n{text}\n' \
                       f'Для отмены введи /cancel'
        self.client.send_message(self.user.chat_id, message_text)

        flag = True
        while flag:
            category, offset = self.wait_for_free_text_answer(offset=offset)
            if category in dict_categories:
                self.goal_category = dict_categories.get(category)
                flag = False
            elif category == '/cancel':
                self.client.send_message(self.user.chat_id, 'Создание цели отменено.')
                return offset
            else:
                self.client.send_message(self.user.chat_id, "Такая категория не существует! \n "
                                                            "Введите категорию еще раз:")

        # Шаг 2: создание названия цели
        self.client.send_message(self.user.chat_id, 'Введите название цели\n'
                                                    'Для отмены введи /cancel')
        self.goal_title, offset = self.wait_for_free_text_answer(offset=offset)
        if self.goal_title == '/cancel':
            self.client.send_message(self.user.chat_id, 'Создание цели отменено.')
            return offset

        # Шаг 3: создание описания цели
        self.client.send_message(self.user.chat_id, 'Введите описание цели \n'
                                                    'Для отмены введи /cancel')
        self.goal_description, offset = self.wait_for_free_text_answer(offset=offset)
        if self.goal_description == '/cancel':
            self.client.send_message(self.user.chat_id, 'Создание цели отменено.')
            return offset

        goal = Goal(title=self.goal_title, category=self.goal_category, description=self.goal_description, user=self.user.user,
                    due_date=datetime.datetime.today() + datetime.timedelta(weeks=2))
        goal.save()
        self.client.send_message(self.user.chat_id, f'Цель создана: #{goal.id} {goal.title}')
        return offset

    def wait_for_free_text_answer(self, offset: int) -> (str, int):
        flag = True
        text: str = ''
        while flag:
            response = self.client.get_updates(offset=offset)
            for item in response.result:
                offset = item.update_id + 1
                text = item.message.text
                flag = False
        return text, offset


