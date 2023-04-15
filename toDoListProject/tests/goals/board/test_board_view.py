import json

import pytest
from django.urls import reverse
from rest_framework import status

from toDoListProject.goals.models import BoardParticipant, GoalCategory, Goal


@pytest.mark.django_db
class TestBoardView:

    @staticmethod
    def get_url(board_id: int) -> str:
        return reverse('goals:board', kwargs={'pk': board_id})

    @pytest.fixture(autouse=True)
    def setup(self, board_participant):
        self.url = self.get_url(board_participant.board_id)

    def test_auth_required(self, client):
        """
        Неавторизованный пользователь не может просмотреть доску
        """
        response = client.get(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unable_create_deleted_board(self, auth_client, board):
        """
        Нельзя просмотреть доску с флагом is_deleted = True
        """
        board.is_deleted = True
        board.save()
        response = auth_client.get(self.url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_response(self, auth_client):
        """
        TODO: Проверка, что структура ответа соответствует документации
        """
        response = auth_client.get(self.url)

    def test_failed_to_retrieve_other_user_board(self, client, user_factory):
        """
        Проверка, что другой пользователь не может просматривать чужие доски, если ему не выдали права
        """
        user = user_factory.create()
        client.force_login(user)
        response = client.get(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.parametrize("role", [BoardParticipant.Role.writer, BoardParticipant.Role.reader])
    def test_user_with_roles_writer_or_reader_can_access_board(self, role, board, client, user_factory):
        """
        Проверка, что другой пользователь с ролью Writer может просматривать чужую доску        """
        user = user_factory.create()
        board_participant = BoardParticipant(user_id=user.pk, board_id=board.pk, role=role)
        board_participant.save()
        client.force_login(user)
        response = client.get(self.url)
        assert response.status_code == status.HTTP_200_OK

    def test_author_can_update_board(self, auth_client):
        """
        Создатель доски может ее изменить (добавить пользователей, сменить имя)
        """
        data = {'title': 'new title'}
        response = auth_client.patch(self.url, data=data)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()['title'] == "new title"

    def test_fail_to_update_board_by_non_author(self, client, user_factory):
        """
        Пользователь, не имеющий доступа к доске, не может ее изменить (добавить пользователей, сменить имя)
        """
        user = user_factory.create()
        client.force_login(user)
        data = {'title': 'new title'}
        response = client.patch(self.url, data=data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.parametrize("role", [BoardParticipant.Role.writer, BoardParticipant.Role.reader])
    def test_fail_to_update_board_by_writer_or_reader(self, client, user_factory, board, role):
        """
        Пользователь с ролью writer не может ее изменить (добавить пользователей, сменить имя)
        """
        user = user_factory.create()
        board_participant = BoardParticipant(user_id=user.pk, board_id=board.pk,
                                             role=role)
        board_participant.save()
        client.force_login(user)
        data = {'title': 'new title'}
        response = client.patch(self.url, data=data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_fail_to_delete_board_by_non_author(self, client, user_factory):
        """
        Не создатель доски не может ее удалить
        """
        user = user_factory.create()
        client.force_login(user)
        response = client.delete(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.parametrize("role", [BoardParticipant.Role.writer, BoardParticipant.Role.reader])
    def test_fail_to_delete_board_by_writer_or_reader(self, client, user_factory, board, role):
        """
        Пользователи доски с ролями writer и reader не могут ее удалить
        """
        user = user_factory.create()
        board_participant = BoardParticipant(user_id=user.pk, board_id=board.pk,
                                             role=role)
        board_participant.save()
        client.force_login(user)
        response = client.delete(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_author_can_delete_board(self, auth_client):
        """
        Создатель доски может ее удалить
        """
        response = auth_client.delete(self.url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_category_marked_deleted_when_board_is_deleted(self, auth_client, board, user, category_factory):
        """
        При удалении доски, ее категории помечаются is_deleted = True
        """
        category_factory.create(board=board, user=user)
        response = auth_client.delete(self.url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert GoalCategory.objects.get(board_id=board.pk).is_deleted is True

    def test_goal_marked_archived_when_board_is_deleted(self, auth_client, board, user, category_factory, goal_factory):
        """
        При удалении доски ее цели получают статус archived
        """
        category = category_factory.create(board=board, user=user)
        goal_factory.create_batch(5, category=category, user=user)
        response = auth_client.delete(self.url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        for state in Goal.objects.filter(category=category):
            assert state.status == Goal.Status.archived

    def test_assign_new_users_to_the_board(self, auth_client, client, board, user_factory):
        """
        Создатель доски может расшарить доску для других пользователей
        """
        user = user_factory.create()
        data = {
            'title': board.title,
            'participants':
                [
                    {
                        'role': 2,
                        'user': user.username
                    }
                ],
        }
        response = auth_client.put(self.url, data=data)
        print(response.json())
        assert response.status_code == status.HTTP_200_OK
        client.force_login(user)
        response2 = client.get(self.url)
        assert response2.status_code == status.HTTP_200_OK
        assert response.json()['title'] == board.title
