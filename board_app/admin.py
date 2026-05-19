"""Admin configuration for the ``Board`` model."""

from django.contrib import admin

from .models import Board


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    """Admin view for boards including a members counter."""

    list_display = ('id', 'title', 'owner', 'member_count')
    search_fields = (
        'title',
        'owner__username', 'owner__email',
        'members__username', 'members__email',
    )
    list_filter = ('owner',)
    ordering = ('-id',)
    filter_horizontal = ('members',)
    autocomplete_fields = ('owner',)

    @admin.display(description='Members')
    def member_count(self, obj):
        """Return the number of users assigned to the board."""
        return obj.members.count()
