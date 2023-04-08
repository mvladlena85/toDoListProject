from typing import Callable

import pytest
from django.urls import reverse
from faker import Faker

from rest_framework import status

from toDoListProject.goals.models import Board, BoardParticipant


@pytest.fixture
def create_board_data(faker: Faker) -> Callable:
    def _wrapper(**kwargs) -> dict:
        data = {
            'title': faker.word()
        }
        data |= kwargs
        return data
    return _wrapper


class TestBoardCreateView:
    url = reverse('goals:create_board')

    def test_auth_required(self, client, create_board_data):
        """
        Неавторизованный пользователь не может создать доску
        """
        response = client.post(self.url, data=create_board_data())
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_board_creation(self, auth_client, create_board_data):
        """
        Проверка возвращаемого ответа при успешном создании доски
        """
        data = create_board_data()
        response = auth_client.post(self.url, data=data)
        assert response.status_code == status.HTTP_201_CREATED
        assert set(response.json().keys()) == {"id", "created", "updated", "title", "is_deleted"}
        assert response.json()['title'] == data['title']
        assert response.json()['is_deleted'] is False
        assert response.json()['id'] == Board.objects.last().id
        assert response.json()['created'] is not None
        assert response.json()['updated'] is not None

    @pytest.mark.django_db
    def test_board_user_relation(self, auth_client, user, create_board_data):
        """Проверка, что созданная доска:
         - корректно связана с пользователем
         - роль пользователя owner"""
        response = auth_client.post(self.url, data=create_board_data())
        bord_participant_obj = BoardParticipant.objects.last()
        print("pert:", bord_participant_obj.role, bord_participant_obj.board_id, bord_participant_obj.user_id)
        print("resp:", response.json())
        assert bord_participant_obj.board_id == response.json()["id"]
        assert bord_participant_obj.user_id == user.id
        assert bord_participant_obj.role == BoardParticipant.Role.owner

    @pytest.mark.django_db
    def test_unable_create_deleted_board(self, auth_client, create_board_data):
        """
        Нельзя создать доску с флагом is_deleted = True
        """
        data = create_board_data(is_deleted=True)
        response = auth_client.post(self.url, data=data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()['is_deleted'] is False
