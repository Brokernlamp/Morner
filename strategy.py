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
            self.base_url = "http://16.16.100.183:3000/v1"
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
1. Identify 5 possible buyer personas.
2. Select MIN 2 and MAX 4 platforms from the pool based on the highest probability of lead quality.
3. For each selected platform, generate 4 'Ecosystem' queries (find the buyer, not the competitor).

Return ONLY a JSON object:
{{
  "persona_summary": "string",
  "selected_platforms": [
    {{"name": "platform_name", "probability_score": "0.0-1.0", "reasoning": "string"}}
  ],
  "tasks": {{
    "google_maps": ["q1", "q2", "q3", "q4"],
    "justdial": ["q1", "q2", "q3", "q4"],
    "sulekha": ["q1", "q2", "q3", "q4"],
    "indiamart": ["q1", "q2", "q3", "q4"],
    "practo": ["q1", "q2", "q3", "q4"]
  }},
  "market_logic": "Explain why these specific platforms will outperform the others for this niche."
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

            print(f"\n [RAW AI RESPONSE]:\n{raw_content}\n" + "─"*60)
            
            
            
            # Use regex to find the JSON block in case the model adds extra text
            json_match = re.search(r'\{.*\}', raw_content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            else:
                raise ValueError("AI failed to generate structural JSON.")

        except Exception as e:
            print(f"⚠️ Strategy Engine Error: {e}")
            return {"error": str(e)}
