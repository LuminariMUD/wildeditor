# AI Integration Guide

This document describes the AI-powered description generation system integrated into the Wildeditor MCP server.

## Overview

The Wildeditor MCP server now includes AI-powered description generation using PydanticAI, with support for multiple AI providers and graceful fallback to template-based generation.

## Features

### Multi-Provider Support
- **OpenAI** (GPT-4, GPT-3.5)
- **Anthropic** (Claude 3 Opus, Claude 3 Sonnet)
- **Ollama** (Local LLMs - Llama2, Mistral, etc.)
- **Template Fallback** (When no AI provider is configured)

### Structured Output
The AI service generates structured descriptions with metadata:
- Content flags (historical, resources, wildlife, geological, cultural)
- Quality scores (0-9.99)
- Word counts and character counts
- Key features extraction

### Graceful Degradation
The system follows a fallback chain:
1. Configured AI provider (via AI_PROVIDER env var)
2. Auto-detection (OpenAI → Anthropic → Ollama)
3. Template-based generation (always available)

## Configuration

### Environment Variables

Add to your `.env` file in `/home/luminari/wildeditor/apps/mcp/`:

```bash
# AI Provider Configuration
AI_PROVIDER=openai  # Options: openai, anthropic, ollama, none

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4-turbo-preview

# Anthropic Configuration  
ANTHROPIC_API_KEY=your-anthropic-api-key
ANTHROPIC_MODEL=claude-3-opus-20240229

# Ollama Configuration (for local LLMs)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

### Provider Selection Priority

1. **Explicit Configuration**: Set `AI_PROVIDER` to force a specific provider
2. **Auto-Detection**: If `AI_PROVIDER=none` or unset, the system checks for available API keys
3. **Fallback**: If no AI provider is available, template generation is used

## MCP Tools

### generate_region_description

Generates comprehensive descriptions for wilderness regions.

**Parameters:**
- `region_name`: Name of the region
- `terrain_theme`: Primary terrain type/theme
- `description_style`: Writing style (poetic, practical, mysterious, dramatic, pastoral)
- `description_length`: Target length (brief, moderate, detailed, extensive)
- `include_sections`: List of sections to include

**Example Request:**
```json
{
  "id": "gen-1",
  "method": "tools/call",
  "params": {
    "name": "generate_region_description",
    "arguments": {
      "region_name": "Crystal Caves",
      "terrain_theme": "underground crystal formations",
      "description_style": "mysterious",
      "description_length": "moderate",
      "include_sections": ["overview", "geography", "atmosphere", "wildlife"]
    }
  }
}
```

**Response:**
```json
{
  "generated_description": "...",
  "metadata": {
    "has_historical_context": false,
    "has_resource_info": true,
    "has_wildlife_info": true,
    "has_geological_info": true,
    "has_cultural_info": false,
    "quality_score": 8.5
  },
  "word_count": 450,
  "character_count": 2800,
  "suggested_quality_score": 8.5,
  "ai_provider": "openai",
  "key_features": ["crystal formations", "underground rivers", "bioluminescent fungi"]
}
```

## Testing

### Check AI Service Status

```python
#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/luminari/wildeditor/apps/mcp/src')

from services.ai_service import get_ai_service

ai_service = get_ai_service()
provider_info = ai_service.get_provider_info()

print(f"Provider: {provider_info['provider']}")
print(f"Available: {provider_info['available']}")
print(f"Model: {provider_info.get('model', 'N/A')}")
```

### Test via MCP Server

```bash
curl -X POST http://luminarimud.com:8001/mcp/request \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test-1",
    "method": "tools/call",
    "params": {
      "name": "generate_region_description",
      "arguments": {
        "region_name": "Test Region",
        "terrain_theme": "forest",
        "description_style": "poetic",
        "description_length": "brief"
      }
    }
  }'
```

## Cost Optimization

### Development Phase
During initial world-building, use high-quality AI models for rich descriptions:
- OpenAI GPT-4 for maximum quality
- Anthropic Claude 3 Opus for creative writing
- Higher token limits for extensive descriptions

### Production Phase
Once the world is established, optimize costs:
- Switch to GPT-3.5-turbo or Claude 3 Haiku
- Use Ollama for local generation (no API costs)
- Rely more on template generation for routine updates
- Cache generated descriptions

### Hybrid Approach
- Use AI for important regions (cities, quest areas)
- Use templates for generic wilderness areas
- Allow manual override for curated content

## Architecture

### Components

1. **AI Service** (`services/ai_service.py`)
   - Provider management
   - Model initialization
   - Structured output generation
   - Fallback handling

2. **MCP Tools** (`mcp/tools.py`)
   - Integration point for AI service
   - Fallback to template generation
   - API communication

3. **Configuration** (`config.py`)
   - Environment variable management
   - API settings

### Data Flow

```
MCP Client Request
    ↓
MCP Server (tools/call)
    ↓
ToolRegistry._generate_region_description()
    ↓
AIService.generate_description()
    ↓
PydanticAI Agent → AI Provider API
    ↓
Structured Output (GeneratedDescription)
    ↓
MCP Response
```

## Troubleshooting

### Common Issues

1. **"No module named 'services'" Error**
   - Ensure you're running from the correct directory
   - Check Python path includes MCP src directory

2. **AI Provider Not Available**
   - Verify API keys are set in environment
   - Check provider service status
   - Review logs for authentication errors

3. **Fallback to Templates**
   - This is normal when no AI provider is configured
   - Check environment variables if AI was expected

### Debug Mode

Enable debug logging in `.env`:
```bash
WILDEDITOR_LOG_LEVEL=DEBUG
```

View logs:
```bash
tail -f /var/log/mcp-server.log
```

## Future Enhancements

### Planned Features
- [ ] Fine-tuning support for specialized wilderness descriptions
- [ ] Embedding-based similarity search for consistent style
- [ ] Batch generation for multiple regions
- [ ] Description variation generation
- [ ] Translation support for multi-language MUDs

### Integration Opportunities
- Connect to game's existing lore database
- Incorporate player-generated content
- Dynamic descriptions based on time/weather
- Quest-aware contextual descriptions

## Support

For issues or questions:
- Check logs at `/var/log/mcp-server.log`
- Review test scripts in repository
- Contact the Luminari development team