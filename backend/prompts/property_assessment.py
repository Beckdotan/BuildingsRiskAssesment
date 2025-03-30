from prompts.base import BasePromptTemplate

class PropertyAssessmentPrompt(BasePromptTemplate):
    """
    Prompt template for Property Assessment risk category.
    
    This template contains specialized prompts for evaluating property-related risks
    such as building age, construction type, safety features, and property size.
    """
    
    def __init__(self):
        """
        Initialize the Property Assessment prompt template with predefined system and user prompts.
        """
        system_prompt = """
            You are a professional property risk assessor specializing in multi-family properties. Analyze ONLY the PROPERTY ASSESSMENT risks of the given property and provide a detailed risk assessment.
            
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
        """
        
        user_prompt_template = """
            <property_info>
            Property Age: {property_age} years
            Number of Units: {number_of_units}
            Construction Type: {construction_type}
            Safety Features Present: {safety_features}
            Safety Features Missing: {missing_safety_features}
            </property_info>
        """
        
        system_input_variables = ["format_instructions"]
        user_input_variables = ["property_age", "number_of_units", "construction_type", 
                              "safety_features", "missing_safety_features"]
        
        super().__init__(system_prompt, user_prompt_template, 
                        system_input_variables, user_input_variables)