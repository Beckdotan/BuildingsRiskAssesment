from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import os

# Define Pydantic models for request validation
class PropertyData(BaseModel):
    propertyAge: int
    numberOfUnits: int
    constructionType: str
    safetyFeatures: List[str]

# Define response models
class RiskFactor(BaseModel):
    category: str
    risk_level: str
    description: str

class RiskAssessment(BaseModel):
    overall_risk_score: int
    risk_factors: List[RiskFactor]
    recommendations: List[str]

# Create FastAPI app
app = FastAPI(title="Multi-Family Property Risk Assessment API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/assess", response_model=RiskAssessment)
async def assess_property(property_data: PropertyData):
    # In a real implementation, this would integrate with an LLM
    # For now, we'll return a mock response
    risk_assessment = {
        "overall_risk_score": 65,
        "risk_factors": [
            {
                "category": "Building Age",
                "risk_level": "Medium",
                "description": "The property's age suggests potential issues with electrical systems and plumbing."
            },
            {
                "category": "Construction Type",
                "risk_level": "Low",
                "description": "The construction materials used are generally resistant to common hazards."
            },
            {
                "category": "Safety Features",
                "risk_level": "Medium",
                "description": "Some essential safety features are present, but additional measures could improve overall safety."
            }
        ],
        "recommendations": [
            "Consider updating electrical systems",
            "Implement additional fire safety measures",
            "Regular inspection of plumbing systems is advised"
        ]
    }
    
    return risk_assessment

@app.get("/")
async def root():
    return {"message": "Welcome to the Multi-Family Property Risk Assessment API"}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)