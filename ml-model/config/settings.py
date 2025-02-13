# config/settings.py
import os

# Application Metadata
APP_TITLE = "Precision-Tuned Recommendation System"
APP_DESCRIPTION = """
A sophisticated recommendation system designed to provide personalized 
product suggestions based on user interactions and preferences.
"""
APP_VERSION = "0.1.0"

# CORS Configuration
ALLOWED_ORIGINS = [
    "http://localhost:5173",  # React development server
    "https://yourdomain.com",  # Production domain
]

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL")

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")