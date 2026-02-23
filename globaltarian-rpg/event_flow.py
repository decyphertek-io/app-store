"""LangGraph Event Flow System - Golden Ratio Random/Deterministic Balance"""
import random
from typing import Dict, List, TypedDict
from langgraph.graph import StateGraph, END
from agents import AGENTS, GOLDEN_RATIO

class GameStateGraph(TypedDict):
    location: str
    health: int
    threat_level: int
    worms_found: int
    events_history: List[Dict]
    current_event: Dict
    agent_responses: List[str]

def trigger_random_event(state: GameStateGraph) -> GameStateGraph:
    """Randomly select an agent to generate an event"""
    agent_name = random.choice(list(AGENTS.keys()))
    agent = AGENTS[agent_name]
    
    context = {
        "health": state["health"],
        "threat_level": state["threat_level"],
        "worms_found": state["worms_found"],
        "location": state["location"]
    }
    
    event = agent.generate_event(context)
    event["source"] = agent_name
    
    state["current_event"] = event
    state["events_history"].append(event)
    state["threat_level"] += event.get("threat", 0)
    
    return state

def agents_respond(state: GameStateGraph) -> GameStateGraph:
    """Other agents respond to the current event"""
    current_event = state["current_event"]
    responses = []
    
    for agent_name, agent in AGENTS.items():
        if agent_name != current_event.get("source"):
            if random.random() < 0.5:  # 50% chance each agent responds
                try:
                    response = agent.respond_to_event(current_event) if agent.llm else None
                    if response:
                        responses.append(response)
                except:
                    pass
    
    state["agent_responses"] = responses
    return state

def update_game_state(state: GameStateGraph) -> GameStateGraph:
    """Apply event effects to game state"""
    event = state["current_event"]
    
    # Apply threat changes
    threat_change = event.get("threat", 0)
    state["threat_level"] = max(0, min(100, state["threat_level"] + threat_change))
    
    # Negative threat = healing
    if threat_change < 0:
        state["health"] = min(100, state["health"] - threat_change)
    
    # High threat damages health
    if state["threat_level"] > 70:
        state["health"] = max(0, state["health"] - 5)
    
    # Track worm discoveries
    if event.get("type") in ["discovery", "revelation"] and "worm" in event.get("desc", "").lower():
        state["worms_found"] += 1
    
    return state

def should_continue(state: GameStateGraph) -> str:
    """Decide if event flow should continue"""
    if state["health"] <= 0:
        return "game_over"
    if state["worms_found"] >= 5:
        return "victory"
    if random.random() < GOLDEN_RATIO:
        return "continue"
    return "end"

# Build LangGraph state machine
workflow = StateGraph(GameStateGraph)

# Add nodes
workflow.add_node("trigger_event", trigger_random_event)
workflow.add_node("agents_respond", agents_respond)
workflow.add_node("update_state", update_game_state)

# Add edges
workflow.set_entry_point("trigger_event")
workflow.add_edge("trigger_event", "agents_respond")
workflow.add_edge("agents_respond", "update_state")
workflow.add_conditional_edges(
    "update_state",
    should_continue,
    {
        "continue": "trigger_event",
        "end": END,
        "game_over": END,
        "victory": END
    }
)

# Compile graph
event_graph = workflow.compile()

def run_event_cycle(game_state: Dict) -> Dict:
    """Run one cycle of the event flow"""
    state = GameStateGraph(
        location=game_state.get("location", "central_hub"),
        health=game_state.get("health", 100),
        threat_level=game_state.get("threat_level", 0),
        worms_found=game_state.get("worms_found", 0),
        events_history=game_state.get("events_history", []),
        current_event={},
        agent_responses=[]
    )
    
    result = event_graph.invoke(state)
    return result
