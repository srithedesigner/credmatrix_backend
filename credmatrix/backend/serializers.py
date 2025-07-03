from rest_framework import serializers
from backend.models import Report, Document

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ["id", "s3_path", "uploaded_at"]


class ReportSerializer(serializers.ModelSerializer):
    documents = DocumentSerializer(many=True, read_only=True)

    class Meta:
        model = Report
        fields = [
            "id",
            "status",
            "services", 
            "created_at",
            "target_entity_name",
            "target_entity_pan",
            "credits",
            "pending_documents",
            "cancellation_reason",
            "documents",
        ]


class InitiateRequestSerializer(serializers.Serializer):
    entity_name = serializers.CharField(max_length=255, required=True)
    entity_pan = serializers.CharField(max_length=20, required=True)
    services = serializers.ListField(  # Updated to handle a list of services
        child=serializers.CharField(max_length=50),
        required=True,
    )
    credits = serializers.IntegerField(required=True)
    document_ids = serializers.ListField(  # Added to handle document IDs
        child=serializers.IntegerField(),
        required=False,
    )


class DeleteReportSerializer(serializers.Serializer):
    cancellation_reason = serializers.CharField(max_length=255, required=True)


class ConfirmDocumentUploadSerializer(serializers.Serializer):
    document_id = serializers.IntegerField(required=True, help_text="ID of the document to confirm.")

class UploadDocumentSerializer(serializers.Serializer):
    report_id = serializers.IntegerField(required=False, help_text="ID of the report to associate the document with (optional).")
    document_name = serializers.CharField(required=True, help_text="Name of the document to upload.")