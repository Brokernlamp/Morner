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
            self.base_url = "/v1"
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
        
        system_prompt =  def get_search_blueprint(self, context):
        """Generates a multi-platform strategy based on firmographics."""
        
        system_prompt = f"""You are a B2B/B2C Lead Generation Architect.
The User (a Freelancer) is offering: {context['offering']}
Location: {context['location']}
Target Business/Client Size: {context['target_size']}
Decision Maker: {context['decision_maker']}

STRATEGIC OBJECTIVE:
Generate search queries that find POTENTIAL CUSTOMERS who need this service. 
DO NOT search for the service itself (which finds competitors). 
Search for the 'Demand Centers' or 'Buyer Personas'.

Examples:
- If offering 'Maid Services', search for: "Upscale residential societies", "Working professional hubs", "New parents community".
- If offering 'Web Dev', search for: "Local businesses with no website", "New startups".

TASK:
1. Define a 'Persona Summary' of the ideal BUYER.
2. Select 2 platforms: 'google_maps' and 'general_web'.
3. Generate 4 high-intent search queries that find where these BUYERS are located.

Return ONLY a JSON object:
{{
  "persona_summary": "string",
  "market_segment": "string",
  "tasks": {{
    "google_maps": ["query1", "query2", "query 3", "query4"],
    "general_web": ["query1", "query2", "query 3", "query4"],
    "linkedin": ["q1", "q2"],
    "indiamart": ["q1", "q2"],
    "sulekha": ["q1", "q2"]
  }},
  "platform_logic": "Why these queries will find CUSTOMERS and not COMPETITORS.",
  "lead_scoring_criteria": ["Criteria for a high-value buyer"]
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
