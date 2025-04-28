from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
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
from django.contrib.auth import authenticate, login as auth_login
from django.http import FileResponse, Http404
import os;
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from logging import getLogger
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from datetime import date 
from django.core.files.storage import default_storage

logger = getLogger('django')
@api_view(['GET'])
def getOrgsOfUser(request):
    email = request.headers.get('X-User-Email')
    if not email:
        return JsonResponse({'error': 'User email missing from request'}, status=400)

    try:
        user = get_object_or_404(CustomUser, email=email)
        org_memberships = OrgMember.objects.filter(user=user)

        organizations = []
        for org_member in org_memberships:
            organizations.append({
                'id': org_member.org_id_FK.org_id,
                'name': org_member.org_id_FK.org_name
            })

        print("Fetched organizations:", organizations)  # Debugging output

        return JsonResponse({'organizations': organizations})
    except CustomUser.DoesNotExist:
        logger.error(f"User with email {email} does not exist.")
        return JsonResponse({'error': 'User not found'}, status=404)


def index(request):
    return render(request, 'users/index.html')


@api_view(['GET'])
def profile_view(request):
    user = request.user
    if not user.is_authenticated:
        return Response({"error": "User is not authenticated."}, status=status.HTTP_401_UNAUTHORIZED)
    serializer = CustomUserSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)




from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import OrgMember, Assignment

