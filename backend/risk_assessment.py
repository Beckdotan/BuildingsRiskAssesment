from langchain.llms import OpenAI, Anthropic
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
import json
import os
from dotenv import load_dotenv
from models import RiskLevel, RiskAssessment, RiskCategory, RiskFactor
from typing import Optional, Dict, Any, Union, List
import asyncio
import time
import concurrent.futures

# Load environment variables
load_dotenv()

# Define response schemas for structured category output
category_schema = ResponseSchema(
    name="risk_factors",
    description="""
    A list of risk factors for this category, where each risk factor must have exactly these fields:
    1. 'category' (string) - The specific aspect being assessed
    2. 'risk_level' (string) - Must be one of: 'No Risk', 'Low', 'Medium', or 'High'
    3. 'description' (string) - A detailed explanation of the risk
    
    Example:
    {
      "risk_factors": [
        {
          "category": "Building Age",
          "risk_level": "High",
          "description": "The property's 45-year age suggests significant concerns with electrical systems and plumbing infrastructure."
        },
        {
          "category": "Construction Type",
          "risk_level": "Medium",
          "description": "Wood frame construction presents moderate fire risks and potential maintenance issues."
        }
      ]
    }
    """
)

# Create category output parser
category_parser = StructuredOutputParser.from_response_schemas([category_schema])
category_format_instructions = category_parser.get_format_instructions()

def get_llm(provider="openai", model_name=None, temperature=0.2):
    """Initialize the language model based on provider."""
    provider = provider.lower()
    
    if provider == "openai":
        default_model = "gpt-3.5-turbo"
        selected_model = model_name or default_model
        return ChatOpenAI(temperature=temperature, model_name=selected_model)
    elif provider == "anthropic":
        default_model = "claude-2"
        return Anthropic(temperature=temperature, model=model_name or default_model)
    else:
        # Default to OpenAI if provider not recognized
        default_model = "gpt-3.5-turbo"
        return ChatOpenAI(temperature=temperature, model_name=model_name or default_model)

