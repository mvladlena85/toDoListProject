from django.db import transaction
from rest_framework import serializers

from toDoListProject.core.models import User
from toDoListProject.core.serializers import UserSerializer
from toDoListProject.goals.models import GoalCategory, Goal, GoalComment, Board, BoardParticipant


class GoalCategoryCreateSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для создания категории
    """
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalCategory
        read_only_fields = ("id", "created", "updated", "user")
        fields = "__all__"

    def validate_board(self, value: Board) -> Board:
        """
        Проверка прав пользователя перед созданием категории
        """
        if not BoardParticipant.objects.filter(board_id=value.pk,
                                               user_id=self.context["request"].user.id,
                                               role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer]):
            raise serializers.ValidationError("Permission Denied")
        return value


class GoalCategorySerializer(serializers.ModelSerializer):
    """
    Сериалайзер для отображения категорий
    """
    user = UserSerializer(read_only=True)

    class Meta:
        model = GoalCategory
        fields = "__all__"
        read_only_fields = ("id", "created", "updated", "user", "board")


class GoalCreateSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для создания цели
    """
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Goal
        read_only_fields = ("id", "created", "updated", "user")
        fields = "__all__"

    def validate_category(self, value: GoalCategory) -> GoalCategory:
        """
        Проверка, есть ли у пользователя права на привязку цели к данной категории
        """
        if value.is_deleted:
            raise serializers.ValidationError("not allowed in deleted category")

        if value.user != self.context["request"].user:
            raise serializers.ValidationError("not owner of category")

        return value


class GoalSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для отображения данных цели
    """
    user = UserSerializer(read_only=True)

    class Meta:
        model = Goal
        fields = "__all__"
        read_only_fields = ("id", "created", "updated", "user")


class GoalCommentCreateSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для создания комментария
    """
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalComment
        fields = "__all__"
        read_only_fields = ("id", "created", "updated", "user")


class GoalCommentSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для отображения комментария
    """
    user = UserSerializer(read_only=True)

    class Meta:
        model = GoalComment
        fields = "__all__"
        read_only_fields = ("id", "created", "updated", "user", "goal")


class BoardCreateSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для создания доски
    """
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Board
        read_only_fields = ("id", "created", "updated", "is_deleted")
        fields = "__all__"

    def create(self, validated_data):
        """
        При создании доски, помимо сохранения данных в БД в таблице goals_board,
        создаем запись в таблице goals_perticiants c данными пользователя, доски
        и роли пользователя Owner
        """
        user = validated_data.pop("user")
        board = Board.objects.create(**validated_data)
        BoardParticipant.objects.create(
            user=user, board=board, role=BoardParticipant.Role.owner
        )
        return board


class BoardParticipantSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для внесения данных о доступе пользователей к доскам
    """
    role = serializers.ChoiceField(required=True, choices=BoardParticipant.Role.choices[1:])
    user = serializers.SlugRelatedField(slug_field="username", queryset=User.objects.all())

    class Meta:
        model = BoardParticipant
        fields = "__all__"
        read_only_fields = ("id", "created", "updated", "board")


class BoardSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для отображения данных доски
    """
    participants = BoardParticipantSerializer(many=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Board
        fields = "__all__"
        read_only_fields = ("id", "created", "updated")

    def update(self, instance: Board, validated_data: dict) -> Board:
        """
        Обновление списка пользователей, имеющих доступ к доске и их прав,
        изменение названия доски
        """
        with transaction.atomic():
            instance.participants.exclude(user=self.context["request"].user).delete()
            if 'participants' in validated_data.keys():
                for participant in validated_data["participants"]:
                    BoardParticipant.objects.create(
                        user_id=participant["user"].id,
                        role=participant["role"],
                        board_id=instance.pk
                    )

            if validated_data["title"]:
                instance.title = validated_data["title"]
                instance.save(update_fields=("title",))

        return instance


class BoardListSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для обновления списка досок
    """
    class Meta:
        model = Board
        fields = "__all__"
        read_only_fields = ("id", "created", "updated")
