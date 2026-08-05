# Chat Assistant Guide

The Wilderness Editor Chat Assistant is an AI-powered building companion that helps create wilderness regions, paths, and descriptions through natural language interaction.

## Quick Start

1. **Open Chat**: Click the chat icon in the top-right corner of the editor
2. **Position Window**: Drag the chat window to your preferred location (even to a second monitor)
3. **Resize**: Drag the corners to resize the window - settings are saved automatically
4. **Start Building**: Ask the assistant to create regions, paths, or analyze terrain

## Core Capabilities

### Spatial Intelligence

The assistant can analyze your wilderness and make smart recommendations:

```
"Find empty space near the village for a new forest region"
"What terrain is between coordinates (100, 200) and (300, 400)?"
"Analyze the area around the mountain region"
```

### Region Creation

Create regions with natural, organic borders:

```
"Create a dense forest region northeast of the village"
"Make a swamp region between the river and hills"
"Add a geographic region covering the valley floor"
```

**Features:**
- Organic borders with 8-12 coordinate points
- Terrain-aware placement using elevation data
- Overlap prevention for geographic regions
- Multiple region types supported

### Path Building

Connect regions with natural-looking paths:

```
"Create a dirt road connecting the village to the forest"
"Make a river flowing from the mountains to the ocean"
"Connect these three regions with a paved road"
```

**Features:**
- Curved paths with 4-8 coordinate points
- Terrain-following routes for rivers
- Multiple path types (roads, rivers, streams)
- Multi-region connections

### Terrain Analysis

Understand your wilderness geography:

```
"What's the elevation at coordinates (150, 300)?"
"Show me a map of the area around the castle"
"Find zone entrances near the forest"
```

## UI Features

### Draggable Window
- **Drag Handle**: Click and drag the title bar to move the window
- **Multi-Monitor**: Works across multiple displays
- **Position Memory**: Window position is saved between sessions

### Resizable Interface
- **Resize Handles**: Drag corners or edges to resize
- **Constraints**: Minimum 300x200, maximum 800x600 pixels
- **Size Memory**: Window size is saved between sessions

### Markdown Support
- **Rich Text**: Full markdown rendering for AI responses
- **Code Blocks**: Syntax-highlighted code examples
- **Tables**: Formatted data tables
- **Links**: Clickable links (when applicable)

## Natural Language Commands

### Region Commands

| Command | Result |
|---------|---------|
| "Create a forest region" | Creates a new forest region with organic borders |
| "Make a geographic region covering the hills" | Creates a region following terrain contours |
| "Add a swamp between regions A and B" | Finds space and creates connecting region |

### Path Commands

| Command | Result |
|---------|---------|
| "Connect village to castle with road" | Creates curved road between regions |
| "Make a river from mountains to ocean" | Creates river following elevation descent |
| "Draw a dirt path through the forest" | Creates natural path with terrain awareness |

### Analysis Commands

| Command | Result |
|---------|---------|
| "What's at coordinates (100, 200)?" | Analyzes terrain and existing features |
| "Find empty space near the lake" | Identifies suitable areas for new regions |
| "Show terrain map around village" | Generates area analysis with overlays |

## Integration with Editor

### View Control

The assistant can control the map view:

```
"Center the map on the forest region"
"Show me region #1001045"
"Focus on coordinates (250, -100)"
```

### Content Staging

All AI-generated content follows the staging pattern:

1. **Generation**: AI creates descriptions, hints, or coordinates
2. **Staging**: Content is held in memory (not saved to database)
3. **Review**: User sees amber "staged" indicators
4. **Save/Discard**: User explicitly saves or discards staged content

This ensures you always control what gets permanently saved.

## Technical Architecture

### Communication Flow
```
Chat UI (Frontend) → Chat Agent (Port 8002) → MCP Server (Port 8001) → Backend (Port 8000)
```

### Key Components

1. **ChatAssistant.tsx**: Draggable/resizable chat window with markdown rendering
2. **ChatBridge.ts**: Converts AI actions to editor operations
3. **Chat Agent**: PydanticAI-powered assistant with spatial intelligence
4. **MCP Server**: Tool layer providing wilderness operations

### Data Flow

1. User types message in chat
2. Message sent to Chat Agent (port 8002)
3. Agent analyzes request and calls MCP tools (port 8001)
4. MCP tools query/modify backend database (port 8000)
5. Agent generates response with actions
6. ChatBridge executes actions in frontend editor
7. User sees results immediately (staged content)

## Advanced Features

### Organic Border Generation

The assistant uses sophisticated algorithms to create natural-looking region borders:

- **Polar Coordinates**: Generates points around center using angles
- **Irregularity**: Varies angles for non-geometric shapes  
- **Spikiness**: Varies radius for natural variation
- **Terrain Following**: Adjusts to elevation and sector data

### Overlap Prevention

Geographic regions are automatically checked for overlaps:

- **Bounding Box Analysis**: Quick overlap detection
- **Geographic Region Focus**: Only warns about geographic (type 1) overlaps
- **Alternative Suggestions**: Provides different coordinates if conflicts exist

### Terrain-Aware Routing

Paths are created with terrain intelligence:

- **Elevation Analysis**: Rivers flow downhill, roads avoid steep grades  
- **Curve Generation**: Bezier-like curves for natural appearance
- **Obstacle Avoidance**: Routes around existing regions when possible

## Troubleshooting

### Common Issues

**Chat not responding:**
- Check browser console for errors
- Verify chat agent is running (port 8002)
- Try refreshing the page

**Actions not working:**
- Ensure you have unsaved changes permission
- Check if the item already exists
- Look for error messages in chat response

**Window position lost:**
- Clear browser localStorage if needed
- Reset by dragging window back to desired position

### Performance Tips

- Keep chat window reasonably sized for better performance
- Close chat when not needed to save memory  
- Refresh if responses become slow

## Best Practices

### Effective Prompts

**Good prompts:**
- "Create a forest region northeast of the village with organic borders"
- "Make a river connecting the mountain springs to the coastal harbor"
- "Find suitable space for a market town between the forest and plains"

**Less effective prompts:**
- "Make something"
- "Add region"
- "Create path here" (without specific location)

### Workflow Integration

1. **Plan First**: Ask for terrain analysis before creating
2. **Review Staging**: Always check staged content before saving
3. **Save Frequently**: Use Save buttons to persist your work
4. **Test Navigation**: Verify paths connect properly in-game

## Future Enhancements

### Planned Features

- **WebSocket Support**: Real-time streaming responses
- **Session History**: Persistent conversation history
- **Region Templates**: Pre-built region types and themes  
- **Batch Operations**: Create multiple related features at once
- **Export/Import**: Share chat-created content between projects

### Feedback

Report issues or suggestions in the project repository. The chat assistant is actively developed and improved based on user feedback.