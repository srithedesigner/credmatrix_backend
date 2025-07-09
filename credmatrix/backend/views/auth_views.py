from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import Group
from drf_spectacular.utils import extend_schema, OpenApiExample
from ..models import User, Entity, EntityType, OTP
from backend.services.email_service import send_email
import random


class signup_view(APIView):
    """
    Signup API
    ---
    Allows users to sign up by providing email, password, name, entity_name, entity_type, and OTP.
    """
    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "email": {"type": "string", "example": "user@example.com"},
                    "password": {"type": "string", "example": "securepassword"},
                    "name": {"type": "string", "example": "John Doe"},
                    "entity_name": {"type": "string", "example": "CredMatrix Inc."},
                    "entity_type": {"type": "string", "example": "STARTUP"},
                    "otp": {"type": "string", "example": "123456"},
                },
                "required": ["email", "password", "name", "entity_name", "entity_type", "otp"],
            }
        },
        responses={
            201: {"description": "User created successfully"},
            400: {"description": "Invalid entity type or incorrect OTP"},
        },
    )
    def post(self, request):
        data = request.data
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        entity_name = data.get('entity_name')
        entity_type = data.get('entity_type')
        otp = data.get('otp')

        # Validate entity type
        if entity_type not in [etype.name for etype in EntityType]:
            return Response({"error": "Invalid entity type"}, status=status.HTTP_400_BAD_REQUEST)

        # Validate OTP
        try:
            otp_record = OTP.objects.get(email=email)
            if otp_record.otp != otp:
                return Response({"error": "Incorrect OTP"}, status=status.HTTP_400_BAD_REQUEST)
        except OTP.DoesNotExist:
            return Response({"error": "OTP not found for this email"}, status=status.HTTP_400_BAD_REQUEST)

        # Create entity
        entity = Entity.objects.create(name=entity_name, entity_type=entity_type)

        # Create user
        user = User.objects.create(
            email=email,
            username=email,
            name=name,
            entity=entity
        )
        user.set_password(password)
        user.save()

        # Assign user to the "User" group
        user_group, _ = Group.objects.get_or_create(name='User')
        user.groups.add(user_group)

        # Delete OTP after successful signup
        otp_record.delete()

        return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)

class login_view(APIView):
    """
    Login API
    ---
    Allows users to log in by providing email and password. Returns JWT tokens.
    """
    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "email": {"type": "string", "example": "user@example.com"},
                    "password": {"type": "string", "example": "securepassword"},
                },
                "required": ["email", "password"],
            }
        },
        responses={
            200: {
                "description": "Login successful",
                "content": {
                    "application/json": {
                        "example": {
                            "access": "ACCESS_TOKEN",
                            "refresh": "REFRESH_TOKEN",
                        }
                    }
                },
            },
            401: {"description": "Invalid credentials"},
        },
    )
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(request, username=email, password=password)
        if user is not None:
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }, status=status.HTTP_200_OK)
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class logout_view(APIView):
    """
    Logout API
    ---
    Allows users to log out by blacklisting the refresh token.
    """
    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "refresh": {"type": "string", "example": "REFRESH_TOKEN"},
                },
                "required": ["refresh"],
            }
        },
        responses={
            200: {"description": "Logout successful"},
            400: {"description": "Invalid token"},
        },
    )
    def post(self, request):
        refresh_token = request.data.get('refresh')
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
        


class send_otp_view(APIView):
    """
    Send OTP API
    ---
    Sends an OTP to the user's email address.
    """
    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "email": {"type": "string", "example": "user@example.com"},
                },
                "required": ["email"],
            }
        },
        responses={
            200: {"description": "OTP sent successfully"},
            400: {"description": "Email is required"},
        },
    )
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Generate a random 6-digit OTP
        otp = str(random.randint(100000, 999999))

        # Save OTP to the database
        OTP.objects.update_or_create(email=email, defaults={"otp": otp})

        # Send OTP via email using the utility
        subject = "Your OTP for Signup"
        message = f"Your OTP is {otp}. It is valid for 5 minutes."
        mail_status = send_email(subject, message, [email])
        if not mail_status:
            return Response({"error": "Failed to send OTP"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({"message": "OTP sent successfully"}, status=status.HTTP_200_OK)