from django.contrib import admin
from .models import Task, TaskComment


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
	list_display = (
		'id',
		'title',
		'board',
		'status',
		'priority',
		'assignee',
		'reviewer',
		'due_date',
		'comments_count',
	)
	search_fields = (
		'title',
		'description',
		'board__title',
		'assignee__username',
		'assignee__email',
		'reviewer__username',
		'reviewer__email',
	)
	list_filter = ('status', 'priority', 'due_date', 'board')
	ordering = ('due_date', '-id')
	list_select_related = ('board', 'assignee', 'reviewer')
	autocomplete_fields = ('board', 'assignee', 'reviewer')
	date_hierarchy = 'due_date'


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
	list_display = ('id', 'task', 'author', 'created_at', 'short_content')
	search_fields = ('content', 'author__username', 'author__email', 'task__title')
	list_filter = ('created_at',)
	ordering = ('-created_at',)
	list_select_related = ('task', 'author')
	autocomplete_fields = ('task', 'author')

	@admin.display(description='Content')
	def short_content(self, obj):
		return obj.content[:60]
