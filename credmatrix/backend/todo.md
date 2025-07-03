# TODO List

1. Implement session-based cleanup for temporary documents:
   - Track uploaded documents in the user's session.
   - Clean up unreferenced documents when the user abandons the initiation process or the session expires.
   - Ensure documents are deleted from both the database and S3.

2. Update the `services` field in the `Report` model:
   - Change it from a `CharField` to a `ListField` or equivalent to support multiple services.
   - Update serializers, views, and database migrations

