from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from backend.models import Report, Activity, Transaction, Document
from django.utils.timezone import now
from backend.serializers import ReportSerializer
from drf_spectacular.utils import extend_schema, OpenApiExample
from backend.serializers import InitiateRequestSerializer
from backend.serializers import DeleteReportSerializer, UploadDocumentSerializer, ConfirmDocumentUploadSerializer
from backend.services.s3_service import s3_service




class GetReportsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get Reports",
        description="Fetch all reports made by users in the same entity as the authenticated user, including document details.",
        responses={
            200: {
                "description": "Reports fetched successfully",
                "content": {
                    "application/json": {
                        "example": {
                            "reports": [
                                {
                                    "id": 1,
                                    "status": "REQUEST_RAISED",
                                    "services": "FINANCIAL_INFO",
                                    "created_at": "2025-07-01T10:00:00Z",
                                    "target_entity_name": "CredMatrix Inc.",
                                    "target_entity_pan": "ABCD123456",
                                    "credits": 10,
                                    "pending_documents": [],
                                    "cancellation_reason": None,
                                    "documents": [
                                        {
                                            "id": 101,
                                            "s3_path": "s3://bucket-name/documents/report1/doc1.pdf",
                                            "uploaded_at": "2025-06-30T15:00:00Z"
                                        },
                                        {
                                            "id": 102,
                                            "s3_path": "s3://bucket-name/documents/report1/doc2.pdf",
                                            "uploaded_at": "2025-06-30T16:00:00Z"
                                        }
                                    ]
                                }
                            ]
                        }
                    }
                },
            },
            400: {"description": "User does not belong to any entity"},
            401: {"description": "Authentication credentials were not provided"},
        },
    )
    def get(self, request):
        user = request.user
        entity = user.entity

        if not entity:
            return Response({"error": "User does not belong to any entity"}, status=400)

        reports = Report.objects.filter(user__entity=entity)
        serializer = ReportSerializer(reports, many=True)
        return Response(serializer.data, status=200)



class EditReportView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Edit Report",
        description="Allows authenticated users to edit the contents of a report and upload new documents.",
        request=ReportSerializer,
        responses={
            200: {
                "description": "Report updated successfully",
                "content": {
                    "application/json": {
                        "example": {
                            "message": "Report updated successfully",
                            "report": {
                                "id": 1,
                                "status": "UNDER_ASSESMENT",
                                "services": "FINANCIAL_INFO",
                                "created_at": "2025-07-01T10:00:00Z",
                                "target_entity_name": "CredMatrix Inc.",
                                "target_entity_pan": "ABCD123456",
                                "credits": 15,
                                "documents": [
                                    {
                                        "id": 101,
                                        "s3_path": "entity_id/report_id/financial_report.pdf",
                                        "uploaded_at": "2025-07-01T10:00:00Z"
                                    }
                                ]
                            }
                        }
                    }
                },
            },
            404: {"description": "Report not found"},
            400: {"description": "Invalid data provided"},
        },
    )
    def put(self, request, report_id):
        try:
            report = Report.objects.get(id=report_id)

            old_state = {field: getattr(report, field) for field in request.data.keys()}

            serializer = ReportSerializer(report, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()

                new_state = {field: serializer.data[field] for field in request.data.keys()}

                Activity.objects.create(
                    report=report,
                    user=request.user,
                    old_state=old_state,
                    new_state=new_state,
                    timestamp=now(),
                )

                return Response({"message": "Report updated successfully", "report": serializer.data}, status=200)
            return Response({"error": serializer.errors}, status=400)
        except Report.DoesNotExist:
            return Response({"error": "Report not found"}, status=404)

class DeleteReportView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Delete (Cancel) Report",
        description="Allows authenticated users to cancel a report by providing a cancellation reason. The report status is updated to 'CANCELLED'.",
        request=DeleteReportSerializer,  # Use the serializer here
        responses={
            200: {
                "description": "Report canceled successfully",
                "content": {
                    "application/json": {
                        "example": {
                            "message": "Report canceled successfully",
                            "report": {
                                "id": 1,
                                "status": "CANCELLED",
                                "cancellation_reason": "The requester provided incomplete information."
                            }
                        }
                    }
                },
            },
            404: {"description": "Report not found"},
            400: {"description": "Invalid data provided"},
        },
    )
    def patch(self, request, report_id):
        try:
            report = Report.objects.get(id=report_id)

            serializer = DeleteReportSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({"error": serializer.errors}, status=400)

            cancellation_reason = serializer.validated_data["cancellation_reason"]

            report.status = "CANCELLED"
            report.cancellation_reason = cancellation_reason
            report.save()

            Activity.objects.create(
                report=report,
                user=request.user,
                old_state={"status": report.status, "cancellation_reason": report.cancellation_reason},
                new_state={"status": "CANCELLED", "cancellation_reason": cancellation_reason},
                timestamp=now(),
            )

            return Response(
                {
                    "message": "Report canceled successfully",
                    "report": {
                        "id": report.id,
                        "status": report.status,
                        "cancellation_reason": report.cancellation_reason,
                    },
                },
                status=200,
            )
        except Report.DoesNotExist:
            return Response({"error": "Report not found"}, status=404)


