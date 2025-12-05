# Resume ATS Scanner

A full-stack web application for scanning and analyzing resumes using Applicant Tracking System (ATS) technology. Built with Next.js frontend and FastAPI backend.

## Features

- 🔐 **User Authentication**: Secure JWT-based authentication with signup and login
- 📄 **Document Upload**: Upload resumes (PDF/DOCX) with drag-and-drop support
- ☁️ **Cloud Storage**: Documents stored securely in AWS S3
- 📊 **Document Management**: View, download, and delete uploaded resumes
- 🎨 **Modern UI**: Beautiful gradient design with animations and responsive layout
- 🔒 **Protected Routes**: Dashboard accessible only to authenticated users

## Tech Stack

### Backend

- **FastAPI**: Modern Python web framework
- **PostgreSQL**: Database for user and document metadata
- **SQLAlchemy**: ORM for database operations
- **JWT**: Token-based authentication
- **AWS S3**: Cloud storage for documents
- **Bcrypt**: Password hashing

### Frontend

- **Next.js 14+**: React framework with App Router
- **TypeScript**: Type-safe JavaScript
- **TailwindCSS**: Utility-first CSS framework
- **Axios**: HTTP client with interceptors
- **React Context**: Global state management

## Project Structure

```
ResumeMatchAI/
├── backend/
│   ├── auth/              # Authentication module
│   │   ├── routes.py      # Auth endpoints
│   │   ├── schemas.py     # Pydantic models
│   │   └── utils.py       # JWT & password utilities
│   ├── upload/            # Document upload module
│   │   ├── routes.py      # Upload endpoints
│   │   ├── schemas.py     # Document schemas
│   │   └── s3_service.py  # S3 integration
│   ├── database.py        # Database configuration
│   ├── models.py          # SQLAlchemy models
│   ├── main.py            # FastAPI application
│   └── requirements.txt   # Python dependencies
│
└── frontend/
    └── src/
        ├── app/           # Next.js pages
        │   ├── login/     # Login page
        │   ├── signup/    # Signup page
        │   ├── dashboard/ # Protected dashboard
        │   └── page.tsx   # Landing page
        ├── contexts/      # React contexts
        │   └── AuthContext.tsx
        └── lib/           # Utilities
            ├── api.ts     # Axios client
            ├── auth-controller.ts
            └── document-controller.ts
```

## Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js 18+
- PostgreSQL
- AWS Account (for S3)

### Backend Setup

1. Navigate to backend directory:

```bash
cd backend
```

2. Create and activate virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create `.env` file (copy from `.env.example`):

```bash
cp .env.example .env
```

5. Configure environment variables in `.env`:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/resumematch_db
SECRET_KEY=your-secret-key-here
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-bucket-name
FRONTEND_URL=http://localhost:3000
```

6. Create PostgreSQL database:

```bash
createdb resumematch_db
```

7. Run the server:

```bash
uvicorn main:app --reload
```

Backend will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:

```bash
cd frontend
```

2. Install dependencies:

```bash
npm install axios react-hook-form zod @hookform/resolvers lucide-react
```

3. Create `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

4. Run development server:

```bash
npm run dev
```

Frontend will be available at `http://localhost:3000`

## API Endpoints

### Authentication

- `POST /auth/signup` - Create new user account
- `POST /auth/login` - Login and get JWT tokens
- `POST /auth/refresh` - Refresh access token
- `GET /auth/me` - Get current user profile
- `POST /auth/logout` - Logout user

### Document Upload

- `POST /upload/document` - Upload a resume (requires auth)
- `GET /upload/documents` - Get all user documents (requires auth)
- `GET /upload/document/{id}` - Get specific document (requires auth)
- `DELETE /upload/document/{id}` - Delete document (requires auth)

## Usage

1. **Sign Up**: Create a new account at `/signup`
2. **Login**: Sign in at `/login`
3. **Upload Resume**: Drag and drop or click to upload your resume on the dashboard
4. **Manage Documents**: View, download, or delete your uploaded resumes

## Security Features

- Passwords hashed with bcrypt
- JWT tokens with expiration
- Automatic token refresh
- Protected API endpoints
- File type and size validation
- Secure S3 storage with presigned URLs

## Development

### Running Tests

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

### Code Formatting

```bash
# Backend
black .
isort .

# Frontend
npm run lint
```

## License

MIT License - see LICENSE file for details

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Support

For issues and questions, please open an issue on GitHub.