@api_view(['POST'])
def create_assignment(request):
    # Extract email from query parameters
    email = request.query_params.get('email')
    
    if not email:
        return Response({'detail': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)

    # Fetch the user by email
    try:
        user = get_user_model().objects.get(email=email)
    except get_user_model().DoesNotExist:
        return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check if the user is a reviewer
    is_reviewer = OrgMember.objects.filter(user=user, is_reviewer=True).exists()
    
    # Log the status of is_reviewer for debugging
    logger.debug(f"is_reviewer for {email}: {is_reviewer}")

    if not is_reviewer:
        # If the user is not a reviewer, return a 401 Unauthorized response
        return Response({'detail': 'You are not a reviewer.'}, status=status.HTTP_401_UNAUTHORIZED)
    
    # Get the assignment details from the request data
    assignment_name = request.data.get('assignment_name')
    assignment_description = request.data.get('assignment_description')
    end_date = request.data.get('end_date')
    
    # Log the assignment details for debugging
    logger.debug(f"Incoming Data: {request.data}")
    
    if not all([assignment_name, assignment_description, end_date]):
        return Response({'detail': 'All assignment fields are required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Create the assignment
        assignment = Assignment.objects.create(
            assignment_name=assignment_name,
            assignment_description=assignment_description,
            end_date=end_date,
        )
        
        logger.debug(f"Assignment created successfully: {assignment}")

        # Return a success response
        return Response({'detail': 'Assignment created successfully.'}, status=status.HTTP_201_CREATED)

    except Exception as e:
        # Log the exception to understand the error better
        logger.error(f"Error creating assignment: {str(e)}")
        return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['GET'])
def get_assignments_name(request, role):
    # Fetch assignments based on the role (viewee or viewer)
    assignments = Assignment.objects.all()  # Filter based on role if needed
    assignment_list = []

    for assignment in assignments:
        assignment_list.append({
            'id': assignment.assignment_id,
            'assignment_name': assignment.assignment_name,
        })

    return Response({
        "assignments": assignment_list
    })





@api_view(['GET'])
def get_assignments_by_role(request, role):
    # Fetch assignments based on the role (viewee or viewer)
    assignments = Assignment.objects.all()  # Filter based on role if needed
    assignment_list = []

    for assignment in assignments:
        assignment_list.append({
            'id': assignment.assignment_id,
            'assignment_name': assignment.assignment_name,
            'assignment_description': assignment.assignment_description,
            'end_date': assignment.end_date,
        })

    return Response({
        "assignments": assignment_list
    })


@api_view(['GET'])
def get_reviewees(request):
    try:
        
        logger.info("Received GET request for reviewees.")
        
        
        reviewees = OrgMember.objects.filter(is_reviewee=True)
        
        if not reviewees.exists():
            logger.warning("No reviewees found with is_reviewee=True.")
            return Response({"message": "No reviewees found."}, status=status.HTTP_404_NOT_FOUND)
        
        reviewee_list = []

   
        for reviewee in reviewees:
        
            for user in reviewee.user.all():
                reviewee_list.append({
                    'id': user.id,  
                    'name': user.username,  
                    'email': user.email,
                    'is_reviewee': reviewee.is_reviewee,
                })

        logger.info(f"Found {len(reviewee_list)} reviewees.")
        
     
        return Response({
            "reviewees": reviewee_list
        })

    except Exception as e:
     
        logger.error(f"Error occurred while fetching reviewees: {str(e)}")
        
    
        return Response({"message": "An error occurred while fetching reviewees."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_reviewers(request):
    try:
  
        logger.info("Received GET request for reviewers.")
    
        reviewers = OrgMember.objects.filter(is_reviewer=True)
        
        if not reviewers.exists():
            logger.warning("No reviewers found with is_reviewer=True.")
            return Response({"message": "No reviewers found."}, status=status.HTTP_404_NOT_FOUND)
        
        reviewer_list = []


        for reviewer in reviewers:
      
            for user in reviewer.user.all():
                reviewer_list.append({
                    'id': user.id,  
                    'name': user.username,  
                    'email': user.email,
                    'is_reviewer': reviewer.is_reviewer,
                })

        logger.info(f"Found {len(reviewer_list)} reviewers.")
        
      
        return Response({
            "reviewers": reviewer_list
        })

    except Exception as e:
      
        logger.error(f"Error occurred while fetching reviewers: {str(e)}")
        

        return Response({"message": "An error occurred while fetching reviewers."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)








@csrf_exempt  
@api_view(['POST'])
def delete_assignment(request):
    
    email = request.query_params.get('email')
    
   
    logger.debug(f"Incoming request data: {request.data}")
    logger.debug(f"Query parameters: {request.query_params}")

    if not email:
        logger.debug("Email is missing in request.")
        return Response({'detail': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)

   
    try:
        user = get_user_model().objects.get(email=email)
    except get_user_model().DoesNotExist:
        logger.debug(f"User with email {email} not found.")
        return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
    

    is_reviewer = OrgMember.objects.filter(user=user, is_reviewer=True).exists()
    
    
    logger.debug(f"is_reviewer for {email}: {is_reviewer}")

    if not is_reviewer:
        
        logger.debug(f"User {email} is not a reviewer. Denying access.")
        return Response({'detail': 'You are not a reviewer.'}, status=status.HTTP_401_UNAUTHORIZED)
    
    
    assignment_id = request.data.get('assignment_id')
    assignment_name = request.data.get('assignment_name')


    logger.debug(f"Received assignment_id: {assignment_id}, assignment_name: {assignment_name}")

    if not assignment_id or not assignment_name:
  
        if not assignment_id:
            logger.debug("Missing assignment_id in request data.")
        if not assignment_name:
            logger.debug("Missing assignment_name in request data.")
        
        return Response({'error': 'Both assignment_id and assignment_name are required'}, 
                         status=status.HTTP_400_BAD_REQUEST)

    try:
        
        assignment = Assignment.objects.get(assignment_id=assignment_id, assignment_name=assignment_name)

        logger.debug(f"Assignment found: {assignment}")

   
        assignment.delete()

        logger.debug(f"Assignment {assignment_name} deleted successfully.")
        return Response({'message': 'Assignment deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

    except Assignment.DoesNotExist:
        logger.debug(f"Assignment with id {assignment_id} and name {assignment_name} not found.")
        return Response({'error': 'Assignment not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:

        logger.error(f"Error deleting assignment: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
def update_assignment(request, pk):
    try:
        assignment = Assignment.objects.get(pk=pk)
    except Assignment.DoesNotExist:
        return Response({'detail': 'Assignment not found'}, status=status.HTTP_404_NOT_FOUND)
    
   
    serializer = AssignmentSerializer(assignment, data=request.data, partial=False)  # `partial=False` ensures all fields are required
    
    if serializer.is_valid():
    
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def submit_comment(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            reviewee_id = data['reviewee_id']
            assignment_id = data['assignment_id']
            comment_text = data['comment']

            # Fetch the reviewee and assignment
            reviewee = Reviewee.objects.get(id=reviewee_id)
            assignment = Assignment.objects.get(id=assignment_id)

            # Create the comment
            Comment.objects.create(
                reviewee=reviewee,
                assignment=assignment,
                text=comment_text,
            )

            return JsonResponse({'success': True})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid method'})

@csrf_exempt  # If you are bypassing CSRF for testing or specific cases
  # Make sure the user is logged in to submit the form
def submit_form(request):
    if request.method == 'POST':
        # Get data from the frontend
        selected_reviewee = request.POST.get('reviewee')
        selected_assignment = request.POST.get('assignment')
        comment = request.POST.get('comment', '')

        if not selected_reviewee or not selected_assignment:
            return JsonResponse({'error': 'Please select both reviewee and assignment.'}, status=400)

        # Process or save the data
        try:
            reviewee = OrgMember.objects.get(id=selected_reviewee)
            assignment = Assignment.objects.get(id=selected_assignment)

            # Add any further logic for saving the submission here

            return JsonResponse({'success': 'Form submitted successfully!'}, status=200)
        except OrgMember.DoesNotExist:
            return JsonResponse({'error': 'Reviewee not found.'}, status=404)
        except Assignment.DoesNotExist:
            return JsonResponse({'error': 'Assignment not found.'}, status=404)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)

@api_view(['GET'])
def get_submission_for_reviewee(request):

    uploads_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
    
 
    try:
        files = [f for f in os.listdir(uploads_dir) if os.path.isfile(os.path.join(uploads_dir, f))]
        if not files:
            return Response({'error': 'No files found in the uploads directory'}, status=404)

        # Sort files alphabetically
        files.sort()

        # Pick a random file
        random_file = random.choice(files)
        
        # Get the submission related to the chosen file
        submission = Submission.objects.filter(file_path=f'uploads/{random_file}').first()

        if not submission:
            return Response({'error': 'No submission found for the selected file'}, status=404)

        return Response({
            'file_path': submission.file_path,
            'submission_id': submission.id,
        })
    
    except Exception as e:
        return Response({'error': str(e)}, status=500)
@api_view(['POST'])
def upload_file(request):
    try:
        # Retrieve data from the request
        reviewer_id = request.data.get('reviewer_id')  # CustomUser ID (selectedReviewer from frontend)
        uploaded_file = request.FILES.get('file')
        team_leader = request.user.team if hasattr(request.user, 'team') else None  # Use the current logged-in user's team leader or None

        # If subtask is provided, use it, otherwise, it's optional.
        assignment_subtask_id = request.data.get('subtask_id')  # Optional

        # Validate required fields
        if not reviewer_id or not uploaded_file:
            return Response(
                {"error": "Reviewer and file are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Fetch the relevant objects
        reviewer_user = get_object_or_404(CustomUser, id=reviewer_id)
        assignment_subtask = None
        if assignment_subtask_id:
            assignment_subtask = get_object_or_404(AssignmentSubtask, id=assignment_subtask_id)

        # Save the file in the media/uploads directory
        file_path = default_storage.save(f'uploads/{uploaded_file.name}', uploaded_file)

        # Create a new Submission record
        submission = Submission.objects.create(
            subtask_id_FK=assignment_subtask,  # Can be None (nullable)
            reviewer_id_FK=reviewer_user,
            team_leader_id_FK=team_leader,  # May be None (nullable)
            submission_status=Submission.SUBMITTED,  # Set the initial status
        )

        # Return the response with the file path and submission details
        return Response(
            {
                "message": "File uploaded successfully.",
                "file_path": f"{settings.MEDIA_URL}{file_path}",
                "submission_id": submission.submission_id,
                "reviewer_id": reviewer_id,
                "team_leader_id": team_leader.id if team_leader else None,
            },
            status=status.HTTP_201_CREATED,
        )

    except Exception as e:
        return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(['POST'])
def submit_assignment(request):
    # Validate required fields in request data
    subtask_id = request.data.get('subtask_id_FK')
    team_leader_id = request.data.get('team_leader_id_FK')
    reviewer_id = request.data.get('reviewer_id_FK')
    submission_status = request.data.get('submission_status', 'S')  # Default to 'S' for Submitted

    # Check if all required fields are provided
    if not all([subtask_id, team_leader_id, reviewer_id]):
        return Response({'detail': 'All fields are required.'}, status=status.HTTP_400_BAD_REQUEST)

    # Create a new Submission
    try:
        submission = Submission.objects.create(
            subtask_id=subtask_id,
            team_leader_id=team_leader_id,
            reviewer_id=reviewer_id,
            submission_status=submission_status,
        )

        # Serialize the created Submission object
        serializer = SubmissionSerializer(submission)

        # Return the serialized data
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

@csrf_exempt
def login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not email or not password:
            return JsonResponse({"success": False, "message": "Email and password are required."}, status=400)

        # Check if user exists based on the email first (for debugging)
        try:
            user = CustomUser.objects.get(email=email)
            logger.debug(f"User found: {user.email}")  # Log user information (be careful with sensitive data)
        except CustomUser.DoesNotExist:
            logger.warning(f"No user found with email: {email}")
            return JsonResponse({"success": False, "message": "Invalid email or password."}, status=401)

        # Authenticate the user
        user = authenticate(request, email=email, password=password)

        if user:
            # Successful authentication
            logger.debug(f"User {user.email} authenticated successfully.")
            auth_login(request, user)

            # Generate tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            response = JsonResponse({
                "success": True,
                "message": "Authentication successful.",
                "access": access_token,
            })

            # Set secure refresh token in the cookie
            response.set_cookie(
                key="refresh_token",
                value=str(refresh),
                httponly=True,
                secure=True,
                samesite="Strict",
                max_age=7 * 24 * 60 * 60  # 7 days
            )
            return response
        else:
            logger.warning(f"Invalid credentials for user with email: {email}")
            return JsonResponse({"success": False, "message": "Invalid email or password."}, status=401)

    return JsonResponse({"success": False, "message": "Method not allowed."}, status=405)

def loginoauth(request):
    # Path to the React app's index.html
    react_app_path = os.path.join(settings.BASE_DIR, 'frontend', 'oauth', 'dist', 'index.html')
    
    try:
        return FileResponse(open(react_app_path, 'rb'))
    except FileNotFoundError:
        raise Http404("React app not found.")




@login_required
def Orgselect(request):
    organization = Organization.objects.all()
    context = {
        'organization': organization
    }
    return render(request,'users/Orgselect.html',context)


def dashboard_view(request):
    user_roles = {}
    if request.user.is_authenticated:
        # Get the roles for the current user
        try:
            member = OrgMember.objects.get(user=request.user)
            user_roles = {
                'is_reviewee': member.is_reviewee,
                'is_reviewer': member.is_reviewer
            }
        except OrgMember.DoesNotExist:
            user_roles = {
                'is_reviewee': False,
                'is_reviewer': False
            }
    return render(request, 'dashboard.html', {'user_roles': user_roles})












































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





