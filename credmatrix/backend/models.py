from django.db import models
from django.contrib.auth.models import AbstractUser
from enum import Enum
from django.utils.timezone import now
from datetime import timedelta

class EntityType(Enum):
    INDIVIDUAL = 0
    BANK = 1
    NBFC = 2
    CORPORATE = 3
    STARTUP = 4
    CONSULTANT = 5
    OTHER = 6

class ReportStatus(Enum):
    COMPLETED = 0
    REQUEST_RAISED = 1
    UNDER_ASSESMENT = 2
    DOC_PENDING = 3
    DRAFT = 4
    CANCELLED = 5

class ServiceType(Enum):
    FINANCIAL_INFO = 0
    COMPREHENSIVE_REPORT_WITH_SCORES = 1
    BUREAU_REPORT = 2
    BANK_REF_CHECK = 3

class Entity(models.Model):
    ENTITY_TYPE_CHOICES = [(etype.name, etype.name) for etype in EntityType]
    name = models.CharField(max_length=255)
    entity_type = models.CharField(
        max_length=20,
        choices=ENTITY_TYPE_CHOICES,
        default=EntityType.INDIVIDUAL.name
    )
    admin_user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='admin_of_entities')

    def __str__(self):
        return f"{self.name} ({self.entity_type})"

class User(AbstractUser):
    entity = models.ForeignKey(Entity, on_delete=models.SET_NULL, null=True, related_name='users')
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.email

    def is_admin(self):
        return self.groups.filter(name='admin').exists()

    def is_user(self):
        return self.groups.filter(name='user').exists()

class OTP(models.Model):
    email = models.EmailField(unique=True)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return now() < self.created_at + timedelta(minutes=5)


class Report(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    agent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_reports')
    status = models.CharField(
        max_length=20,
        default=ReportStatus.DRAFT.name,
        choices=[(status.name, status.name) for status in ReportStatus]
    )
    services = models.JSONField(default=list)  # Changed to JSONField to store a list of services
    created_at = models.DateTimeField(auto_now_add=True)
    target_entity_name = models.CharField(max_length=255)
    target_entity_pan = models.CharField(max_length=20)
    credits = models.IntegerField(default=0)
    pending_documents = models.JSONField(default=list)
    cancellation_reason = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Report by {self.user.email} - Status: {self.status}"

class Document(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='documents', db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    s3_path = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Document for Report ID {self.report.id} - S3 Path"

class Transaction(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='transactions')
    credits = models.IntegerField()

    def __str__(self):
        return f"Transaction ID {self.id} - User: {self.user.email} - Credits: {self.credits}"

class Activity(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='activities')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    timestamp = models.DateTimeField(auto_now_add=True)
    old_state = models.JSONField(default=dict)
    new_state = models.JSONField(default=dict)

    def __str__(self):
        return f"Activity for Report ID {self.report.id} by {self.user.email}"