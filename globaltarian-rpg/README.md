# GLOBALTARIAN RPG

A cyberpunk text-based RPG set in 2184 where you hunt a polymorphic AI worm through the Globaltarian network.

## Story

Year 2184. The Multitek Universe. A polymorphic AI worm has self-populated through the network, rewriting reality as it spreads. You are Chase, a network security engineer tasked with tracerouting the globaltarian path and neutralizing it before the global parasite is an octopus throughout the network. 

## Features

- **Text-based TUI**: Cyberpunk terminal interface using Textual
- **LangChain Agents**: AI-powered character interactions
- **LangGraph Event Flows**: Dynamic story progression
- **OpenRouter AI**: AI vs AI battles
- **Network Traceroute**: Puzzle mechanics to find the worm
- **Cyberpunk Theme**: Neuromancer/Terminator/Orwell inspired

## Build & Run

```bash
# Build executable with UV + PyInstaller
bash build.sh

# Run the built executable
./dist/globaltarian-rpg.app
```

The build script uses UV to create a temporary venv, installs dependencies, builds with PyInstaller, then tears down the environment - leaving only the standalone executable.

## Commands

- `scan` - Scan current location for worm signatures
- `move <location>` - Move to connected network node
- `traceroute` - Trace network paths to find globaltarian locations
- `event` - Trigger AI event flow (requires OpenRouter API key)
- `help` - Show available commands
- `quit` - Exit game

## Game Mechanics

1. **Network Exploration**: Navigate through network nodes
2. **Worm Detection**: Use traceroute to find infected nodes
3. **AI Battles**: Fight the polymorphic worm using AI agents
4. **Story Progression**: Uncover the worm's origin through LangGraph events

## Requirements

- Python 3.13
- OpenRouter API key (for AI battles)
- UV package manager

## Configuration

Set your OpenRouter API key:
```bash
export OPENROUTER_API_KEY="your-key-here"
```

## Credits

Built with:
- Textual (TUI framework)
- LangChain (AI agents)
- LangGraph (Event flows)
- OpenRouter (AI API)
