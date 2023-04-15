from django.db import transaction
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework import permissions, filters, status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from toDoListProject.goals.filters import GoalDateFilter
from toDoListProject.goals.models import GoalCategory, Goal, GoalComment, Board, BoardParticipant
from toDoListProject.goals.permissions import BoardPermissions, GoalPermission, IsOwnerOrReadOnly, \
    CommentCreatePermission
from toDoListProject.goals.serializers import GoalCreateSerializer, GoalCategorySerializer, \
    GoalCategoryCreateSerializer, GoalSerializer, GoalCommentCreateSerializer, GoalCommentSerializer, \
    BoardCreateSerializer, BoardSerializer, BoardListSerializer


class BoardCreateView(CreateAPIView):
    """
    View Для создания доски
    """
    model = Board
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BoardCreateSerializer


class BoardView(RetrieveUpdateDestroyAPIView):
    """
    View для отображения, изменения и удаления конкретной доски
    """
    model = Board
    permission_classes = [permissions.IsAuthenticated, BoardPermissions]
    serializer_class = BoardSerializer

    def get_queryset(self):
        return Board.objects.filter(is_deleted=False)

    def perform_destroy(self, instance: Board):
        # При удалении доски помечаем ее как is_deleted,
        # «удаляем» категории, помечая их как is_deleted, обновляем статус целей
        with transaction.atomic():
            instance.is_deleted = True
            instance.save()
            instance.categories.update(is_deleted=True)
            Goal.objects.filter(category__board=instance).update(
                status=Goal.Status.archived
            )
        return instance


class BoardListView(ListAPIView):
    """
    View для получения списка досок, доступных пользователю
    """
    model = Board
    permission_classes = [permissions.IsAuthenticated, BoardPermissions]
    serializer_class = BoardListSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [filters.OrderingFilter, ]
    ordering_fields = ["title", "created"]
    ordering = ["title"]

    def get_queryset(self):
        return Board.objects.prefetch_related("participants").filter(participants__user_id=self.request.user.pk,
                                                                     is_deleted=False)


class GoalCategoryCreateView(CreateAPIView):
    """
    View для создания категории
    """
    model = GoalCategory
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCategoryCreateSerializer

    def create(self, request, *args, **kwargs) -> Response:
        """
        Функция для создания категории. Сначала проверяем роль пользователя для текущей доски,
        и если у пользователя есть права на изменение доски (роль admin или writer),
        то создаем категорию.
        """
        request = request
        role = BoardParticipant.objects.get(board_id=request.data["board"], user_id=request.user.id).role
        if role == BoardParticipant.Role.reader:
            raise permissions.exceptions.PermissionDenied
        else:
            return super().create(request, *args, **kwargs)


class GoalCategoryListView(ListAPIView):
    """
    View для получения списка категорий, доступных пользователю
    """
    model = GoalCategory
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCategorySerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    filterset_fields = ["board"]
    ordering_fields = ["title", "created"]
    ordering = ["title"]
    search_fields = ["title"]

    def get_queryset(self):
        return GoalCategory.objects.prefetch_related("board__participants").\
            filter(board__participants__user_id=self.request.user.id, is_deleted=False)


class GoalCategoryView(RetrieveUpdateDestroyAPIView):
    """
    View для получения, изменения и удаления конкретной категории
    """
    model = GoalCategory
    serializer_class = GoalCategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return GoalCategory.objects.prefetch_related("board__participants").\
            filter(board__participants__user_id=self.request.user.id,
                   is_deleted=False)

    def update(self, request, *args, **kwargs) -> Response:
        """
        Функция для изменения категории. Сначала проверяем,
        есть ли права у пользователя на изменение категории (роль writer/owner)
        """
        board_id = GoalCategory.objects.get(id=kwargs["pk"]).board_id
        role = BoardParticipant.objects.get(board_id=board_id, user_id=request.user.id).role
        if role == BoardParticipant.Role.reader:
            raise permissions.exceptions.PermissionDenied
        else:
            return super().update(request, *args, **kwargs)

    def perform_destroy(self, instance):
        """
        При "удалении" категории просто помечаем ее как is_deleted = True
        """
        instance.is_deleted = True
        instance.save()
        return instance


class GoalCreateView(CreateAPIView):
    """
    View для создания цели
    """
    model = Goal
    permission_classes = [GoalPermission]
    serializer_class = GoalCreateSerializer


class GoalListView(ListAPIView):
    """
    View для получения списка целей, доступных пользователю
    """
    model = Goal
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    filterset_class = GoalDateFilter
    ordering_fields = ["title", "created"]
    ordering = ["title", "created"]
    search_fields = ["title", "description"]

    def get_queryset(self):
        return Goal.objects.filter(
            Q(category__board__participants__user_id=self.request.user.id)
            & ~Q(status=Goal.Status.archived)
            & Q(category__is_deleted=False)
        )


class GoalView(RetrieveUpdateDestroyAPIView):
    """
    View для получения, изменения и удаления цели
    """
    model = Goal
    serializer_class = GoalSerializer
    permission_classes = [GoalPermission]

    def get_queryset(self):
        return Goal.objects.filter(
            ~Q(status=Goal.Status.archived)
            & Q(category__is_deleted=False)
        )

    def perform_destroy(self, instance: Goal):
        """
        При "удалении" цели выставляем статус "в архиве"
        """
        instance.status = Goal.Status.archived
        instance.save()
        return instance


class GoalCommentCreateView(CreateAPIView):
    """
    View для создания комментария
    """
    model = GoalComment
    permission_classes = [CommentCreatePermission]
    serializer_class = GoalCommentCreateSerializer


class GoalCommentListView(ListAPIView):
    """
    View для получения списка комментариев к цели
    """
    model = GoalComment
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    serializer_class = GoalCommentSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter
    ]
    filterset_fields = ["goal"]

    def get_queryset(self):
        return GoalComment.objects.filter(
            goal__category__board__participants__user_id=self.request.user.id,
        )


class GoalCommentView(RetrieveUpdateDestroyAPIView):
    """
    View для получения, изменения и удаления комментария
    """
    model = GoalComment
    serializer_class = GoalCommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return GoalComment.objects.filter(user=self.request.user)
