"""
Service client executing LLM chat assistance, translation steps, and response plan drafts.
"""
import json
import logging
import httpx
from typing import List, Dict, Optional
from app.config import settings
from app.services.rag_store import search_rag

logger = logging.getLogger(__name__)

# Simulated fallback answers for robust offline validation
MOCK_RESPONSES = {
    "fan": {
        "hello": "Hello! Welcome to MetLife Stadium, your host venue for the FIFA World Cup 2026. How can I help you enjoy your match experience today? I can help with gate wait times, NJ transit train schedules, clear bag policies, and restroom/elevator locations.",
        "bag": "MetLife Stadium has a strict clear bag policy. All bags must be clear plastic, vinyl, or PVC, and not exceed 12in x 6in x 12in. You are also allowed a small clutch bag (4.5in x 6.5in). Prohibited items include umbrellas, selfie sticks, and banners larger than 3x5 feet.",
        "train": "To get back to Secaucus Junction, please use the NJ Transit Meadowlands Rail Line. Trains start running 3.5 hours before kickoff and continue running up to 2 hours after the match ends. We highly recommend buying round-trip tickets now via the NJ Transit App to avoid post-game queues.",
        "wheelchair": "MetLife Stadium offers fully accessible wheelchair seating on all levels. Accessible sections are located in Section 109, 124, 143, 201, 224, 317, and 335. Elevators are accessible near Gates A, C, and D. You can also pick up assistive listening devices or sensory bags at Guest Services (Section 124).",
        "concession": "Concession stands are located throughout all concourses. We feature localized international food options in sections 117, 142, 220, and 316. In line with our World Cup sustainability goals, all cups are 100% compostable and can be discarded in the Green Compost bins.",
        "recycle": "For sustainability at MetLife, please discard aluminum cans and plastic bottles in the Blue Recycle bins. Food scraps, napkins, and plastic cups belong in the Green Compost bins. Everything else goes into Gray Landfill bins. You can earn points for scanning the QR code on the bins!",
        "default": "Welcome to MetLife Stadium for FIFA World Cup 2026. Based on stadium regulations, clear bags only are permitted. NJ Transit Meadowlands Rail provides direct train service. For accessibility services, please check Guest Services at Section 124. Feel free to ask about gate congestion, recycling, or concessions!"
    },
    "volunteer": {
        "hello": "Volunteer Coordinator AI active. Welcome to your shift! Let's ensure a secure and smooth tournament experience. Let me know if you need instructions on crowd control, accessibility escorts, or reporting an incident.",
        "shift": "Volunteer shifts start 4 hours prior to kickoff. Ensure you check-in at the Volunteer Hub in Lot C, grab your neon green vest, and receive your sector assignment. Remember to take a 30-minute break in the Volunteer Rest Zone behind Section 136.",
        "incident": "To report an operational incident, please use the Organizer Command Center tab or alert the nearest venue coordinator using intercom extension 2026. Provide the exact location (gate/section) and severity.",
        "default": "Volunteer operations support: Shift check-ins are located at Lot C Volunteer Hub. Ensure you wear your neon green vest at all times. Use the intercom *55 or dial extension 2026 to report emergency incidents immediately."
    },
    "organizer": {
        "hello": "Operations Intelligence Copilot active. Monitoring gate congestions, incident queues, and utility status. How can I assist you with resource reallocation or public safety announcements?",
        "default": "Operations Intelligence command mode: Use the incident manager below to log gate issues, medical requests, or waste overflows. I can draft multi-language emergency statements and dispatch volunteers instantly."
    }
}

