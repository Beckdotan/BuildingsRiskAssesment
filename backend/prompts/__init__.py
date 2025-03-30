# This file makes the prompts directory a Python package
# It allows importing modules from this directory using the 'prompts' namespace

from prompts.registry import PromptRegistry
from prompts.base import BasePromptTemplate
from prompts.property_assessment import PropertyAssessmentPrompt
from prompts.location_factors import LocationFactorsPrompt
from prompts.liability_risks import LiabilityRisksPrompt

__all__ = [
    'PromptRegistry',
    'BasePromptTemplate',
    'PropertyAssessmentPrompt',
    'LocationFactorsPrompt',
    'LiabilityRisksPrompt'
]