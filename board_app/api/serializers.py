from rest_framework import serializers
from board_app.models import Board
from django.contrib.auth.models import User
from tasks_app.api.serializers import TaskBasicSerializer, UserBriefSerializer


class BoardSerializer(serializers.ModelSerializer):
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
        return obj.members.count()

    def get_ticket_count(self, obj):
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        return obj.tasks.filter(status="to-do").count()

    def get_tasks_high_prio_count(self, obj):
        return obj.tasks.filter(priority="high").count()

    def create(self, validated_data):
        members = validated_data.pop("members", [])
        board = super().create(validated_data)
        if members:
            board.members.set(members)
        return board

    def update(self, instance, validated_data):
        members = validated_data.pop("members", None)
        instance = super().update(instance, validated_data)
        if members is not None:
            instance.members.set(members)
        return instance



class SingleBoardSerializer(serializers.ModelSerializer):
    owner_id = serializers.IntegerField(source='owner.id', read_only=True)
    members = UserBriefSerializer(many=True, read_only=True)
    tasks = TaskBasicSerializer(many=True, read_only=True) 
    
    class Meta:
         model = Board
         fields = ['id', 'title', 'owner_id', 'members', 'tasks']



class BoardUpdateSerializer(serializers.ModelSerializer):
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

      def to_representation(self, instance):
           data = super().to_representation(instance)
           data.pop('members', None)
           return data
      
      

