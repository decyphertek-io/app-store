"""Fractal Story Engine - Parses agent interactions into narrative threads"""
import random
from typing import Dict, List

GOLDEN_RATIO = 0.618

class StoryEngine:
    def __init__(self):
        self.narrative_threads = []
        self.story_depth = 0
        
    def parse_interaction(self, scene: Dict, agents: List) -> Dict:
        """Parse agent scene into narrative thread"""
        thread = {
            "scene": scene,
            "depth": self.story_depth,
            "connections": []
        }
        
        # Find connections to previous threads (fractal pattern)
        for prev in self.narrative_threads[-3:]:
            if self._threads_connect(scene, prev["scene"]):
                thread["connections"].append(prev)
        
        self.narrative_threads.append(thread)
        
        # Increase story complexity
        if len(thread["connections"]) > 0:
            self.story_depth += 1
        
        return thread
    
    def _threads_connect(self, scene1: Dict, scene2: Dict) -> bool:
        """Check if scenes share narrative elements"""
        keywords1 = set(scene1.get("desc", "").lower().split())
        keywords2 = set(scene2.get("desc", "").lower().split())
        return len(keywords1 & keywords2) > 2
    
    def get_narrative_summary(self) -> str:
        """Generate summary of story so far"""
        if not self.narrative_threads:
            return "Story beginning..."
        
        recent = self.narrative_threads[-5:]
        summary = f"Story depth: {self.story_depth}. "
        summary += f"Recent events: {len(recent)}. "
        
        return summary

STORY = StoryEngine()
