from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Entity

# Register the User model with UserAdmin
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {
            'fields': ('entity', 'name', 'hashed_password'),
        }),
    )
    list_display = ('username', 'email', 'name', 'entity', 'is_admin', 'is_user')  # Fields to display in the user list
    search_fields = ('username', 'email', 'name')  # Fields to search by

# Register the Entity model
@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    list_display = ('name', 'entity_type', 'admin_user')  # Fields to display in the entity list
    search_fields = ('name', 'entity_type')  # Fields to search by