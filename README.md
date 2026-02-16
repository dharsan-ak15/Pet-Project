# Online Pet Adoption and Shelter Management Portal

A full-stack Django + MySQL web application to help report lost/found pets and manage shelter verification workflows.

## Features

- User registration, login, logout (Django built-in authentication)
- User dashboard to:
  - report lost/found pets
  - search accepted pet reports
  - view submitted requests and status
- Admin request management panel:
  - list all requests
  - filter by status
  - accept/reject/delete requests
  - pagination
- Notification logic:
  - users receive dashboard notifications when admin changes request status
- Optional enhancement included:
  - image upload for pet reports

## Tech Stack

- **Frontend:** Django Templates, HTML, CSS, Bootstrap 5
- **Backend:** Django (latest stable series via requirements constraints)
- **Database:** MySQL
- **Auth:** Django built-in `User` model + session auth

## Project Structure

```text
Pet-Project/
├── manage.py
├── requirements.txt
├── README.md
├── pet_portal/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── accounts/
│   ├── forms.py
│   ├── views.py
│   └── urls.py
├── pets/
│   ├── models.py
│   ├── forms.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── signals.py
├── templates/
│   ├── base.html
│   ├── accounts/
│   ├── pets/
│   └── admin_panel/
└── static/css/styles.css
```

## Database Model

`PetRequest`
- `pet_type` (Dog, Cat, Other)
- `breed`
- `color`
- `location`
- `description`
- `contact_information`
- `request_type` (Lost / Found)
- `status` (Pending / Accepted / Rejected)
- `created_at`
- `updated_at`
- `image` (optional)
- `user` (ForeignKey to Django `User`)

`Notification`
- `user`
- `pet_request`
- `message`
- `is_read`
- `created_at`

## Step-by-Step Setup Instructions

### 1) Clone and enter project
```bash
git clone <your-repo-url>
cd Pet-Project
```

### 2) Create virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3) Install dependencies
```bash
pip install -r requirements.txt
```

### 4) Create MySQL database
Example:
```sql
CREATE DATABASE pet_portal_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 5) Configure environment variables
```bash
export MYSQL_DATABASE=pet_portal_db
export MYSQL_USER=root
export MYSQL_PASSWORD=yourpassword
export MYSQL_HOST=127.0.0.1
export MYSQL_PORT=3306
export DJANGO_SECRET_KEY='replace-with-a-secure-key'
export DJANGO_DEBUG=True
```

### 6) Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 7) Create superuser
```bash
python manage.py createsuperuser
```

### 8) Run development server
```bash
python manage.py runserver
```

Open:
- App: `http://127.0.0.1:8000/`
- Django Admin: `http://127.0.0.1:8000/admin/`
- Admin Request Panel: `http://127.0.0.1:8000/pets/admin/requests/`

## Notes

- `PyMySQL` is used as the MySQL driver via `pet_portal/__init__.py`.
- Notifications are auto-generated through a model signal whenever an admin changes a request's status.
- For production, set `DJANGO_DEBUG=False` and use strong secrets.