class GroqService:
    """
    Main service executing the multi-agent LLM reasoning loops via Groq API client
    or simulating intelligence response patterns locally.
    """
    def __init__(self):
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.api_key = settings.GROQ_API_KEY
        self.model = settings.GROQ_MODEL
        self.is_active = bool(self.api_key)
        self.response_cache = {}
        
        if self.is_active:
            logger.info(f"Groq Service active using model {self.model}.")
        else:
            logger.warning("No GROQ_API_KEY found. Running in Mock Groq Agent Simulation Mode.")

    def _call_groq_api(self, messages: List[Dict], temperature: float = 0.3) -> str:
        """Helper to invoke Groq API using HTTP client."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature
        }
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.post(self.api_url, headers=headers, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    logger.error(f"Groq API returned error {response.status_code}: {response.text}")
        except Exception as e:
            logger.error(f"Error calling Groq API: {e}")
        return ""

    # Multi-Agent Coordination pipeline
    def get_assistant_response(self, role: str, query: str, history: List[Dict], language: str) -> Dict:
        """
        Coordinates AI Assistant Agent and Translation Agent to output localized responses.
        Uses a local cache memory to avoid duplicate external API queries.
        """
        import time
        history_tuple = tuple((h.get("role", ""), h.get("content", "")) for h in history)
        cache_key = (role, query.strip().lower(), history_tuple, language)
        now = time.time()
        
        if cache_key in self.response_cache:
            cached_result, timestamp = self.response_cache[cache_key]
            if now - timestamp < 300:
                logger.info("High-speed Cache HIT for assistant response.")
                return cached_result

        # Step 1: Search RAG grounding store
        rag_context = search_rag(query)
        
        # Define base suggestions for follow-ups
        suggested_actions = self._generate_suggested_actions(role, query)
        
        if not self.is_active:
            # Fallback mock mode
            raw_response = self._get_mock_fallback_response(role, query, rag_context)
            localized_response = self._mock_translate(raw_response, language)
            result = {
                "response": localized_response,
                "detected_language": language,
                "suggested_actions": suggested_actions
            }
            self.response_cache[cache_key] = (result, now)
            return result

        # --- Multi-Agent Execution (Live Groq API) ---
        try:
            # 1. AI Assistant Agent Prompting (Generates content reasoning in English for consistency)
            assistant_system_prompt = (
                f"You are the 'AI Assistant Agent' for MetLife Stadium at the FIFA World Cup 2026. Your role is: '{role.upper()}'.\n"
                f"Ground your responses strictly in the provided RAG Context. If the context does not contain the answer, "
                f"responsibly state that you lack specific details but offer general stadium navigation support.\n"
                f"Write your response in English.\n\n"
                f"ROLE SPECIFICS:\n"
                f"- FAN: Friendly, welcoming, focuses on ticketing, transit, ADA navigation, clear bag limits, restrooms.\n"
                f"- VOLUNTEER: Supportive, clear, operations-oriented, coordinates check-ins, safety procedures.\n"
                f"- ORGANIZER: Strategy-focused, brief data-driven reports.\n\n"
                f"RAG CONTEXT:\n{rag_context}\n"
            )
            
            # Format messages payload
            messages = [{"role": "system", "content": assistant_system_prompt}]
            for msg in history:
                messages.append({
                    "role": "user" if msg["role"] == "user" else "assistant",
                    "content": msg["content"]
                })
            messages.append({"role": "user", "content": query})
            
            # Call Assistant Agent
            assistant_output = self._call_groq_api(messages, temperature=0.3)
            
            if not assistant_output:
                raise Exception("Assistant Agent returned empty response.")
                
            # 2. Translation Agent Prompting (Translates output into requested language)
            if language == "en":
                # Already in requested language
                result = {
                    "response": assistant_output,
                    "detected_language": language,
                    "suggested_actions": suggested_actions
                }
                self.response_cache[cache_key] = (result, now)
                return result
                
            translation_system_prompt = (
                f"You are the 'Translation Agent' for MetLife Stadium at the FIFA World Cup 2026.\n"
                f"Your task is to take the response generated by the AI Assistant Agent and translate it fully and accurately "
                f"into the requested target language: '{language}' (use 'es' for Spanish, 'fr' for French).\n"
                f"Do not add any introductory text, warnings, notes, or commentary. Only output the direct translation."
            )
            
            translation_messages = [
                {"role": "system", "content": translation_system_prompt},
                {"role": "user", "content": f"Translate the following text:\n{assistant_output}"}
            ]
            
            translated_output = self._call_groq_api(translation_messages, temperature=0.1)
            
            if not translated_output:
                # Return original assistant output if translation agent fails
                translated_output = f"[Translation unavailable] {assistant_output}"
                
            result = {
                "response": translated_output,
                "detected_language": language,
                "suggested_actions": suggested_actions
            }
            self.response_cache[cache_key] = (result, now)
            return result
            
        except Exception as e:
            logger.error(f"Error in multi-agent pipeline: {e}. Falling back to simulation.")
            raw_response = self._get_mock_fallback_response(role, query, rag_context)
            localized_response = self._mock_translate(raw_response, language)
            result = {
                "response": localized_response,
                "detected_language": language,
                "suggested_actions": suggested_actions
            }
            self.response_cache[cache_key] = (result, now)
            return result

    def generate_incident_response_plan(self, incident: Dict) -> Dict:
        """
        Drafts resolution plans, multilingual alerts, and volunteer actions using Groq API.
        """
        title = incident["title"]
        description = incident["description"]
        zone = incident["zone"]
        severity = incident["severity"]
        
        prompt = (
            f"Generate an Operations Resolution Plan for the following incident at FIFA 2026:\n"
            f"Title: {title}\n"
            f"Location/Zone: {zone}\n"
            f"Severity: {severity}\n"
            f"Description: {description}\n\n"
            f"Format the output strictly as a valid JSON object with these exact keys:\n"
            f"- 'response_plan': Detailed step-by-step resolution strategy for venue staff.\n"
            f"- 'announcements': A dictionary with keys 'en', 'es', and 'fr', containing clear public safety announcements.\n"
            f"- 'assigned_tasks': A list of 3 specific tasks to immediately assign to volunteers.\n"
            f"Do not output any introductory or summary text. Output only the JSON object."
        )
        
        if self.is_active:
            try:
                messages = [
                    {"role": "system", "content": "You are a JSON-generating venue safety assistant. Only return valid JSON."},
                    {"role": "user", "content": prompt}
                ]
                response_text = self._call_groq_api(messages, temperature=0.2)
                
                # Sanitize markdown wrapper codeblocks if present
                clean_text = response_text.strip()
                if clean_text.startswith("```"):
                    # Find start and end indices
                    start = clean_text.find("{")
                    end = clean_text.rfind("}")
                    if start != -1 and end != -1:
                        clean_text = clean_text[start:end+1]
                        
                parsed_json = json.loads(clean_text)
                return parsed_json
            except Exception as e:
                logger.error(f"Failed to generate structured plan from Groq: {e}. Fallback to mock.")
                
        # --- Mock Fallback Resolution ---
        if severity == "High":
            plan = f"Deploy Venue Emergency Response Team to {zone} immediately. Coordinate with local law enforcement/security. Establish safety cordon and route pedestrian traffic away from the bottleneck."
            tasks = [
                f"Assist with pedestrian crowd redirection 50 meters away from {zone}.",
                f"Hand out water bottles to fans waiting in the congested zone.",
                f"Verify scanner statuses and report hardware conditions to Volunteer Hub."
            ]
            announcements = {
                "en": f"Attention Fans: We are experiencing ticket scanner delays at {zone}. Please follow volunteer directions and consider using Gate A or Gate D for quicker entry.",
                "es": f"Atención Aficionados: Estamos experimentando retrasos en el escáner de boletos en {zone}. Por favor siga las instrucciones de los voluntarios y use la Puerta A o D.",
                "fr": f"Attention Supporters : Des retards de scanner sont signalés à {zone}. Veuillez suivre les consignes des bénévoles et utiliser la porte A ou D."
            }
        else:
            plan = f"Dispatch local supervisor to {zone}. Assess materials list, guide guests to alternative lanes, and update Command Center when resolved."
            tasks = [
                f"Coordinate visual checks and maintain clear passageways near {zone}.",
                f"Assist families and guests requiring ADA navigation to bypass the area.",
                f"Provide directions to the nearest working facilities."
            ]
            announcements = {
                "en": f"Operations notice: Service alert near {zone}. Please exercise caution in the area. Restrooms and guest services remain available in adjacent sectors.",
                "es": f"Aviso de operaciones: Alerta de servicio cerca de {zone}. Por favor transite con precaución en la zona.",
                "fr": f"Avis d'exploitation : Alerte de service près de {zone}. Veuillez circuler avec prudence dans cette zone."
            }
            
        return {
            "response_plan": plan,
            "announcements": announcements,
            "assigned_tasks": tasks
        }

    def analyze_waste_item(self, item_id: str) -> Dict:
        """
        Classifies waste category using local knowledge mapping (High efficiency).
        """
        categories = {
            "plastic_bottle": {
                "item_name": "Aluminum Can / Plastic Beverage Bottle",
                "target_bin": "Recycle (Blue Bin)",
                "co2_saved_kg": 0.08,
                "points_awarded": 15,
                "sorting_instruction": "Empty all remaining liquids out of the container first. Drop the plastic bottle or aluminum can directly into the Blue Recycle bin.",
                "sustainability_tip": "Recycling a single plastic bottle saves enough energy to power a stadium scoreboard for 15 seconds!"
            },
            "food_waste": {
                "item_name": "Hotdog / Nacho Food Remains",
                "target_bin": "Compost (Green Bin)",
                "co2_saved_kg": 0.15,
                "points_awarded": 25,
                "sorting_instruction": "Ensure all wrappers or plastic foils are removed. Toss food scraps, napkins, and compostable plates directly into the Green Compost bin.",
                "sustainability_tip": "MetLife Stadium composts organic waste locally, returning nutrient-rich soils back to regional community farms!"
            },
            "compostable_cup": {
                "item_name": "FIFA Official Souvenir Cup",
                "target_bin": "Compost (Green Bin)",
                "co2_saved_kg": 0.10,
                "points_awarded": 20,
                "sorting_instruction": "These souvenir cups are specifically manufactured from plant-based PLA and are 100% compostable. Dispose of them in the Green Compost bin.",
                "sustainability_tip": "Using plant-based cups reduces raw plastic production demands by 60% compared to traditional cups."
            },
            "cardboard_tray": {
                "item_name": "Food Carrying Cardboard Tray",
                "target_bin": "Recycle (Blue Bin)",
                "co2_saved_kg": 0.05,
                "points_awarded": 10,
                "sorting_instruction": "Remove any leftover food scraps (which go to Compost), flatten the clean cardboard tray, and slide it into the Blue Recycle container.",
                "sustainability_tip": "MetLife recycling loops cardboard back into clean structural packaging materials within 60 days."
            },
            "styrofoam_cup": {
                "item_name": "Coffee Styrofoam Cup / Plastic Wrap",
                "target_bin": "Landfill (Gray Bin)",
                "co2_saved_kg": 0.00,
                "points_awarded": 2,
                "sorting_instruction": "Styrofoam is non-recyclable and non-compostable in standard facilities. Place the container inside the Gray Landfill bin.",
                "sustainability_tip": "Avoid styrofoam when possible! Purchase hot drinks in compostable paper cups to reduce landfill dependency."
            }
        }
        return categories.get(item_id, categories["styrofoam_cup"])

    def _get_mock_fallback_response(self, role: str, query: str, rag_context: str) -> str:
        """Helper to match keywords inside static mock database."""
        query_lower = query.lower()
        role_responses = MOCK_RESPONSES.get(role, MOCK_RESPONSES["fan"])
        matched_content = ""
        for key in role_responses.keys():
            if key in query_lower:
                matched_content = role_responses[key]
                break
        if not matched_content:
            matched_content = role_responses["default"]
            snippet = rag_context.split("\n\n")[0]
            matched_content = f"{matched_content}\n\n[Grounded Info]: {snippet}"
        return matched_content

    def _mock_translate(self, content: str, language: str) -> str:
        """Helper to simulate translation for mock response."""
        if language == "es":
            return f"[Es - Versión traducida]: {content}\n(Nota: Respuesta multilingüe simulada por el Agente de Traducción de Groq)."
        elif language == "fr":
            return f"[Fr - Version traduite]: {content}\n(Note: Réponse multilingue simulée par l'Agent de Traduction de Groq)."
        return content

    def _generate_suggested_actions(self, role: str, query: str) -> List[str]:
        """Helper to generate contextual role action tags."""
        if role == "fan":
            return ["Find Wheelchair / ADA routes", "NJ Transit train schedule", "View recycling points leaderboard"]
        elif role == "volunteer":
            return ["Where is the Volunteer Hub?", "Report emergency incident", "Volunteer safety guidelines"]
        else:
            return ["Refresh Gate Congestion Map", "Create new Incident Alert", "Generate crowd operations report"]

groq_service = GroqService()
