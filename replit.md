# Harsha Projects - Portfolio Website

## Overview

This is a Flask-based portfolio website for showcasing electronics and software development projects. The application serves as both a project portfolio and knowledge base, featuring user authentication, content management, and search functionality.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Database**: SQLite for development/preview (configured for easy transition to PostgreSQL)
- **Data Layer**: SQLAlchemy ORM with declarative base model
- **Authentication**: Flask-Login for session management
- **Forms**: WTForms with Flask-WTF for form handling and validation

### Frontend Architecture
- **Template Engine**: Jinja2 (Flask's default)
- **CSS Framework**: Bootstrap 5
- **Icons**: Font Awesome 6
- **Theme System**: Dark/Light theme toggle with localStorage persistence
- **JavaScript**: Vanilla JS for interactive features

### File Structure
- **Main Application**: `app.py` (Flask app configuration)
- **Routes**: `routes.py` (URL endpoints and view logic)
- **Models**: `models.py` (database schema definitions)
- **Forms**: `forms.py` (form classes and validation)
- **Utilities**: `utils.py` (file upload helpers), `email_utils.py` (email verification)
- **Templates**: Organized in `templates/` with admin subdirectory
- **Static Assets**: CSS, JS, and upload directories

## Key Components

### Authentication System
- User registration with email verification (OTP-based)
- Login/logout functionality with "remember me" option
- Admin role-based access control
- Profile management with photo uploads

### Content Management
- **Projects**: Electronics and software development projects
- **Testing**: Test procedures and experimental results
- Both content types support:
  - Rich text descriptions
  - Image uploads (photos, circuit diagrams)
  - Video demonstrations
  - Code snippets with syntax highlighting
  - Step-by-step procedures

### File Upload System
- Secure file handling with allowed extensions
- Organized storage in `/static/uploads/` subdirectories
- Support for images (PNG, JPG, GIF, SVG), videos (MP4), and documents (PDF, TXT)
- 16MB maximum file size limit

### Search Functionality
- Full-text search across projects and testing items
- Search results organized by content type

## Data Flow

### User Registration Flow
1. User fills registration form with interests selection
2. System validates data and creates verification record
3. OTP sent via email (currently console logging for development)
4. User enters OTP for email verification
5. Account activated upon successful verification

### Content Creation Flow
1. Admin users access content creation forms
2. Form data validated (title, description required)
3. Files uploaded and saved to organized directories
4. Database records created with file paths
5. Content immediately available to authenticated users

### Search Flow
1. User submits search query
2. System searches across project and testing titles/descriptions
3. Results filtered and organized by content type
4. Paginated results displayed with preview cards

## External Dependencies

### Python Packages
- Flask ecosystem (Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF)
- Werkzeug (security utilities, file handling)
- WTForms (form validation)
- SQLAlchemy (database ORM)

### Frontend Libraries
- Bootstrap 5 (responsive design, components)
- Font Awesome 6 (icons)
- Custom CSS with CSS variables for theming

### File Storage
- Local filesystem storage for uploaded files
- Organized directory structure under `/static/uploads/`

## Deployment Strategy

### Development Configuration
- SQLite database for easy setup and preview
- Debug mode enabled
- Console logging for email verification
- Local file storage

### Production Considerations
- Database: Easily configurable to PostgreSQL via connection string
- Email: Ready for integration with SendGrid or similar service
- File Storage: Can be extended to cloud storage (S3, etc.)
- Security: Environment-based secret key management
- Proxy: ProxyFix configured for reverse proxy deployment

### Security Features
- CSRF protection via Flask-WTF
- Secure filename handling for uploads
- Password hashing with Werkzeug
- Session-based authentication
- Input validation and sanitization

The application is designed for easy deployment to platforms like Replit, Heroku, or similar PaaS providers, with minimal configuration changes needed for production use.