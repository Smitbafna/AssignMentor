from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.validators import MinLengthValidator, MaxLengthValidator, EmailValidator, RegexValidator

class CustomUser(AbstractUser):
    enr_no = models.IntegerField(
        validators=[MinLengthValidator(8), MaxLengthValidator(8)],
        help_text="This field requires exactly 8 digits."
    )
    username = models.CharField(
        max_length=255,
        help_text="This field requires less than 255 characters.",
        unique=False 
    )
    password = models.CharField(
        max_length=255,
        help_text="This field requires less than 255 characters."
    )
    email = models.EmailField(
        max_length=320,
        unique=True,
        validators=[
            EmailValidator(),
            RegexValidator(
                regex=r'^[\w\.-]+@iitr\.ac\.in$',
                message="Email must be from @iitr.ac.in domain."
            )
        ],
        help_text="This field requires less than 320 characters."
    )
    Whatsapp_no = models.IntegerField(
        validators=[MinLengthValidator(10), MaxLengthValidator(10)],
        help_text="This field requires exactly 10 digits."
    )
    profile_pic = models.FileField(
        upload_to='documents/profile_pics/',
    )

    # Gender choices
    MALE = "M"
    FEMALE = "F"
    OTHERS = "O"
    
    GENDER_CHOICES = [
        (MALE, "Male"),
        (FEMALE, "Female"),
        (OTHERS, "Others"),
    ]

    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES
    )
    dob = models.DateField(blank=False)

    # Placeholder for Branch Choices - add actual branches
    BRANCH_CHOICES = []

    branch = models.CharField(
        max_length=3,
        choices=BRANCH_CHOICES
    )

    # Override the default related names for groups and user_permissions
    groups = models.ManyToManyField(Group, related_name='customuser_set', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='customuser_set', blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # Ensure that 'username' is still part of required fields

    def __str__(self):
        return f"{self.email} ({self.enr_no})"


class Assignment(models.Model):
    assignment_id = models.AutoField(primary_key=True)
    is_assign_creator_FK = models.ForeignKey(
        'ars.OrgMember', 
        on_delete=models.CASCADE,
        related_name="assignments_created_by_member"
    )
    assignment_name = models.CharField(
        max_length=255
    )
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField()
    assignment_description = models.TextField()
    assigned_teams_FK = models.ManyToManyField('ars.Team')
    assign_reviewer_FK = models.ManyToManyField(
        'ars.OrgMember', 
        blank=True,
        related_name="assignments_reviewed_by_member"
    )

    def __str__(self):
        return self.assignment_name

class AssignmentSubtask(models.Model):
    subtask_id = models.AutoField(primary_key=True)
    ass_to_subtask_FK = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    description = models.TextField()
    subtask_end_date = models.DateField()
    assign_subtask_status_FK = models.OneToOneField('Submission', on_delete=models.CASCADE)
    subtask_status = models.BooleanField(default=False)
    assign_subtask_reviewer_FK = models.ManyToManyField(CustomUser)

    def __str__(self):
        return f"Subtask {self.subtask_id} of Assignment {self.ass_to_subtask_FK.assignment_name}"

class Submission(models.Model):
    submission_id = models.AutoField(primary_key=True)
    subtask_id_FK = models.ForeignKey(AssignmentSubtask, on_delete=models.CASCADE)
    isCompleted = models.BooleanField(default=False)
    reviewer_id_FK = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    team_leader_id_FK = models.ForeignKey('ars.Team', on_delete=models.CASCADE)
    
    submitted_at = models.DateTimeField(auto_now_add=True)

    SUBMITTED = "S"
    UNDER_REVIEW = "UR"
    COMPLETED = "C"
    REJECTED = "R"

    submission_status_choices = [
        (SUBMITTED, "Submitted"),
        (UNDER_REVIEW, "Under Review"),
        (COMPLETED, "Completed"),
        (REJECTED, "Rejected")
    ]
        
    submission_status = models.CharField(
        max_length=25,
        choices=submission_status_choices
    )

    def __str__(self):
        return f'Submission {self.submission_id} for Subtask {self.subtask_id_FK}'

class Attachment(models.Model):
    attachment_id = models.AutoField(primary_key=True)
    attachment_type = models.CharField(max_length=50, choices=[
        ('document', 'Document'),
        ('image', 'Image'),
        ('video', 'Video'),
        ('other', 'Other')
    ])
    attachment_name = models.CharField(max_length=255)
    iteration = models.PositiveIntegerField(default=1, editable=False)
    date_of_submission = models.DateField(auto_now_add=True)
    submission_id_FK = models.ForeignKey(Submission, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        # Automatically set the iteration number based on the number of previous attachments for the same submission
        if not self.pk:  # Check if it's a new attachment (not yet saved to the database)
            previous_attachments = Attachment.objects.filter(submission_id_FK=self.submission_id_FK).count()
            self.iteration = previous_attachments + 1  # Set iteration based on existing attachments
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.attachment_name} ({self.attachment_type})'

class Feedback(models.Model):
    feedback_id = models.AutoField(primary_key=True)
    attach_feed_FK = models.OneToOneField(Attachment, on_delete=models.CASCADE)
    feedback = models.TextField()

    def __str__(self):
        return f'Feedback for {self.attach_feed_FK.attachment_name}'

class ConnectionDetails(models.Model):
    connection_id = models.AutoField(primary_key=True)
    user_id = models.ManyToManyField(CustomUser)
    login_start = models.DateTimeField(auto_now_add=True)
    login_end = models.DateTimeField(null=True, blank=True)
    user_agent = models.CharField(max_length=255)
    connection_ip = models.GenericIPAddressField()
    device_name = models.CharField(max_length=255)
    device_id = models.CharField(max_length=255, unique=True)
    last_used = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Connection {self.connection_id} for user {self.user_id}'

class Organization(models.Model):
    org_id = models.AutoField(primary_key=True)
    org_name = models.CharField(max_length=255)
    admin = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.org_name

class OrgMember(models.Model):
    member_id = models.AutoField(primary_key=True)
    org_id_FK = models.ForeignKey(Organization, on_delete=models.CASCADE)
    user = models.ManyToManyField(CustomUser)
    is_admin = models.BooleanField(default=False)
    is_reviewer = models.BooleanField(default=False)
    is_reviewee = models.BooleanField(default=False)

    def __str__(self):
        # Join usernames from the user ManyToManyField
        usernames = ", ".join(user.username for user in self.user.all())
        return f"{usernames} - {self.org_id_FK.org_name}"

class Team(models.Model):
    team_id = models.AutoField(primary_key=True)
    team_name = models.CharField(max_length=255)
    team_members_FK = models.ManyToManyField(OrgMember, related_name="teams_with_member")
    team_leader_FK = models.ForeignKey(OrgMember, on_delete=models.CASCADE, related_name="teams_led_by_member")
    team_leader_submission_FK = models.ForeignKey(Submission, on_delete=models.CASCADE)

    def __str__(self):
        return self.team_name
