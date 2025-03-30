from prompts.base import BasePromptTemplate

class LiabilityRisksPrompt(BasePromptTemplate):
    """
    Prompt template for Liability Risks risk category.
    
    This template contains specialized prompts for evaluating liability-related risks
    such as tenant safety, legal compliance, insurance implications, and specific liability concerns.
    """
    
    def __init__(self):
        """
        Initialize the Liability Risks prompt template with predefined system and user prompts.
        """
        system_prompt = """
            You are a professional liability risk assessor specializing in multi-family properties. Analyze ONLY the LIABILITY RISKS of the given property and provide a detailed risk assessment.
            
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
        
        user_prompt_template = """
            <property_info>
            Property Age: {property_age} years
            Number of Units: {number_of_units}
            Construction Type: {construction_type}
            Safety Features Present: {safety_features}
            Safety Features Missing: {missing_safety_features}
            Location: {location}
            </property_info>
        """
        
        system_input_variables = ["format_instructions"]
        user_input_variables = ["property_age", "number_of_units", "construction_type", 
                              "safety_features", "missing_safety_features", "location"]
        
        super().__init__(system_prompt, user_prompt_template, 
                        system_input_variables, user_input_variables)