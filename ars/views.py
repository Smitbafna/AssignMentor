from django.shortcuts import render

# Create your views here.from django.contrib.auth.models import Group, User
from rest_framework import permissions, viewsets
from rest_framework import status  # Import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Assignment, AssignmentSubtask, Submission, Attachment, Feedback
from .serializers import  AssignmentSerializer,  AssignmentSubtaskSerializer,SubmissionSerializer,AttachmentSerializer,FeedbackSerializer
from .models import CustomUser, ConnectionDetails, Organization, OrgMember, Team
from .serializers import (
    CustomUserSerializer,
    ConnectionDetailsSerializer,
    OrganizationSerializer,
    OrgMemberSerializer,
    TeamSerializer,
)
import requests
from django.conf import settings
from django.shortcuts import redirect
from django.http import HttpResponse
from django.contrib.auth import login
from .models import CustomUser


# ViewSet for AssignmentSubtask with ordering by 'subtask_end_date'
class AssignmentSubtaskViewSet(viewsets.ModelViewSet):
    queryset = AssignmentSubtask.objects.all().order_by('subtask_end_date')  # Order by subtask_end_date
    serializer_class = AssignmentSubtaskSerializer
    permission_classes = [permissions.IsAuthenticated]

# ViewSet for Submission with ordering by 'submitted_at'
class SubmissionViewSet(viewsets.ModelViewSet):
    queryset = Submission.objects.all().order_by('-submitted_at')  # Order by submitted_at in descending order
    serializer_class = SubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

# ViewSet for Attachment with ordering by 'date_of_submission'
class AttachmentViewSet(viewsets.ModelViewSet):
    queryset = Attachment.objects.all().order_by('-date_of_submission')  # Order by date_of_submission descending
    serializer_class = AttachmentSerializer
    permission_classes = [permissions.IsAuthenticated]

# ViewSet for Feedback with ordering by 'feedback_id'
class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all().order_by('feedback_id')  # Order by feedback_id in ascending order
    serializer_class = FeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]

 
# ViewSet for CustomUser with ordering by username
class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all().order_by('username')  # Order by username
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated]  # Only authenticated users can access this API

# ViewSet for ConnectionDetails with ordering by login_start
class ConnectionDetailsViewSet(viewsets.ModelViewSet):
    queryset = ConnectionDetails.objects.all().order_by('-login_start')  # Order by login_start descending
    serializer_class = ConnectionDetailsSerializer
    permission_classes = [permissions.IsAuthenticated]

# ViewSet for Organization with ordering by org_name
class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.all().order_by('org_name')  # Order by org_name
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated]

# ViewSet for OrgMember with ordering by member_id
class OrgMemberViewSet(viewsets.ModelViewSet):
    queryset = OrgMember.objects.all().order_by('member_id')  # Order by member_id
    serializer_class = OrgMemberSerializer
    permission_classes = [permissions.IsAuthenticated]

# ViewSet for Team with ordering by team_name
class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all().order_by('team_name')  # Order by team_name
    serializer_class = TeamSerializer
    permission_classes = [permissions.IsAuthenticated]


