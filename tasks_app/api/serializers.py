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

    STATUS_CHOICES = ["to-do", "in-progress", "review", "done"]
    PRIORITY_CHOICES = ["low", "medium", "high"]
    ALLOWED_UPDATE_FIELDS = {
        "title",
        "description",
        "status",
        "priority",
        "assignee_id",
        "reviewer_id",
        "due_date",
    }

    status = serializers.ChoiceField(choices=STATUS_CHOICES)
    priority = serializers.ChoiceField(choices=PRIORITY_CHOICES)

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
        self._validate_update_fields()
        board = self._get_board(data)
        self._validate_board_presence(board)
        self._validate_user_membership(data.get('assignee'), board, "Assignee")
        self._validate_user_membership(data.get('reviewer'), board, "Reviewer")
        self._prevent_board_change(data)
        return data

    def _validate_update_fields(self):
        """Restrict task updates to explicitly supported writable fields."""
        if self.instance is None:
            return
        invalid_fields = set(self.initial_data.keys()) - self.ALLOWED_UPDATE_FIELDS
        if invalid_fields:
            raise serializers.ValidationError({
                field: ["This field is not allowed for task updates."]
                for field in sorted(invalid_fields)
            })
    
    def _get_board(self, data):
        """Resolve board from payload or existing instance."""
        return data.get('board') or getattr(self.instance, 'board', None)

    def _validate_board_presence(self, board):
        """Require a board relation when creating tasks."""
        if self.instance is None and board is None:
            raise serializers.ValidationError({'board': 'This field is required.'})
    
    def _validate_user_membership(self, user, board, role):
        """Ensure assignee/reviewer belongs to the board or owns it."""
        if not user or board is None:
            return
        is_owner = board.owner_id == user.id
        is_member = board.members.filter(id=user.id).exists()
        if not (is_owner or is_member):
            raise serializers.ValidationError(f"{role} must be a member or owner of the board.")
        
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
    

