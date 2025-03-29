# Multi-Family Property Risk Assessment Tool

A web application that provides risk assessments for multi-family properties to assist insurance companies in evaluating property risks.

## Project Overview

This application helps insurance professionals analyze and assess risks associated with multi-family properties. By inputting property details such as age, number of units, construction type, and safety features, users receive a comprehensive risk assessment that identifies potential hazards and provides recommendations for risk mitigation.

### Key Features

- Property data collection through an intuitive web interface
- Risk assessment analysis across multiple categories
- Detailed risk factor breakdown with explanations
- Actionable recommendations for risk mitigation

## Technical Architecture

The application follows a client-server architecture with:

- **Frontend**: React-based single-page application
- **Backend**: FastAPI Python server providing REST API endpoints

## Installation Guide

### Prerequisites

- Python 3.8+ for the backend
- Node.js 14+ and npm for the frontend
- Git (optional, for cloning the repository)

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd BuildingsRiskAssesment/backend
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows:
     ```
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```
     source venv/bin/activate
     ```

4. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd BuildingsRiskAssesment/frontend
   ```

2. Install the required dependencies:
   ```
   npm install
   ```

## Running the Application

### Backend

1. Navigate to the backend directory:
   ```
   cd BuildingsRiskAssesment/backend
   ```

2. Start the FastAPI server:
   ```
   python app.py
   ```
   The API will be available at http://localhost:5000

### Frontend

1. Navigate to the frontend directory:
   ```
   cd BuildingsRiskAssesment/frontend
   ```

2. Start the development server:
   ```
   npm run dev
   ```
   The web application will be available at http://localhost:5173

## API Documentation

Once the backend server is running, you can access the automatically generated API documentation at:
- Swagger UI: http://localhost:5000/docs
- ReDoc: http://localhost:5000/redoc

## Technical Considerations

### Current Implementation

- The backend currently uses a mock response for risk assessment
- CORS is configured to allow requests from any origin (for development purposes)
- The frontend communicates with the backend via HTTP requests using Axios

### Future Enhancements

- Integration with a Language Model (LLM) for more sophisticated risk assessments
- User authentication and authorization
- Database integration for storing property data and assessment history
- More detailed property input fields for more accurate assessments
- Customizable risk assessment parameters for different insurance needs

### Security Considerations

- In a production environment, CORS should be restricted to specific origins
- API rate limiting should be implemented to prevent abuse
- Input validation should be enhanced for security
- Proper error handling and logging should be implemented

## License

© 2023 Property Risk Assessment Tool
