from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class RiskLevel(str, Enum):
    NO_RISK = "No Risk"
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class PropertyData(BaseModel):
    propertyAge: int
    numberOfUnits: int
    constructionType: str
    safetyFeatures: List[str]
    location: Optional[str] = None

class RiskFactor(BaseModel):
    category: str
    risk_level: RiskLevel
    description: str
    
    class Config:
        schema_extra = {
            "example": {
                "category": "Building Age",
                "risk_level": "High",
                "description": "The property's age suggests potential issues with electrical systems and plumbing."
            }
        }

class RiskCategory(BaseModel):
    category_name: str
    category_risk_level: RiskLevel
    risk_factors: List[RiskFactor]
    
    class Config:
        schema_extra = {
            "example": {
                "category_name": "Property Assessment",
                "category_risk_level": "Medium",
                "risk_factors": [
                    {
                        "category": "Building Age",
                        "risk_level": "High",
                        "description": "The property's age suggests potential issues with electrical systems and plumbing."
                    }
                ]
            }
        }

class RiskAssessment(BaseModel):
    overall_risk_level: RiskLevel
    categories: List[RiskCategory]
    
    class Config:
        schema_extra = {
            "example": {
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
                            }
                        ]
                    }
                ]
            }
        }