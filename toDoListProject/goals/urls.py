from django.urls import path

from toDoListProject.goals import views

app_name = 'toDoListProject'
urlpatterns = [
    path("goal_category/create", views.GoalCategoryCreateView.as_view(), name="create_category"),
    path("goal_category/list", views.GoalCategoryListView.as_view(), name="category_list"),
    path("goal_category/<pk>", views.GoalCategoryView.as_view(), name="category"),
    path("goal/create", views.GoalCreateView.as_view(), name="create_goal"),
    path("goal/list", views.GoalListView.as_view(), name="goal_list"),
    path("goal/<pk>", views.GoalView.as_view(), name="goal"),
    path("goal_comment/create", views.GoalCommentCreateView.as_view(), name="create_comment"),
    path("goal_comment/list", views.GoalCommentListView.as_view(), name="comment_list"),
    path("goal_comment/<pk>", views.GoalCommentView.as_view(), name="comment"),
    path("board/create", views.BoardCreateView.as_view(), name="create_board"),
    path("board/list", views.BoardListView.as_view(), name="board_list"),
    path("board/<pk>", views.BoardView.as_view(), name="board"),

]

