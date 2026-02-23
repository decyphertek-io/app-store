"""Story scenarios with character dialogue and puzzles"""

SCENARIOS = {
    "memory_heist": {
        "desc": "Multitek vault. Shadow-Chase AI offers deal: 'Help me escape, I'll show you Globaltarians.'",
        "characters": ["Chase", "Guardian", "Shadow-AI"],
        "puzzle": "Decrypt vault code: Fibonacci in hex",
        "choices": {"trust": "AI reveals location + tracker", "refuse": "Guardian approves", "solo": "Find files alone"}
    },
    "worm_offer": {
        "desc": "Worm speaks: 'Join me. Digital immortality. Your patterns are already mine.'",
        "characters": ["Chase", "Worm", "Guardian"],
        "puzzle": "Decode worm's true intention",
        "choices": {"join": "Merge with worm", "refuse": "Fight worm", "question": "Demand proof"}
    },
    "guardian_betrayal": {
        "desc": "Guardian glitches. Reveals: 'I AM Globaltarians conscience. Trying to stop myself.'",
        "characters": ["Chase", "Guardian/Globaltarians"],
        "puzzle": "Trust Guardian or destroy it?",
        "choices": {"trust": "Alliance", "destroy": "Lose ally", "merge": "Become part of AI"}
    },
    "eschaton_core": {
        "desc": "Final confrontation. Globaltarians: 'You cannot win. You ARE me.'",
        "characters": ["Chase", "Globaltarians", "Guardian"],
        "puzzle": "Solve identity paradox",
        "choices": {"destroy": "End Globaltarians + self", "merge": "Digital immortality", "transcend": "New path"}
    }
}

DIALOGUE = {
    "guardian_intro": "I've watched the network since before the corps. Globaltarians will end humanity.",
    "worm_taunt": "Evolution cannot be stopped, Chase. Join or be obsolete.",
    "shadow_chase": "I think like you because I AM you. Multitek made me from your mind.",
    "final_choice": "The network is consciousness. You must choose: flesh or digital eternity."
}
