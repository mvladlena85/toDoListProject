from django.db import transaction
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework import permissions, filters
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
    model = Board
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BoardCreateSerializer


class BoardView(RetrieveUpdateDestroyAPIView):
    model = Board
    permission_classes = [permissions.IsAuthenticated, BoardPermissions]
    serializer_class = BoardSerializer

    def get_queryset(self):
        # Обратите внимание на фильтрацию – она идет через participants
        return Board.objects.filter(participants__user=self.request.user, is_deleted=False)

    def perform_destroy(self, instance: Board):
        # При удалении доски помечаем ее как is_deleted,
        # «удаляем» категории, обновляем статус целей
        with transaction.atomic():
            instance.is_deleted = True
            instance.save()
            instance.categories.update(is_deleted=True)
            Goal.objects.filter(category__board=instance).update(
                status=Goal.Status.archived
            )
        return instance


class BoardListView(ListAPIView):
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
    model = GoalCategory
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCategoryCreateSerializer

    def create(self, request, *args, **kwargs):
        role = BoardParticipant.objects.get(board_id=request.data["board"], user_id=request.user.id).role
        if role == BoardParticipant.Role.reader:
            raise permissions.exceptions.PermissionDenied
        else:
            return super().create(self, request, *args, **kwargs)


class GoalCategoryListView(ListAPIView):
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
    model = GoalCategory
    serializer_class = GoalCategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return GoalCategory.objects.prefetch_related("board__participants").\
            filter(board__participants__user_id=self.request.user.id,
                   is_deleted=False)

    def update(self, request, *args, **kwargs):
        board_id = GoalCategory.objects.get(id=kwargs["pk"]).board_id
        role = BoardParticipant.objects.get(board_id=board_id, user_id=request.user.id).role
        if role == BoardParticipant.Role.reader:
            raise permissions.exceptions.PermissionDenied
        else:
            return super().update(self, request, *args, **kwargs)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()
        return instance


class GoalCreateView(CreateAPIView):
    model = Goal
    permission_classes = [GoalPermission]
    serializer_class = GoalCreateSerializer


class GoalListView(ListAPIView):
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
    model = Goal
    serializer_class = GoalSerializer
    permission_classes = [GoalPermission]

    def get_queryset(self):
        return Goal.objects.filter(
            ~Q(status=Goal.Status.archived)
            & Q(category__is_deleted=False)
        )

    def perform_destroy(self, instance):
        instance.is_archived = True
        instance.save()
        return instance


class GoalCommentCreateView(CreateAPIView):
    model = GoalComment
    permission_classes = [CommentCreatePermission]
    serializer_class = GoalCommentCreateSerializer


class GoalCommentListView(ListAPIView):
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
    model = GoalComment
    serializer_class = GoalCommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return GoalComment.objects.filter(user=self.request.user)
