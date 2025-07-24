# Football Analytics SaaS Platform

A two-sided platform connecting sports teams with analytics consultants for game data analysis and insights.

## Project Structure

```
Football Analytics Program/
├── frontend/          # React TypeScript application
├── backend/           # Python Flask API
└── README.md
```

## Phase 1.1 - Authentication System ✅

### Completed Features

- **Project Setup**: React frontend with TypeScript and Python Flask backend
- **Authentication System**: JWT-based auth for teams and consultants
- **User Registration/Login**: Separate flows for teams and consultants
- **Protected Routes**: Role-based access control
- **Basic Dashboards**: Placeholder dashboards for both user types

### Backend API Endpoints

- `POST /api/auth/team/register` - Team registration
- `POST /api/auth/team/login` - Team login
- `POST /api/auth/consultant/register` - Consultant registration
- `POST /api/auth/consultant/login` - Consultant login
- `GET /api/auth/verify` - Token verification
- `GET /api/health` - Health check

### Frontend Routes

- `/login` - Login page (teams and consultants)
- `/register` - Registration page
- `/team/dashboard` - Team dashboard (protected)
- `/consultant/dashboard` - Consultant dashboard (protected)

## Getting Started

### Backend Setup

1. Navigate to backend directory:
   ```bash
   cd backend
   ```

2. Create and activate virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables in `.env` file

5. Start the Flask server:
   ```bash
   python app.py
   ```

### Frontend Setup

1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

### Database Setup

- PostgreSQL database required (configure in `.env`)
- Tables will be created automatically on first run

## Next Steps

Ready for **Phase 1.2**: Database schema implementation with games and play_data models.

## Technology Stack

- **Frontend**: React, TypeScript, React Router, Axios
- **Backend**: Python, Flask, SQLAlchemy, JWT
- **Database**: PostgreSQL
- **Authentication**: JWT tokens with bcrypt password hashing