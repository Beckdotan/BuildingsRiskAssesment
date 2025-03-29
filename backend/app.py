from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from models import PropertyData, RiskLevel, RiskFactor, RiskCategory, RiskAssessment
from risk_assessment import get_risk_assessment, get_risk_assessment_sync
from typing import Optional

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
async def assess_property(
    property_data: PropertyData,
    provider: Optional[str] = Query("openai", description="LLM provider to use (openai, anthropic)"),
    model_name: Optional[str] = Query(None, description="Specific model to use (default: 'gpt-3.5-turbo' for OpenAI, 'claude-2' for Anthropic)"),
    temperature: Optional[float] = Query(0.2, description="Temperature setting for the LLM (controls randomness)")
):
    # Use the async risk assessment function directly
    try:
        # Since we're in an async function, we can use the async version
        risk_assessment = await get_risk_assessment(property_data, provider, model_name, temperature)
        return risk_assessment
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating risk assessment: {str(e)}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)