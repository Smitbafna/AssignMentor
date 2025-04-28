import rest_framework
from .models import Assignment, AssignmentSubtask, Submission, Attachment, Feedback
from rest_framework import serializers
from .models import CustomUser, ConnectionDetails, Organization, OrgMember, Team
from rest_framework import serializers

class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = '__all__'  # Include all fields except is_assign_creator_FK

class AssignmentSubtaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentSubtask
        fields = '__all__'  # Serialize all fields


class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = '__all__'  # Serialize all fields


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = '__all__'  # Serialize all fields


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'  # Serialize all fields



class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'  # Serialize all fields


class ConnectionDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConnectionDetails
        fields = '__all__'  # Serialize all fields


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'  # Serialize all fields


class OrgMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrgMember
        fields = '__all__'  # Serialize all fields


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'  # Serialize all fields

