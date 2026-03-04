"""Serializers for tasks, task comments, and compact user payloads."""

from rest_framework import serializers
from tasks_app.models import Task, TaskComment
from django.contrib.auth.models import User

class UserBriefSerializer(serializers.ModelSerializer):
    """Lightweight user representation used in nested task responses."""

    fullname = serializers.CharField(source='username')

    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']



class TaskSerializer(serializers.ModelSerializer):
    """Full task serializer with nested users and membership validation."""

    assignee = UserBriefSerializer(read_only=True)
    reviewer = UserBriefSerializer(read_only=True)

    assignee_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='assignee', write_only=True, required=False)
    reviewer_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='reviewer', write_only=True, required=False)
    
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'board', 'title', 'description', 'status', 'priority', 
            'assignee', 'assignee_id', 'reviewer', 'reviewer_id',
            'due_date', 'comments_count'
        ]
    
    def get_comments_count(self, obj):
        """Return live comment count from related comments."""
        return obj.comments.count()

    def to_representation(self, instance):
        """Remove write-only helper fields from output payload."""
        data = super().to_representation(instance)
        for field in ['assignee_id', 'reviewer_id']:
            data.pop(field, None)
        return data

    def validate(self, data):
        """Validate board membership and block board reassignment."""
        board = self._get_board(data)
        self._validate_user_membership(data.get('assignee'), board, "Assignee")
        self._validate_user_membership(data.get('reviewer'), board, "Reviewer")
        self._prevent_board_change(data)
        return data
    
    def _get_board(self, data):
        """Resolve board from payload or existing instance."""
        return data.get('board') or getattr(self.instance, 'board', None)
    
    def _validate_user_membership(self, user, board, role):
        """Ensure assignee/reviewer belongs to the task board."""
        if user and user not in board.members.all():
            raise serializers.ValidationError(f"{role} must be a member of the board.")
        
    def _prevent_board_change(self, data):
        """Disallow moving existing tasks to a different board."""
        if self.instance and 'board' in data and data['board'] != self.instance.board:
            raise serializers.ValidationError("Changing the board of a task is not allowed")



class TaskBasicSerializer(TaskSerializer):
    """Task serializer variant without ``board`` field for nesting."""

    class Meta(TaskSerializer.Meta):
        fields = [field for field in TaskSerializer.Meta.fields if field != 'board']



class TaskCommentSerializer(serializers.ModelSerializer):
    """Serializer for creating and listing task comments."""

    author = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = TaskComment
        fields = ['id', 'created_at', 'author', 'content']
        read_only_fields = ['id', 'created_at', 'author']

    def get_author(self, obj):
        """Return display name fallback chain for comment author."""
        return f"{obj.author.first_name} {obj.author.last_name}".strip() or obj.author.username
    

