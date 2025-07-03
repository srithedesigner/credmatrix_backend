# CredMatrix Backend

This is the backend for the CredMatrix application, built using Django and Django REST Framework.

## Setup Instructions

1. Clone the Repository:
   git clone https://github.com/srithedesigner/credmatrix_backend.git
   cd credmatrix_backend

2. Create a Virtual Environment:
   python3 -m venv env
   source env/bin/activate

3. Install Dependencies:
   pip install -r requirements.txt

4. Configure Environment Variables:
   Create a `.env` file and add:
   SECRET_KEY=your_secret_key
   DEBUG=True
   DATABASE_URL=postgres://username:password@localhost:5432/credmatrix_db
   AWS_ACCESS_KEY_ID=your_aws_access_key
   AWS_SECRET_ACCESS_KEY=your_aws_secret_key
   AWS_STORAGE_BUCKET_NAME=your_bucket_name

5. Apply Migrations:
   python manage.py migrate

6. Run the Server:
   python manage.py runserver

## API Documentation

- Swagger UI: http://127.0.0.1:8000/api/docs/
- OpenAPI Schema: http://127.0.0.1:8000/api/schema/

## To-Do List

- Write unit tests for views and serializers.
- Improve error handling and logging.
- Connect DB
- Testing integration
- adding admin views
- adding payment gateway

## License

Licensed under the MIT License.