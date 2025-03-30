from typing import Dict, Any

class BasePromptTemplate:
    """
    Base class for all prompt templates in the system.
    
    This class stores system_prompt and user_prompt_template without handling formatting.
    LangChain will handle the formatting of these templates.
    
    Attributes:
        system_prompt (str): The system prompt template string.
        user_prompt_template (str): The user prompt template string.
        input_variables (Dict[str, list]): Dictionary mapping 'system' and 'user' to their required input variables.
    """
    
    def __init__(self, system_prompt: str, user_prompt_template: str, 
                 system_input_variables: list = None, user_input_variables: list = None):
        """
        Initialize a new BasePromptTemplate.
        
        Args:
            system_prompt (str): The system prompt template string.
            user_prompt_template (str): The user prompt template string.
            system_input_variables (list, optional): List of variables required by the system prompt.
            user_input_variables (list, optional): List of variables required by the user prompt.
        """
        self.system_prompt = system_prompt
        self.user_prompt_template = user_prompt_template
        self.input_variables = {
            'system': system_input_variables or [],
            'user': user_input_variables or []
        }
    
    def get_system_prompt(self) -> str:
        """
        Get the system prompt template.
        
        Returns:
            str: The system prompt template string.
        """
        return self.system_prompt
    
    def get_user_prompt_template(self) -> str:
        """
        Get the user prompt template.
        
        Returns:
            str: The user prompt template string.
        """
        return self.user_prompt_template
    
    def get_input_variables(self) -> Dict[str, list]:
        """
        Get the input variables required by this template.
        
        Returns:
            Dict[str, list]: Dictionary mapping 'system' and 'user' to their required input variables.
        """
        return self.input_variables