class InitiateRequestView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Initiate Request",
        description="Allows authenticated users to initialize a report and upload associated documents.",
        request=InitiateRequestSerializer,
        responses={
            201: {
                "description": "Request initiated successfully",
                "content": {
                    "application/json": {
                        "example": {
                            "message": "Request initiated successfully",
                            "report": {
                                "id": 1,
                                "status": "REQUEST_RAISED",
                                "services": "BUREAU_REPORT",
                                "created_at": "2025-07-01T10:00:00Z",
                                "target_entity_name": "CredMatrix Inc.",
                                "target_entity_pan": "ABCD123456",
                                "credits": 12,
                                "documents": [
                                    {
                                        "id": 101,
                                        "s3_path": "entity_id/report_id/financial_report.pdf",
                                        "uploaded_at": "2025-07-01T10:00:00Z"
                                    }
                                ]
                            }
                        }
                    }
                },
            },
            400: {"description": "Invalid data or insufficient credits"},
        },
    )
    def post(self, request):
        serializer = InitiateRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"error": serializer.errors}, status=400)

        user = request.user
        entity = user.entity
        if not entity:
            return Response({"error": "User does not belong to any entity"}, status=400)
        
        data = serializer.validated_data

        required_credits = get_required_credits(data["services"])

        if entity.credits < required_credits:
            return Response({"error": "Insufficient credits"}, status=400)


        report = Report.objects.create(
            user=user,
            status="REQUEST_RAISED",
            services=data["services"],
            created_at=now(),
            target_entity_name=data["entity_name"],
            target_entity_pan=data["entity_pan"],
            credits=required_credits,
        )


        document_ids = data.get("document_ids", [])
        Document.objects.filter(id__in=document_ids, user=user, report=None).update(
            report=report, uploaded_at=now()
        )

        entity.credits -= required_credits
        entity.save()

        Transaction.objects.create(
            user=user,
            report=report,
            credits=required_credits,
            created_at=now(),
        )

        return Response(
            {
                "message": "Request initiated successfully",
                "report": {
                    "id": report.id,
                    "status": report.status,
                    "services": report.services,
                    "created_at": report.created_at,
                    "target_entity_name": report.target_entity_name,
                    "target_entity_pan": report.target_entity_pan,
                    "credits": report.credits,
                    "documents": [
                        {
                            "id": doc.id,
                            "s3_path": doc.s3_path,
                            "uploaded_at": doc.uploaded_at,
                        }
                        for doc in report.documents.all()
                    ],
                },
            },
            status=201,
        )


class ConfirmDocumentUploadView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Confirm Document Upload",
        description="Confirms that a document has been successfully uploaded to S3. Updates the `uploaded_at` timestamp for the document.",
        request=ConfirmDocumentUploadSerializer,
        responses={
            201: {
                "description": "Document confirmed successfully",
                "content": {
                    "application/json": {
                        "example": {
                            "message": "Document confirmed successfully",
                            "document": {
                                "id": 123,
                                "s3_path": "entity_id/report_id/financial_report.pdf",
                                "uploaded_at": "2025-07-01T10:00:00Z"
                            }
                        }
                    }
                },
            },
            400: {
                "description": "Invalid data provided",
                "content": {
                    "application/json": {
                        "example": {
                            "error": "document_id is required"
                        }
                    }
                },
            },
            404: {
                "description": "Document not found",
                "content": {
                    "application/json": {
                        "example": {
                            "error": "Document not found"
                        }
                    }
                },
            },
        },
    )
    def post(self, request):
        serializer = ConfirmDocumentUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"error": serializer.errors}, status=400)

        document_id = serializer.validated_data["document_id"]

        try:
            document = Document.objects.get(id=document_id, user=request.user)

            # Confirm the upload
            document.uploaded_at = now()
            document.save()

            return Response(
                {
                    "message": "Document confirmed successfully",
                    "document": {
                        "id": document.id,
                        "s3_path": document.s3_path,
                        "uploaded_at": document.uploaded_at,
                    },
                },
                status=201,
            )
        except Document.DoesNotExist:
            return Response({"error": "Document not found"}, status=404)


class UploadDocumentView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Upload Document",
        description="Generates a presigned URL for uploading a document to S3. Optionally associates the document with a report if `report_id` is provided.",
        request=UploadDocumentSerializer,
        responses={
            200: {
                "description": "Presigned URL generated successfully",
                "content": {
                    "application/json": {
                        "example": {
                            "message": "Presigned URL generated successfully",
                            "upload_url": "https://s3.amazonaws.com/bucket-name/entity_id/report_id/financial_report.pdf?AWSAccessKeyId=...",
                            "key": "entity_id/report_id/financial_report.pdf",
                            "document_id": 123
                        }
                    }
                },
            },
            400: {
                "description": "Invalid data provided",
                "content": {
                    "application/json": {
                        "example": {
                            "error": "document_name is required"
                        }
                    }
                },
            },
            500: {
                "description": "Internal server error",
                "content": {
                    "application/json": {
                        "example": {
                            "error": "An unexpected error occurred"
                        }
                    }
                },
            },
        },
    )
    def post(self, request):
        serializer = UploadDocumentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"error": serializer.errors}, status=400)

        document_name = serializer.validated_data["document_name"]
        report_id = serializer.validated_data.get("report_id")

        try:
            # Construct the S3 key
            user_id = request.user.id
            s3_key = f"{user_id}/temp/{document_name}" if not report_id else f"{user_id}/{report_id}/{document_name}"

            # Generate the presigned URL
            upload_url = s3_service.upload_file(s3_key)

            # Store the temporary document in the database
            document = Document.objects.create(
                user=request.user,
                s3_path=s3_key,
                uploaded_at=None,  # Set uploaded_at to None until confirmed
                report_id=report_id if report_id else None,
            )

            return Response(
                {
                    "message": "Presigned URL generated successfully",
                    "upload_url": upload_url,
                    "key": s3_key,
                    "document_id": document.id,
                },
                status=200,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=500)