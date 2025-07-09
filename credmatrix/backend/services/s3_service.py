import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from django.conf import settings

class S3Service:
    def __init__(self, is_test=False):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key= settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )
        self.bucket_name = settings.AWS_BUCKET_NAME if not is_test else settings.AWS_TEST_BUCKET_NAME

    def upload_file(self, file_key, expiration=3600):
        """
        Generate a presigned URL for uploading a file to S3.

        :param file_key: The key (path) for the file in the S3 bucket.
        :param expiration: Time in seconds for the presigned URL to remain valid.
        :return: Presigned URL for uploading the file.
        """
        try:
            presigned_url = self.s3_client.generate_presigned_url(
                'put_object',
                Params={'Bucket': self.bucket_name, 'Key': file_key},
                ExpiresIn=expiration,
            )
            return presigned_url
        except (NoCredentialsError, PartialCredentialsError) as e:
            raise Exception(f"Error generating presigned URL for upload: {str(e)}")

    def download_file(self, file_key, expiration=3600):
        """
        Generate a presigned URL for downloading a file from S3.

        :param file_key: The key (path) for the file in the S3 bucket.
        :param expiration: Time in seconds for the presigned URL to remain valid.
        :return: Presigned URL for downloading the file.
        """
        try:
            presigned_url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': file_key},
                ExpiresIn=expiration,
            )
            return presigned_url
        except (NoCredentialsError, PartialCredentialsError) as e:
            raise Exception(f"Error generating presigned URL for download: {str(e)}")
        
    def delete_file(self, file_key):
        """
        Delete a file from S3.

        :param file_key: The key (path) of the file in the S3 bucket.
        :return: None
        """
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=file_key)
        except Exception as e:
            raise Exception(f"Failed to delete file from S3: {str(e)}")

s3_service = S3Service()