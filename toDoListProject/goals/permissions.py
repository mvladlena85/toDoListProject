from rest_framework import permissions

from toDoListProject.goals.models import BoardParticipant, Goal, GoalComment


class BoardPermissions(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return BoardParticipant.objects.filter(
                user=request.user, board=obj
            ).exists()
        return BoardParticipant.objects.filter(
            user=request.user, board=obj, role=BoardParticipant.Role.owner
        ).exists()


class GoalPermission(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj: Goal):
        if request.method in permissions.SAFE_METHODS:
            return BoardParticipant.objects.filter(
                user_id=request.user.id, board_id=obj.category.board_id
            ).exists()
        return BoardParticipant.objects.filter(
            user_id=request.user.id, board_id=obj.category.board_id,
            role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer]
        ).exists()


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj: GoalComment):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user_id == request.user.id


class CommentCreatePermission(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        return BoardParticipant.objects.filter(
                user_id=request.user.id, board_id=Goal.objects.get(id=request.data["goal"]).category.board_id,
                role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer]
            ).exists()
