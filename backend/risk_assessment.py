from langchain.llms import OpenAI, Anthropic
from langchain.prompts import PromptTemplate, ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
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
from prompts.registry import PromptRegistry

# Load environment variables
load_dotenv()

# Define response schemas for structured category output
category_schema = ResponseSchema(
    name="risk_factors",
    description="""
    Format Specification:
    A list of risk factors for this category. Each risk factor must contain exactly these fields:
    1. 'category' (string) - The specific aspect being assessed (e.g., Building Age, Construction Type)
    2. 'risk_level' (string) - Must be one of: 'No Risk', 'Low', 'Medium', or 'High'
    3. 'description' (string) - A detailed explanation of why this aspect presents the specified risk level
    
    Example Response:
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
    """
    Generate a risk assessment for a specific category of property risk.
    
    This asynchronous function evaluates property data for a given risk category using an LLM.
    It creates a structured risk assessment with multiple risk factors and an average risk level.
    
    Parameters:
        property_data (PropertyData): Pydantic model containing property information such as age,
            number of units, construction type, safety features, and location.
        category_name (str): The risk category to assess. Options include:
            - "Property Assessment"
            - "Location Factors"
            - "Liability Risks"
        llm (LLM): Language model instance to use for generating the assessment.
            
    Returns:
        RiskCategory: A structured assessment containing:
            - category_name (str): The category being assessed
            - category_risk_level (RiskLevel): The average risk level for the category
            - risk_factors (List[RiskFactor]): Individual risk factors with descriptions
            
    Notes:
        - Each category uses a specialized prompt that guides the LLM to analyze specific aspects
        - Risk level for each category is calculated as the average of all risk factors
        - Risk levels are mapped from "No Risk", "Low", "Medium", to "High"
        - Includes error handling to return a fallback assessment if processing fails
        
    Examples:
        >>> llm = get_llm("openai")
        >>> category = await assess_property_category(property_data, "Property Assessment", llm)
        >>> print(category.category_risk_level)
    """
    
    # Get the prompt template from the registry
    prompt_registry = PromptRegistry.get_instance()
    prompt_template = prompt_registry.get_template(category_name)
    
    if not prompt_template:
        raise ValueError(f"No prompt template found for category: {category_name}")
    
    # Get system and user prompts from the template
    system_prompt = prompt_template.get_system_prompt()
    user_prompt = prompt_template.get_user_prompt_template()
    system_input_vars = prompt_template.get_input_variables()['system']
    user_input_vars = prompt_template.get_input_variables()['user']
    
    # Create a ChatPromptTemplate with separate system and user messages
    system_message_prompt = SystemMessagePromptTemplate.from_template(
        system_prompt,
        input_variables=system_input_vars
    )
    
    human_message_prompt = HumanMessagePromptTemplate.from_template(
        user_prompt,
        input_variables=user_input_vars
    )
    
    # Combine the system and human messages into a chat prompt template
    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
    
    # Create the LLM chain with the chat prompt
    chain = LLMChain(llm=llm, prompt=chat_prompt)
    
    # Prepare data for the prompt
    safety_features_str = ", ".join(property_data.safetyFeatures) if property_data.safetyFeatures else "None"
    missing_safety_features_str = ", ".join(property_data.missingSafetyFeatures) if property_data.missingSafetyFeatures else "None"
    location_str = property_data.location if property_data.location else "Not specified"
    
    # Run the chain
    try:
        # Using acall instead of arun for proper async execution
        # Create a base input data dictionary with all possible fields
        input_data = {
            "property_age": property_data.propertyAge,
            "number_of_units": property_data.numberOfUnits,
            "construction_type": property_data.constructionType,
            "safety_features": safety_features_str,
            "missing_safety_features": missing_safety_features_str,
            "location": location_str,
            "format_instructions": category_format_instructions
        }
        
        # The prompt template will automatically use only the variables it needs
            
        result = await chain.acall(input_data)
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
        
           # Calculate average risk level for the category
        total_risk = 0
        factor_count = len(parsed_result["risk_factors"])
        
        for factor in parsed_result["risk_factors"]:
            factor_risk = risk_levels.get(factor["risk_level"], 0)
            total_risk += factor_risk
        
        # Calculate average and round to nearest integer
        avg_risk = round(total_risk / factor_count) if factor_count > 0 else 0
        
        # Map the average risk back to a risk level string
        category_risk_level = list(risk_levels.keys())[avg_risk]
        
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
    """
    Generate a comprehensive multi-category risk assessment for a property.
    
    This asynchronous function coordinates parallel assessments across multiple risk categories
    and calculates an overall risk level based on the average of all category levels.
    
    Parameters:
        property_data (PropertyData): Pydantic model containing property information such as age,
            number of units, construction type, safety features, and location.
        provider (str): The LLM provider to use. Options include "openai" or "anthropic".
            Defaults to "openai".
        model_name (str, optional): The specific model to use.
            If None, defaults to provider-specific defaults.
        temperature (float): Controls the randomness of the output.
            Defaults to 0.2 for more consistent results.
            
    Returns:
        dict: A complete risk assessment containing:
            - overall_risk_level (str): Average risk level across all categories
            - categories (List[RiskCategory]): Individual category assessments
            
    Notes:
        - Runs category assessments in parallel for faster processing
        - Calculates overall risk as the average of all category risks
        - Risk levels are rounded to the nearest level: "No Risk", "Low", "Medium", or "High"
        
    Examples:
        >>> assessment = await get_risk_assessment(property_data)
        >>> print(assessment["overall_risk_level"])
        >>> for category in assessment["categories"]:
        >>>     print(f"{category.category_name}: {category.category_risk_level}")
    """
    # Initialize the language model
    llm = get_llm(provider, model_name, temperature)
    
    # Define the categories to assess
    categories = ["Property Assessment", "Location Factors", "Liability Risks"]
    
    # Run category assessments in parallel
    tasks = [assess_property_category(property_data, category, llm) for category in categories]
    category_results = await asyncio.gather(*tasks)
    
    # Define risk levels mapping
    risk_levels = {"No Risk": 0, "Low": 1, "Medium": 2, "High": 3}
    
    # Calculate average risk level
    total_risk = 0
    category_count = len(category_results)
    
    for category in category_results:
        category_risk = risk_levels.get(category.category_risk_level, 0)
        total_risk += category_risk
    
    # Calculate average and round to nearest integer
    avg_risk = round(total_risk / category_count) if category_count > 0 else 0
    
    # Map the average risk back to a risk level string
    overall_risk_level = list(risk_levels.keys())[avg_risk]
    
    print(""" avg Risk {avg_risk}, Category Count {category_count}""")
    # Create and return the complete risk assessment
    return {
        "overall_risk_level": overall_risk_level,
        "categories": category_results
    }


