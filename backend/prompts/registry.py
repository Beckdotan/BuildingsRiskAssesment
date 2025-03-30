from typing import Dict, Optional
from prompts.base import BasePromptTemplate
from prompts.property_assessment import PropertyAssessmentPrompt
from prompts.location_factors import LocationFactorsPrompt
from prompts.liability_risks import LiabilityRisksPrompt

class PromptRegistry:
    """
    Singleton registry for managing prompt templates.
    
    This class provides a centralized way to access all prompt templates in the system.
    It follows the singleton pattern to ensure only one instance exists.
    
    Attributes:
        _instance (PromptRegistry): The singleton instance of the registry.
        _templates (Dict[str, BasePromptTemplate]): Dictionary mapping category names to template instances.
    """
    
    _instance = None
    
    def __init__(self):
        """
        Initialize the registry with all available prompt templates.
        
        This should only be called once through the get_instance() method.
        """
        self._templates = {
            "Property Assessment": PropertyAssessmentPrompt(),
            "Location Factors": LocationFactorsPrompt(),
            "Liability Risks": LiabilityRisksPrompt()
        }
    
    @classmethod
    def get_instance(cls) -> 'PromptRegistry':
        """
        Get the singleton instance of the registry.
        
        Returns:
            PromptRegistry: The singleton instance.
        """
        if cls._instance is None:
            cls._instance = PromptRegistry()
        return cls._instance
    
    def get_template(self, category: str) -> Optional[BasePromptTemplate]:
        """
        Get a prompt template for a specific category.
        
        Args:
            category (str): The category name to get a template for.
                Valid options are: "Property Assessment", "Location Factors", "Liability Risks".
        
        Returns:
            Optional[BasePromptTemplate]: The template for the specified category, or None if not found.
        """
        return self._templates.get(category)
    
    def get_all_categories(self) -> list:
        """
        Get a list of all available category names.
        
        Returns:
            list: List of category names as strings.
        """
        return list(self._templates.keys())