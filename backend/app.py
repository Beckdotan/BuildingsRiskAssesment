from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from models import PropertyData, RiskLevel, RiskFactor, RiskCategory, RiskAssessment

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
        "overall_risk_level": "Medium",
        "categories": [
            {
                "category_name": "Property Assessment",
                "category_risk_level": "Medium",
                "risk_factors": [
                    {
                        "category": "Building Age",
                        "risk_level": "High",
                        "description": "The property's age suggests potential issues with electrical systems and plumbing."
                    },
                    {
                        "category": "Construction Materials",
                        "risk_level": "Low",
                        "description": "The construction materials used are generally resistant to common hazards."
                    },
                    {
                        "category": "Safety Features",
                        "risk_level": "Medium",
                        "description": "Some essential safety features are present, but additional measures could improve overall safety."
                    }
                ]
            },
            {
                "category_name": "Location Factors",
                "category_risk_level": "Low",
                "risk_factors": [
                    {
                        "category": "Natural Disasters",
                        "risk_level": "No Risk",
                        "description": "The property is located in an area with low natural disaster probability."
                    },
                    {
                        "category": "Neighborhood Safety",
                        "risk_level": "Low",
                        "description": "The neighborhood has a relatively low crime rate and good emergency services access."
                    }
                ]
            },
            {
                "category_name": "Liability Risks",
                "category_risk_level": "Medium",
                "risk_factors": [
                    {
                        "category": "Tenant Safety",
                        "risk_level": "Medium",
                        "description": "Some potential liability concerns related to common areas and facility maintenance."
                    },
                    {
                        "category": "Regulatory Compliance",
                        "risk_level": "Low",
                        "description": "The property appears to meet most regulatory requirements with minor improvements needed."
                    }
                ]
            }
        ]
    }
    
    return risk_assessment

@app.get("/")
async def root():
    return {"message": "Welcome to the Multi-Family Property Risk Assessment API"}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)