async def assess_property_category(property_data, category_name, llm):
    """Generate a risk assessment for a specific category."""
    
    # Define detailed prompt templates for each category
    templates = {
        "Property Assessment": """
            You are a professional property risk assessor specializing in multi-family properties. Analyze ONLY the PROPERTY ASSESSMENT risks of the given property and provide a detailed risk assessment.
            
            <property_info>
            Property Age: {property_age} years
            Number of Units: {number_of_units}
            Construction Type: {construction_type}
            Safety Features Present: {safety_features}
            Safety Features Missing: {missing_safety_features}
            </property_info>
            
            Guidelines for Property Assessment:
            1. Evaluate the property age:
               - Properties less than 10 years old typically have fewer structural issues
               - Properties 10-30 years old may have moderate maintenance needs
               - Properties over 30 years old often have higher risks related to electrical, plumbing, and structural systems
               
            2. Assess construction type risks:
               - Wood Frame: Higher fire risk, potential for termite damage, moderate durability
               - Brick: Good fire resistance, durability, but susceptible to mortar deterioration in older buildings
               - Concrete: Excellent fire resistance and durability, but can have water penetration issues
               - Steel Frame: Good structural integrity, fire-resistant when properly treated
               - Mixed Materials: Varied risks depending on combinations
            
            3. Analyze safety features:
               - Evaluate both present and missing safety features
               - Consider building code compliance implications
               - Assess impact on insurance costs and liability
            
            4. Evaluate by property size (units):
               - Smaller properties (2-4 units): Typically lower management complexity
               - Medium properties (5-20 units): Moderate management complexity
               - Large properties (20+ units): Higher complexity, more systems to maintain
            
            For EACH risk factor you identify, assign a risk level (No Risk, Low, Medium, or High) and provide a clear explanation.
            
            Return ONLY the risk factors for Property Assessment. Include at least 3-5 specific risk factors.
            
            {format_instructions}
        """,
        
        "Location Factors": """
            You are a professional location risk assessor specializing in multi-family properties. Analyze ONLY the LOCATION FACTORS risks of the given property and provide a detailed risk assessment.
            
            <property_info>
            Location: {location}
            Number of Units: {number_of_units}
            </property_info>
            
            Guidelines for Location Assessment:
            1. Natural disaster risks:
               - Research the location for potential flood zones
               - Assess earthquake, hurricane, tornado, or wildfire risks for the area
               - Consider regional climate change impacts
            
            2. Neighborhood factors:
               - Evaluate neighborhood safety and crime rates
               - Consider property values and market trends in the area
               - Assess infrastructure quality and proximity to amenities
            
            3. Regulatory environment:
               - Local housing regulations and compliance requirements
               - Zoning restrictions and development trends
               - Rent control or other regulatory considerations
            
            4. Economic factors:
               - Local employment rates and major employers
               - Economic stability of the region
               - Rental market supply and demand
            
            For EACH risk factor you identify, assign a risk level (No Risk, Low, Medium, or High) and provide a clear explanation.
            
            If the location is "Not specified", focus on general location risks associated with multi-family properties and assume a moderate risk level for most factors.
            
            Return ONLY the risk factors for Location Factors. Include at least 3-5 specific risk factors.
            
            {format_instructions}
        """,
        
        "Liability Risks": """
            You are a professional liability risk assessor specializing in multi-family properties. Analyze ONLY the LIABILITY RISKS of the given property and provide a detailed risk assessment.
            
            <property_info>
            Property Age: {property_age} years
            Number of Units: {number_of_units}
            Construction Type: {construction_type}
            Safety Features Present: {safety_features}
            Safety Features Missing: {missing_safety_features}
            Location: {location}
            </property_info>
            
            Guidelines for Liability Risk Assessment:
            1. Tenant safety considerations:
               - Evaluate how missing safety features impact tenant safety
               - Consider trip/fall hazards based on property age and type
               - Assess security risks based on available features
               - Evaluate fire safety risks based on construction and safety features
            
            2. Legal and regulatory compliance:
               - Building code compliance issues related to property age
               - ADA compliance considerations
               - Health and safety regulation requirements
               - Required disclosures based on property characteristics
            
            3. Insurance implications:
               - Factors that may increase insurance premiums
               - Potential coverage gaps based on property characteristics
               - Risk management considerations
            
            4. Specific liability concerns:
               - Environmental hazards possible for this age/type of property
               - Attractive nuisance concerns
               - Premises liability issues
            
            For EACH risk factor you identify, assign a risk level (No Risk, Low, Medium, or High) and provide a clear explanation.
            
            Pay particular attention to missing safety features and their liability implications.
            
            Return ONLY the risk factors for Liability Risks. Include at least 3-5 specific risk factors.
            
            {format_instructions}
        """
    }
    
    # Create the prompt with the appropriate template
    prompt = PromptTemplate(
        input_variables=["property_age", "number_of_units", "construction_type", 
                         "safety_features", "missing_safety_features", "location"],
        template=templates[category_name],
        partial_variables={"format_instructions": category_format_instructions}
    )
    
    # Create the LLM chain
    chain = LLMChain(llm=llm, prompt=prompt)
    
    # Prepare data for the prompt
    safety_features_str = ", ".join(property_data.safetyFeatures) if property_data.safetyFeatures else "None"
    missing_safety_features_str = ", ".join(property_data.missingSafetyFeatures) if property_data.missingSafetyFeatures else "None"
    location_str = property_data.location if property_data.location else "Not specified"
    
    # Run the chain
    try:
        # Using acall instead of arun for proper async execution
        result = await chain.acall({
            "property_age": property_data.propertyAge,
            "number_of_units": property_data.numberOfUnits,
            "construction_type": property_data.constructionType,
            "safety_features": safety_features_str,
            "missing_safety_features": missing_safety_features_str,
            "location": location_str
        })
        result = result.get("text", "")
        
        # Parse the result and extract risk factors
        parsed_result = category_parser.parse(result)
        
        # Validate risk factors
        for factor in parsed_result["risk_factors"]:
            if not all(k in factor for k in ["category", "risk_level", "description"]):
                raise ValueError(f"Missing required fields in risk factor for {category_name}")
        
        # Determine category risk level (highest of any risk factor)
        risk_levels = {"No Risk": 0, "Low": 1, "Medium": 2, "High": 3}
        highest_risk = 0
        
        for factor in parsed_result["risk_factors"]:
            factor_risk = risk_levels.get(factor["risk_level"], 0)
            highest_risk = max(highest_risk, factor_risk)
        
        category_risk_level = list(risk_levels.keys())[highest_risk]
        
        # Create and return the category
        return RiskCategory(
            category_name=category_name,
            category_risk_level=category_risk_level,
            risk_factors=parsed_result["risk_factors"]
        )
    except Exception as e:
        print(f"Error assessing {category_name}: {str(e)}")
        # Return a fallback category with error information
        return RiskCategory(
            category_name=category_name,
            category_risk_level="Medium",
            risk_factors=[{
                "category": f"Error in {category_name} Assessment",
                "risk_level": "Medium",
                "description": f"Unable to generate detailed assessment for this category. Error: {str(e)}"
            }]
        )

async def get_risk_assessment(property_data, provider="openai", model_name=None, temperature=0.2):
    """Generate a comprehensive risk assessment by running parallel assessments for each category."""
    # Initialize the language model
    llm = get_llm(provider, model_name, temperature)
    
    # Define the categories to assess
    categories = ["Property Assessment", "Location Factors", "Liability Risks"]
    
    # Run category assessments in parallel
    tasks = [assess_property_category(property_data, category, llm) for category in categories]
    category_results = await asyncio.gather(*tasks)
    
    # Determine overall risk level (highest of any category)
    risk_levels = {"No Risk": 0, "Low": 1, "Medium": 2, "High": 3}
    highest_risk = 0
    
    for category in category_results:
        category_risk = risk_levels.get(category.category_risk_level, 0)
        highest_risk = max(highest_risk, category_risk)
    
    overall_risk_level = list(risk_levels.keys())[highest_risk]
    
    # Create and return the complete risk assessment
    return {
        "overall_risk_level": overall_risk_level,
        "categories": category_results
    }

# For compatibility with both async and sync contexts
def get_risk_assessment_sync(property_data, provider="openai", model_name=None, temperature=0.2):
    """
    Synchronous wrapper for the async risk assessment function.
    This version works safely within FastAPI's existing event loop.
    """
    try:
        # Check if we're already in an event loop
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Create a new future in the running loop
            return asyncio.run_coroutine_threadsafe(
                get_risk_assessment(property_data, provider, model_name, temperature),
                loop
            ).result()
        else:
            # If no loop is running, use run_until_complete
            return loop.run_until_complete(
                get_risk_assessment(property_data, provider, model_name, temperature)
            )
    except RuntimeError:
        # If there's no event loop in this thread, create one
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                get_risk_assessment(property_data, provider, model_name, temperature)
            )
        finally:
            loop.close()