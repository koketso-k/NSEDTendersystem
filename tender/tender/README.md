Tender Insight Hub - Setup Guide
Prerequisites
Python 3.8+

MySQL 8.0+

MongoDB 4.4+

Node.js 16+ (for frontend)

===================================================================================================================================================
Quick Start

1. Database Setup
MySQL:
CREATE DATABASE tender_hub;
CREATE USER 'tender_user'@'localhost' IDENTIFIED BY 'password123';
GRANT ALL PRIVILEGES ON tender_hub.* TO 'tender_user'@'localhost';
FLUSH PRIVILEGES;

===================================================================================================================================================
MongoDB:

Install and start MongoDB service

No setup required - creates collections automatically

===================================================================================================================================================
2. Backend Setup
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt


===================================================================================================================================================

Create .env file in backend directory

DATABASE_URL=mysql+pymysql://tender_user:password123@localhost/tender_hub
MONGO_URL=mongodb://localhost:27017/
SECRET_KEY=your-super-secret-jwt-key
FRONTEND_URL=http://localhost:3000

===================================================================================================================================================

Start backend:

python run.py
Backend runs on: http://localhost:8000


===================================================================================================================================================

3. Frontend Setup

cd frontend
npm install
npm start

Frontend runs on: http://localhost:3000
===================================================================================================================================================

Test Accounts
Admin: admin@construction.com / password123

IT Manager: dev@itsolutions.com / password123

Features
Multi-tenant SaaS platform

AI tender summarization

Readiness scoring

Team workspace

Tender search & filtering

API Documentation: http://localhost:8000/docs

===================================================================================================================================================