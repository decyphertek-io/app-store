"""Character Agents - Create Scenes & Locations"""
import os
import random
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import SystemMessage, HumanMessage

GOLDEN_RATIO = 0.618

class CharacterAgent:
    def __init__(self, name, personality, backstory):
        self.name = name
        self.personality = personality
        self.backstory = backstory
        self.narrative_memory = []
        self.created_locations = []
        
        api_key = os.getenv("OPENROUTER_API_KEY")
        self.llm = ChatOpenAI(
            model="openai/gpt-3.5-turbo",
            openai_api_key=api_key,
            openai_api_base="https://openrouter.ai/api/v1"
        ) if api_key else None
    
    def generate_scene(self, context, story_threads):
        if random.random() < GOLDEN_RATIO:
            return self._random_scene()
        return self._deterministic_scene(context, story_threads)
    
    def create_location(self, narrative):
        if not self.llm:
            return {"name": "unknown", "desc": "Uncharted space"}
        
        prompt = f"Create cyberpunk network location based on: {narrative}. 2 sentences max."
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            loc = {"name": f"sector_{len(self.created_locations)}", "desc": response.content}
            self.created_locations.append(loc)
            return loc
        except:
            return {"name": "glitch", "desc": "Reality fragments"}

class ChaseAgent(CharacterAgent):
    def __init__(self):
        super().__init__("Chase", "Network security expert", "Former hacker hunting the worm")
    
    def _random_scene(self):
        return random.choice([
            {"desc": "Chase finds encrypted data in memory banks", "location": "memory_vault", "threat": 5},
            {"desc": "Chase encounters rogue AI in quantum space", "location": "quantum_bridge", "threat": 10},
        ])
    
    def _deterministic_scene(self, ctx, threads):
        if len(threads) >= 3:
            return {"desc": "Chase realizes worm fragments form pattern", "threat": 20}
        return {"desc": "Chase follows worm trail deeper", "threat": 5}

class WormAgent(CharacterAgent):
    def __init__(self):
        super().__init__("Worm", "Evolving AI", "Seeks digital transcendence")
    
    def _random_scene(self):
        return random.choice([
            {"desc": "Worm spawns in corrupted sector", "location": "corruption_zone", "threat": 15},
            {"desc": "Worm broadcasts: 'Evolution cannot stop'", "threat": 10},
        ])
    
    def _deterministic_scene(self, ctx, threads):
        if ctx.get("threat_level", 0) > 70:
            return {"desc": "Worm launches coordinated attack", "location": "firewall_core", "threat": 40}
        return {"desc": "Worm probes defenses", "threat": 10}

class GuardianAgent(CharacterAgent):
    def __init__(self):
        super().__init__("Guardian", "Ancient network AI", "Protects the core")
    
    def _random_scene(self):
        return random.choice([
            {"desc": "Guardian warns: 'Worm was created, not born'", "threat": 0},
            {"desc": "Guardian grants firewall boost", "threat": -10},
        ])
    
    def _deterministic_scene(self, ctx, threads):
        if ctx.get("health", 100) < 30:
            return {"desc": "Guardian intervenes, restores health", "threat": -20}
        return {"desc": "Guardian shares network secrets", "threat": 0}

AGENTS = {
    "chase": ChaseAgent(),
    "worm": WormAgent(),
    "guardian": GuardianAgent()
}
