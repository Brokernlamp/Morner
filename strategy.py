import os
import json
import re
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class StrategyEngine:
    def __init__(self):
        # --- MASTER TOGGLE ---
        # Set to True to use your AWS EC2 (Llama 3)
        # Set to False to use OpenRouter (Gemini)
        self.use_aws = False

        if self.use_aws:
            # 🖥️ AWS EC2 Configuration
            self.base_url = "http://16.16.139.161:3000/v1"
            self.api_key = "not-needed"
            self.model_name = "llama3"
        else:
            # ☁️ OpenRouter Configuration
            self.base_url = "https://openrouter.ai/api/v1"
            self.api_key = os.getenv("OPENROUTER_KEY")
            self.model_name = "google/gemini-2.0-flash-lite-001"

        # Initialize the client with the selected settings
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

    def get_search_blueprint(self, context):
        """Generates a multi-platform strategy based on firmographics."""
        
        system_prompt = f"""You are a Lead Generation Architect. 
Analyze the following constraints for the Indian market:
- OFFERING: {context['offering']}
- LOCATION: {context['location']}
- TARGET SIZE: {context['target_size']}
- DECISION MAKER: {context['decision_maker']}

TASK:
1. Define a 'Persona Summary' for the lead.
2. Select 2-3 platforms (google_maps, justdial, indiamart, linkedin).
3. Generate search queries that specifically target the BUSINESS SIZE requested.

Return ONLY a JSON object:
{{
  "persona_summary": "string",
  "market_segment": "string",
  "tasks": {{
    "platform_name": ["query1", "query2"]
  }},
  "platform_logic": "string",
  "lead_scoring_criteria": ["What makes a lead 'High Quality' for this specific target?"]
}}"""

        try:
            # The model parameter now correctly pulls from self.model_name
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": system_prompt}],
                max_tokens=1000,
                temperature=0.2
            )
            
            raw_content = response.choices[0].message.content.strip()
            
            # Use regex to find the JSON block in case the model adds extra text
            json_match = re.search(r'\{.*\}', raw_content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            else:
                raise ValueError("AI failed to generate structural JSON.")

        except Exception as e:
            print(f"⚠️ Strategy Engine Error: {e}")
            return {"error": str(e)}