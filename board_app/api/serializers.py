"""Serializers for board listing, detail, and updates."""

from rest_framework import serializers
from board_app.models import Board
from django.contrib.auth.models import User
from django.db import DatabaseError
from tasks_app.api.serializers import TaskBasicSerializer, UserBriefSerializer


class BoardSerializer(serializers.ModelSerializer):
    """Serializer for board list/create with aggregate counters."""

    members = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        required=False,
        write_only=True
    )
    owner_id = serializers.IntegerField(source="owner.id", read_only=True)

    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = [
            "id", "title", "members", "member_count",
            "ticket_count", "tasks_to_do_count",
            "tasks_high_prio_count", "owner_id"
        ]
        read_only_fields = [
            "owner_id", "member_count", "ticket_count",
            "tasks_to_do_count", "tasks_high_prio_count"
        ]

    def get_member_count(self, obj):
        """Return number of assigned board members."""
        members = getattr(obj, "members", None)
        return self._safe_count(members)

    def get_ticket_count(self, obj):
        """Return number of tasks on the board."""
        tasks = getattr(obj, "tasks", None)
        return self._safe_count(tasks)

    def get_tasks_to_do_count(self, obj):
        """Return number of tasks in ``to-do`` status."""
        tasks = getattr(obj, "tasks", None)
        return self._safe_count(tasks, status="to-do")

    def get_tasks_high_prio_count(self, obj):
        """Return number of high-priority tasks."""
        tasks = getattr(obj, "tasks", None)
        return self._safe_count(tasks, priority="high")

    def _safe_count(self, manager, **filters):
        """Safely count related objects and fallback to 0 on DB relation errors."""
        if manager is None:
            return 0
        try:
            queryset = manager.all()
            if filters:
                queryset = queryset.filter(**filters)
            return queryset.count()
        except (AttributeError, DatabaseError):
            return 0

    def create(self, validated_data):
        """Create board and assign optional initial members."""
        members = validated_data.pop("members", [])
        board = super().create(validated_data)
        if members:
            board.members.set(members)
        return board

    def update(self, instance, validated_data):
        """Update board fields and member assignment atomically."""
        members = validated_data.pop("members", None)
        instance = super().update(instance, validated_data)
        if members is not None:
            instance.members.set(members)
        return instance



class SingleBoardSerializer(serializers.ModelSerializer):
    """Detailed board serializer including nested members and tasks."""

    owner_id = serializers.IntegerField(source='owner.id', read_only=True)
    members = UserBriefSerializer(many=True, read_only=True)
    tasks = serializers.SerializerMethodField()
    
    class Meta:
         model = Board
         fields = ['id', 'title', 'owner_id', 'members', 'tasks']

    def get_tasks(self, obj):
        """Safely serialize board tasks and return an empty list on relation errors."""
        tasks = getattr(obj, "tasks", None)
        if tasks is None:
            return []
        try:
            return TaskBasicSerializer(tasks.all(), many=True).data
        except (AttributeError, DatabaseError):
            return []



class BoardUpdateSerializer(serializers.ModelSerializer):
    """Serializer for partial board updates with enriched read data."""

    ALLOWED_UPDATE_FIELDS = {"title", "members"}

    owner_data = UserBriefSerializer(source='owner', read_only=True)
    members_data = UserBriefSerializer(source='members', many=True, read_only=True)
    members = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        required=False,
    )

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_data', 'members_data', 'members']
        extra_kwargs = {'members': {'write_only': True}}

    def validate(self, attrs):
        """Reject unknown payload fields so board updates stay explicit."""
        unknown_fields = set(self.initial_data.keys()) - self.ALLOWED_UPDATE_FIELDS
        if unknown_fields:
            raise serializers.ValidationError({
                field: ["This field is not allowed for board updates."]
                for field in sorted(unknown_fields)
            })
        return attrs

    def validate_members(self, members):
        """Ensure member IDs are unique in update payload."""
        member_ids = [member.id for member in members]
        if len(member_ids) != len(set(member_ids)):
            raise serializers.ValidationError("Duplicate members are not allowed.")
        return members

    def to_representation(self, instance):
        """Hide write-only member IDs in response payload."""
        data = super().to_representation(instance)
        data.pop('members', None)
        return data
      
      

