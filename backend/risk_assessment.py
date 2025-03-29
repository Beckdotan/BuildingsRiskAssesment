from langchain.llms import OpenAI, Anthropic
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
import json
import os
from dotenv import load_dotenv
from models import RiskLevel, RiskAssessment
from typing import Optional, Dict, Any, Union
import sys

# Load environment variables
load_dotenv()

# Define response schemas for structured output
response_schemas = [
    ResponseSchema(name="overall_risk_level", description="The overall risk level of the property: 'No Risk', 'Low', 'Medium', or 'High'"),
    ResponseSchema(name="categories", description="A list of risk categories, where each category must have exactly these fields: 'category_name' (string), 'category_risk_level' (one of: 'No Risk', 'Low', 'Medium', 'High'), and 'risk_factors' (array of objects where each object has exactly these fields: 'category' (string), 'risk_level' (one of: 'No Risk', 'Low', 'Medium', 'High'), and 'description' (string))")
]

output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
format_instructions = output_parser.get_format_instructions()

def get_risk_assessment(property_data, provider="openai", model_name=None, temperature=0.2):
    """Generate a risk assessment for a multi-family property using LangChain and LLM.
    
    Args:
        property_data: PropertyData object containing information about the property
        provider: LLM provider to use (openai, anthropic, cohere, huggingface)
        model_name: Specific model to use (defaults to provider-specific default if None)
        temperature: Temperature setting for the LLM (controls randomness)
        
    Returns:
        RiskAssessment object with overall risk level and categorized risk factors
    """
    # Initialize the language model based on provider
    provider = provider.lower()
    
    if provider == "openai":
        default_model = "gpt-3.5-turbo"
        selected_model = model_name or default_model
        llm = ChatOpenAI(temperature=temperature, model_name=selected_model)
    elif provider == "anthropic":
        default_model = "claude-2"
        llm = Anthropic(temperature=temperature, model=model_name or default_model)
    else:
        # Default to OpenAI if provider not recognized
        default_model = "gpt-3.5-turbo"
        llm = ChatOpenAI(temperature=temperature, model_name=model_name or default_model)
    
    # Create a prompt template
    template = """
    You are a professional risk assessor for multi-family properties. Analyze the following property information and provide a comprehensive risk assessment.
    
    Property Information:
    - Property Age: {property_age} years
    - Number of Units: {number_of_units}
    - Construction Type: {construction_type}
    - Safety Features: {safety_features}
    - Location: {location}
    
    Provide a detailed risk assessment with the following components:
    1. Overall risk level (No Risk, Low, Medium, or High)
    2. Risk categories including:
       - Property Assessment (building age, construction materials, safety features)
       - Location Factors (natural disasters, neighborhood safety)
       - Liability Risks (tenant safety, regulatory compliance)
    
    For each category, provide specific risk factors with their individual risk levels and descriptions.
    
    {format_instructions}
    """
    
    # Create the prompt with the template
    prompt = PromptTemplate(
        input_variables=["property_age", "number_of_units", "construction_type", "safety_features", "location"],
        template=template,
        partial_variables={"format_instructions": format_instructions}
    )
    
    # Create the LLM chain
    chain = LLMChain(llm=llm, prompt=prompt)
    
    # Run the chain
    safety_features_str = ", ".join(property_data.safetyFeatures) if property_data.safetyFeatures else "None"
    location_str = property_data.location if property_data.location else "Not specified"
    
    result = chain.run({
        "property_age": property_data.propertyAge,
        "number_of_units": property_data.numberOfUnits,
        "construction_type": property_data.constructionType,
        "safety_features": safety_features_str,
        "location": location_str
    })
    
    # Parse the result
    try:
        parsed_output = output_parser.parse(result)
        
        # Ensure all required fields are present
        if not all(k in parsed_output for k in ["overall_risk_level", "categories"]):
            raise ValueError("Missing required fields in LLM output")
            
        # Validate each category has required fields
        for category in parsed_output["categories"]:
            if not all(k in category for k in ["category_name", "category_risk_level", "risk_factors"]):
                raise ValueError("Missing required fields in category")
                
            # Validate each risk factor has required fields
            for factor in category["risk_factors"]:
                if not all(k in factor for k in ["category", "risk_level", "description"]):
                    raise ValueError("Missing required fields in risk factor")
        
        return parsed_output
    except Exception as e:
        # Fallback in case parsing fails
        print(f"Error parsing LLM output: {e}")
        print(f"Raw output: {result}")
        
        # Return a basic assessment as fallback with all required fields
        return {
            "overall_risk_level": "Medium",
            "categories": [
                {
                    "category_name": "Property Assessment",
                    "category_risk_level": "Medium",
                    "risk_factors": [
                        {
                            "category": "Error in Assessment",
                            "risk_level": "Medium",
                            "description": "Unable to generate detailed assessment. Please try again later."
                        }
                    ]
                }
            ]
        }