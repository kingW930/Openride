# OpenSeat Backend

FastAPI backend for the OpenSeat rideshare platform - a community-powered micro-ridesharing platform for daily work commutes.

## Features

- 🔐 JWT Authentication & Authorization
- 🚗 Route Management with AI-powered matching
- 📱 Real-time booking system
- 💳 Interswitch payment integration
- ⛓️ Blockchain token verification
- 🗄️ PostgreSQL database with SQLAlchemy ORM
- ✅ Request validation with Pydantic
- 🛡️ Comprehensive error handling

## Tech Stack

- **Framework**: FastAPI 0.104.1
- **Database**: PostgreSQL with SQLAlchemy
- **Authentication**: JWT with python-jose
- **Validation**: Pydantic v2
- **Payment**: Interswitch API
- **AI**: Custom route matching algorithm

## Project Structure

```
backend/
├── src/
│   ├── config/          # Configuration and database setup
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic schemas
│   ├── controllers/     # Business logic
│   ├── routes/          # API endpoints
│   ├── middleware/      # Auth & error handling
│   └── utils/           # Utilities (AI, blockchain, payments)
├── main.py              # FastAPI application entry point
├── requirements.txt     # Python dependencies
└── .env.example         # Environment variables template
```

## Setup Instructions

### 1. Prerequisites

- Python 3.9+
- PostgreSQL 13+
- pip or poetry

### 2. Clone and Install

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Unix/MacOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Database Setup

```bash
# Create PostgreSQL database
createdb openseat_db

# Or using psql:
psql -U postgres
CREATE DATABASE openseat_db;
\q
```

### 4. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# Update DATABASE_URL with your PostgreSQL credentials
# Update JWT_SECRET_KEY with a secure random key
```

### 5. Run the Application

```bash
# Run with uvicorn
python main.py

# Or run directly with uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user profile

### Routes
- `POST /api/routes` - Create route (drivers only)
- `GET /api/routes/search` - Search available routes
- `GET /api/routes/{id}` - Get route details
- `GET /api/routes/my-routes` - Get driver's routes
- `PATCH /api/routes/{id}` - Update route
- `DELETE /api/routes/{id}` - Delete route

### Bookings
- `POST /api/bookings` - Create booking
- `GET /api/bookings/user/{userId}` - Get user bookings
- `GET /api/bookings/{id}` - Get booking details
- `PATCH /api/bookings/{id}` - Update booking
- `DELETE /api/bookings/{id}` - Cancel booking

### Payments
- `POST /api/payments/initiate` - Initiate payment
- `POST /api/payments/verify` - Verify payment
- `POST /api/payments/webhook` - Payment webhook handler

### Vehicles
- `POST /api/vehicles` - Register vehicle
- `GET /api/vehicles` - Get user vehicles
- `GET /api/vehicles/{id}` - Get vehicle details
- `PATCH /api/vehicles/{id}` - Update vehicle
- `DELETE /api/vehicles/{id}` - Delete vehicle

## Environment Variables

See `.env.example` for all required environment variables.

Key variables:
- `DATABASE_URL` - PostgreSQL connection string
- `JWT_SECRET_KEY` - Secret key for JWT tokens
- `INTERSWITCH_MERCHANT_CODE` - Interswitch merchant code
- `INTERSWITCH_PAY_ITEM_ID` - Interswitch payment item ID

## Database Models

- **User** - User accounts (drivers/riders)
- **Vehicle** - Vehicle registration
- **Route** - Daily commute routes
- **Booking** - Seat reservations
- **Payment** - Payment transactions
- **Rating** - User ratings

## Development

### Generate Database Migrations

```bash
# Initialize Alembic (first time only)
alembic init alembic

# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

### Run Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

## Production Deployment

1. Set `DEBUG=False` in `.env`
2. Use strong `JWT_SECRET_KEY`
3. Configure production database
4. Set up proper CORS origins
5. Use production Interswitch credentials
6. Enable HTTPS
7. Set up proper logging

## License

MIT License

## Support

For issues and questions, please open an issue on GitHub.
