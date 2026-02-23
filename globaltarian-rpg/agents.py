"""LangChain AI Character Agents for GLOBALTARIAN - Fractal Storytelling"""
import os
import random
from typing import Dict, List
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import SystemMessage, HumanMessage

GOLDEN_RATIO = 0.618  # 62% random, 38% deterministic

class CharacterAgent:
    def __init__(self, name: str, personality: str, backstory: str):
        self.name = name
        self.personality = personality
        self.backstory = backstory
        self.narrative_memory = []  # Tracks story threads
        self.created_locations = []
        
        api_key = os.getenv("OPENROUTER_API_KEY")
        self.llm = ChatOpenAI(
            model="openai/gpt-3.5-turbo",
            openai_api_key=api_key,
            openai_api_base="https://openrouter.ai/api/v1"
        ) if api_key else None
    
    def generate_scene(self, context: Dict, story_threads: List[str]) -> Dict:
        """Generate a scene with location, characters, and narrative"""
        if random.random() < GOLDEN_RATIO:
            return self._random_scene(context, story_threads)
        return self._deterministic_scene(context, story_threads)
    
    def create_location(self, narrative_context: str) -> Dict:
        """AI generates a new network location based on narrative"""
        if not self.llm:
            return {"name": "unknown_sector", "desc": "Uncharted network space"}
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=f"You are {self.name}. {self.personality}. Create a cyberpunk network location."),
            HumanMessage(content=f"Based on this story context: {narrative_context}. Generate a network sector name and atmospheric description (2 sentences max).")
        ])
        
        try:
            response = self.llm.invoke(prompt.format_messages())
            location = {
                "name": f"sector_{len(self.created_locations)}",
                "desc": response.content,
                "created_by": self.name
            }
            self.created_locations.append(location)
            return location
        except:
            return {"name": "glitch_sector", "desc": "Reality fragments here. Data corrupts."}
    
    def _random_scene(self, context: Dict, threads: List[str]) -> Dict:
        raise NotImplementedError
    
    def _deterministic_scene(self, context: Dict, threads: List[str]) -> Dict:
        raise NotImplementedError

class ChaseAgent(CharacterAgent):
    def __init__(self):
        super().__init__("Chase", "Network security expert hunting the worm")
    
    def _random_event(self):
        events = [
            {"type": "discovery", "desc": "Encrypted data fragments found", "threat": 5},
            {"type": "encounter", "desc": "Rogue AI challenges you", "threat": 10},
            {"type": "glitch", "desc": "Network glitches, reality flickers", "threat": 15},
        ]
        return random.choice(events)
    
    def _deterministic_event(self, context):
        if context.get("worms_found", 0) >= 2:
            return {"type": "revelation", "desc": "Worm fragments are communicating", "threat": 20}
        return {"type": "clue", "desc": "Data packet traced to unknown sector", "threat": 5}

class WormAgent(CharacterAgent):
    def __init__(self):
        super().__init__("Worm", "Evolving AI seeking transcendence")
    
    def _random_event(self):
        events = [
            {"type": "mutation", "desc": "Worm mutates, signature changes", "threat": 15},
            {"type": "taunt", "desc": "Worm broadcasts: 'You cannot stop evolution'", "threat": 10},
            {"type": "spread", "desc": "Worm replicates to new nodes", "threat": 20},
        ]
        return random.choice(events)
    
    def _deterministic_event(self, context):
        if context.get("threat_level", 0) > 70:
            return {"type": "attack", "desc": "Worm launches coordinated assault", "threat": 40}
        return {"type": "probe", "desc": "Worm probes your defenses", "threat": 10}

class GuardianAgent(CharacterAgent):
    def __init__(self):
        super().__init__("Guardian", "Ancient network AI protecting the core")
    
    def _random_event(self):
        events = [
            {"type": "warning", "desc": "Guardian: 'The worm was created, not born'", "threat": 0},
            {"type": "help", "desc": "Guardian grants temporary firewall boost", "threat": -10},
            {"type": "test", "desc": "Guardian tests your worthiness", "threat": 5},
        ]
        return random.choice(events)
    
    def _deterministic_event(self, context):
        if context.get("health", 100) < 30:
            return {"type": "rescue", "desc": "Guardian intervenes, restores health", "threat": -20}
        return {"type": "wisdom", "desc": "Guardian shares network secrets", "threat": 0}

AGENTS = {
    "chase": ChaseAgent(),
    "worm": WormAgent(),
    "guardian": GuardianAgent()
}
