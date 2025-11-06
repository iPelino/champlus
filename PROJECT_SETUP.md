# CharmPlus Project Setup

## Project Structure

```
charmplus/
├── backend/                    # Django REST Framework backend
│   ├── champlus_api/          # Main Django project settings
│   ├── users/                 # Users app
│   ├── groups/                # Groups app
│   ├── transactions/          # Transactions app
│   ├── manage.py
│   ├── requirements.txt       # Python dependencies
│   ├── .env                   # Backend environment variables (not in git)
│   └── .env.example           # Example environment variables
│
└── frontend/                  # React TypeScript frontend
    ├── src/
    │   ├── components/        # Reusable React components
    │   ├── pages/             # Page-level components
    │   ├── services/          # API service functions
    │   ├── hooks/             # Custom React hooks
    │   └── assets/            # Static assets
    ├── .env                   # Frontend environment variables (not in git)
    └── .env.example           # Example environment variables
```

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Copy the environment variables:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your configuration.

5. Run migrations:
   ```bash
   python manage.py migrate
   ```

6. Create a superuser (optional):
   ```bash
   python manage.py createsuperuser
   ```

7. Run the development server:
   ```bash
   python manage.py runserver
   ```
   The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies (already done during scaffolding):
   ```bash
   npm install
   ```

3. Copy the environment variables:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` if needed (default values should work for local development).

4. Run the development server:
   ```bash
   npm run dev
   ```
   The app will be available at `http://localhost:5173`

## Technology Stack

### Backend
- **Django 5.2.7**: Python web framework
- **Django REST Framework 3.16.1**: RESTful API toolkit
- **djangorestframework-simplejwt 5.3.1**: JWT authentication
- **django-cors-headers 4.6.0**: CORS handling
- **python-decouple 3.8**: Environment variable management

### Frontend
- **React 18**: UI library
- **TypeScript**: Type-safe JavaScript
- **Vite**: Build tool and dev server
- **ESLint**: Code linting

## API Endpoints

### Authentication
- `POST /api/token/` - Obtain JWT token pair
- `POST /api/token/refresh/` - Refresh access token
- `POST /api/token/verify/` - Verify token validity

### Admin
- `/admin/` - Django admin interface

## Environment Variables

### Backend (.env)
- `SECRET_KEY`: Django secret key
- `DEBUG`: Debug mode (True/False)
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `CORS_ALLOWED_ORIGINS`: Comma-separated list of allowed CORS origins

### Frontend (.env)
- `VITE_API_BASE_URL`: Backend base URL
- `VITE_API_URL`: Backend API URL

## Next Steps

1. Implement user authentication flows
2. Create API endpoints for users, groups, and transactions
3. Build frontend components and pages
4. Integrate frontend with backend APIs
5. Add comprehensive testing
