from django.contrib import admin

from toDoListProject.goals.models import GoalCategory, Goal, GoalComment


@admin.register(GoalCategory)
class GoalCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "user", "created", "updated")
    search_fields = ("title", "user")


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "user", "description", "category", "status", "priority", "due_date", "created", "updated")
    search_fields = ["title", "description"]
    list_filter = ("status", "priority",)
    list_display_links = ("title", "user",)


@admin.register(GoalComment)
class GoalCommentAdmin(admin.ModelAdmin):
    list_display = ("id", "text", "goal", "user", "created", "updated")
    search_fields = ["text"]
    list_display_links = ("text", "goal",)
