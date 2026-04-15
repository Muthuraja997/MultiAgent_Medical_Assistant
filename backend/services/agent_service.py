"""
Agent Service

Business logic for agent orchestration and query processing.
"""

import sys
import os

# Add backend directory to path to import agents
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from agents.agent_decision import process_query as agent_process_query


class AgentService:
    """Service class for agent-related operations"""
    
    @staticmethod
    def process_text_query(query: str, conversation_history: list = None) -> dict:
        """
        Process a text query through the multi-agent system.
        
        Args:
            query: User's text query
            conversation_history: Optional conversation history
            
        Returns:
            dict: Response data from the agent system
        """
        try:
            response_data = agent_process_query(query)
            
            if 'messages' not in response_data or len(response_data['messages']) == 0:
                raise ValueError("No messages returned from agent")
            
            response_text = response_data['messages'][-1].content
            
            return {
                "status": "success",
                "response": response_text,
                "agent": response_data.get("agent_name", "UNKNOWN"),
                "full_data": response_data
            }
        except Exception as e:
            raise Exception(f"Agent processing error: {str(e)}")
    
    @staticmethod
    def process_image_query(image_path: str, text: str = "") -> dict:
        """
        Process an image query with optional text through the agent system.
        
        Args:
            image_path: Path to the uploaded image
            text: Optional text accompanying the image
            
        Returns:
            dict: Response data from the agent system
        """
        try:
            query = {"text": text, "image": image_path}
            response_data = agent_process_query(query)
            
            if 'messages' not in response_data or len(response_data['messages']) == 0:
                raise ValueError("No messages returned from agent")
            
            response_text = response_data['messages'][-1].content
            
            result = {
                "status": "success",
                "response": response_text,
                "agent": response_data.get("agent_name", "UNKNOWN"),
                "full_data": response_data
            }
            
            # Check for skin lesion segmentation output
            if response_data.get("agent_name") == "SKIN_LESION_AGENT, HUMAN_VALIDATION":
                segmentation_path = "../common/uploads/skin_lesion_output/segmentation_plot.png"
                if os.path.exists(segmentation_path):
                    result["result_image"] = f"/{segmentation_path}"
            
            return result
        except Exception as e:
            raise Exception(f"Image processing error: {str(e)}")
    
    @staticmethod
    def process_validation(validation_result: str, comments: str = None) -> dict:
        """
        Process human validation for medical AI outputs.
        
        Args:
            validation_result: Yes/No validation result
            comments: Optional validation comments
            
        Returns:
            dict: Validation response
        """
        try:
            # Graph guardrails expect the literal reply to start with Yes/No (see apply_output_guardrails).
            vr = (validation_result or "").strip()
            vl = vr.lower()
            if vl == "yes" or vl.startswith("yes "):
                validation_query = "Yes"
            elif vl == "no" or vl.startswith("no "):
                validation_query = "No"
            else:
                validation_query = vr
            if comments:
                validation_query = f"{validation_query}\nComments: {comments}"

            response_data = agent_process_query(validation_query)
            response_text = response_data['messages'][-1].content

            confirmed = vl == "yes" or vl.startswith("yes ")
            if confirmed:
                return {
                    "status": "validated",
                    "message": "**Output confirmed by human validator:**",
                    "response": response_text
                }
            return {
                "status": "rejected",
                "comments": comments,
                "message": "**Output requires further review:**",
                "response": response_text
            }
        except Exception as e:
            raise Exception(f"Validation processing error: {str(e)}")
