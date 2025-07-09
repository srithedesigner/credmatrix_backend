import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from backend.services.s3_service import S3Service
from django.conf import settings

@pytest.fixture
def s3_service():
    """Provide an instance of the S3Service."""
    return S3Service(False)

@pytest.fixture
def test_file_content():
    """Provide test file content."""
    return b"This is a test file."

@pytest.fixture
def test_file_key():
    """Provide a test file key."""
    return "test-folder/test-file.txt"

@pytest.mark.order(1)
def test_upload_file(s3_service, test_file_key, test_file_content):
    """Test uploading a file to S3."""
    # Generate presigned URL for upload
    presigned_url = s3_service.upload_file(test_file_key)
    assert presigned_url is not None

    # Upload file using presigned URL
    import requests
    response = requests.put(presigned_url, data=test_file_content)
    assert response.status_code == 200

    # Verify file exists in S3
    s3_client = s3_service.s3_client
    response = s3_client.head_object(Bucket=settings.AWS_BUCKET_NAME, Key=test_file_key)
    assert response['ResponseMetadata']['HTTPStatusCode'] == 200

@pytest.mark.order(2)
def test_download_file(s3_service, test_file_key, test_file_content):
    """Test downloading a file from S3."""
    # Check if the file exists before proceeding
    s3_client = s3_service.s3_client
    try:
        s3_client.head_object(Bucket=settings.AWS_BUCKET_NAME, Key=test_file_key)
    except Exception:
        pytest.skip("File does not exist. Skipping download test.")

    # Generate presigned URL for download
    presigned_url = s3_service.download_file(test_file_key)
    assert presigned_url is not None

    # Download file using presigned URL
    import requests
    response = requests.get(presigned_url)
    assert response.status_code == 200
    assert response.content == test_file_content

@pytest.mark.order(3)
def test_delete_file(s3_service, test_file_key):
    """Test deleting a file from S3."""
    # Check if the file exists before proceeding
    s3_client = s3_service.s3_client
    try:
        s3_client.head_object(Bucket=settings.AWS_BUCKET_NAME, Key=test_file_key)
    except Exception:
        pytest.skip("File does not exist. Skipping delete test.")

    # Delete file from S3
    s3_service.delete_file(test_file_key)

    # Verify file is deleted
    with pytest.raises(Exception):
        s3_client.head_object(Bucket=settings.AWS_BUCKET_NAME, Key=test_file_key)