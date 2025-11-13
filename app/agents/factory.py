from typing import Dict, Any, Optional
from groq import Groq
from app.core.config import settings
from app.models.agent import Agent, AgentType
from app.agents.templates import get_template

class AgentFactory:
    def __init__(self):
        self.groq_client = Groq(api_key=settings.GROQ_API_KEY)
    
    def create_agent_config(self, task_description: str) -> Dict[str, Any]:
        analysis_prompt = f"""Analyze this task and determine the best agent type to handle it:

Task: {task_description}

Available agent types:
- RESEARCHER: For research, information gathering, and analysis tasks
- CODER: For programming, software development, and technical tasks
- ANALYST: For data analysis, statistics, and insights
- WRITER: For content creation, copywriting, and editing
- MARKETER: For marketing strategy, campaigns, and promotional content
- DEBUGGER: For finding and fixing bugs, troubleshooting issues
- REVIEWER: For code review, quality assurance, and feedback
- CUSTOM: For tasks that don't fit other categories

Respond with a JSON object:
{{
    "agent_type": "TYPE",
    "reasoning": "why this type fits",
    "suggested_name": "descriptive name",
    "description": "what this agent will do",
    "custom_prompt_additions": "any additional context for the system prompt"
}}"""

        response = self.groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are an AI agent architect. Analyze tasks and recommend optimal agent configurations. Always respond with valid JSON."},
                {"role": "user", "content": analysis_prompt}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        
        result_text = response.choices[0].message.content.strip()
        
        import json
        try:
            result = json.loads(result_text)
        except json.JSONDecodeError:
            start = result_text.find('{')
            end = result_text.rfind('}') + 1
            if start != -1 and end > start:
                result = json.loads(result_text[start:end])
            else:
                result = {
                    "agent_type": "CUSTOM",
                    "reasoning": "Unable to parse recommendation",
                    "suggested_name": "Custom Agent",
                    "description": task_description,
                    "custom_prompt_additions": ""
                }
        
        return result
    
    def build_agent_from_config(self, config: Dict[str, Any], task_description: str) -> Dict[str, Any]:
        agent_type_str = config.get("agent_type", "CUSTOM").upper()
        try:
            agent_type = AgentType[agent_type_str]
        except KeyError:
            agent_type = AgentType.CUSTOM
        
        template = get_template(agent_type)
        
        system_prompt = template["system_prompt"]
        if config.get("custom_prompt_additions"):
            system_prompt += f"\n\nAdditional Context:\n{config['custom_prompt_additions']}"
        
        system_prompt += f"\n\nCurrent Task Focus: {task_description}"
        
        return {
            "name": config.get("suggested_name", f"{agent_type.value.title()} Agent"),
            "agent_type": agent_type,
            "description": config.get("description", task_description),
            "system_prompt": system_prompt,
            "capabilities": template["capabilities"],
            "temperature": template["temperature"],
            "max_tokens": template["max_tokens"],
            "model": "llama-3.3-70b-versatile",
            "agent_metadata": {
                "created_from_task": task_description,
                "reasoning": config.get("reasoning", "")
            }
        }
    
    def execute_with_agent(self, agent: Agent, input_data: str) -> str:
        messages = [
            {"role": "system", "content": agent.system_prompt},
            {"role": "user", "content": input_data}
        ]
        
        response = self.groq_client.chat.completions.create(
            model=agent.model,
            messages=messages,
            temperature=float(agent.temperature),
            max_tokens=int(agent.max_tokens)
        )
        
        return response.choices[0].message.content

agent_factory = AgentFactory()
