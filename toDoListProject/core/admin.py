from django.contrib import admin

# Register your models here.

from toDoListProject.core.models import User


class CustomUserAdmin(admin.ModelAdmin):
    fields = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'is_superuser',
              'last_login', 'date_joined')
    exclude = ('password',)
    list_display = ("username", "email", "first_name", "last_name")
    list_filter = ("is_staff", "is_superuser", "is_active")
    readonly_fields = ('last_login', 'date_joined')
    search_fields = ("username", "email", "first_name", "last_name")


admin.site.register(User, CustomUserAdmin)
