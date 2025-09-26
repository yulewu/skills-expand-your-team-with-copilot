# Mergington High School Activities

A comprehensive web application that allows teachers to manage extracurricular activities and register students. The system provides a modern, interactive interface for viewing activities with advanced filtering, search capabilities, and teacher-authenticated student registration.

## Features

### For Teachers
- **Secure Authentication**: Teacher login system with username/password authentication
- **Student Registration Management**: Register students for activities with email validation  
- **Student Removal**: Remove students from activities with confirmation prompts
- **Real-time Updates**: Activity lists update automatically after registration changes

### For Everyone (Viewing)
- **Browse Activities**: View all available extracurricular activities with detailed information
- **Advanced Search**: Search activities by name, description, or schedule details
- **Smart Filtering**: Filter by category (Sports, Academic, Arts, Technology, etc.)
- **Schedule Filtering**: Filter by day of the week and time periods (before school, after school, weekend)
- **Activity Details**: View participant counts, schedules, and capacity limits
- **Responsive Design**: Works on desktop and mobile devices

### Activity Information
- **Comprehensive Schedules**: View days, times, and duration for each activity
- **Participant Management**: See current enrollment and maximum capacity
- **Category Organization**: Activities organized by type (Sports, Academic, Arts, etc.)
- **Time-based Filtering**: Separate morning, afternoon, and weekend activities

## Technology Stack

- **Backend**: FastAPI (Python web framework)
- **Database**: MongoDB for data persistence  
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Server**: Uvicorn ASGI server
- **Authentication**: Custom teacher authentication system with password hashing

## API Endpoints

### Activities
- `GET /activities` - Get all activities with optional filtering by day and time
- `GET /activities/days` - Get list of all days that have activities scheduled
- `POST /activities/{activity_name}/signup` - Sign up a student (requires teacher authentication)
- `POST /activities/{activity_name}/unregister` - Remove a student (requires teacher authentication)

### Authentication  
- `POST /auth/login` - Teacher login endpoint
- `GET /auth/check-session` - Validate teacher session

## Prerequisites

- Python 3.8+
- MongoDB (running on localhost:27017)
- Modern web browser with JavaScript enabled

## Sample Teacher Accounts

For testing purposes, the system includes these teacher accounts:

| Username | Password | Display Name | Role |
|----------|----------|--------------|------|
| `mrodriguez` | `art123` | Ms. Rodriguez | Teacher |
| `mchen` | `chess456` | Mr. Chen | Teacher |  
| `principal` | `admin789` | Principal Martinez | Admin |

## Development Guide

For detailed setup and development instructions, please refer to our [Development Guide](../docs/how-to-develop.md).
