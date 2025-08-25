#!/usr/bin/env python3
"""
Test AI service integration locally
"""

import asyncio
import sys
import os

# Add the MCP src directory to path
sys.path.insert(0, '/home/luminari/wildeditor/apps/mcp/src')

from mcp.tools import ToolRegistry

async def test():
    tools = ToolRegistry()
    result = await tools._generate_region_description(
        region_name='Crystal Caverns',
        terrain_theme='underground crystal formations',
        description_style='mysterious',
        description_length='brief'
    )
    
    print("=" * 60)
    print("AI DESCRIPTION GENERATION TEST")
    print("=" * 60)
    
    if 'error' in result:
        print(f"❌ Error: {result['error']}")
    else:
        print(f"✅ Success!")
        print(f"   AI Provider: {result.get('ai_provider', 'unknown')}")
        print(f"   Word count: {result.get('word_count', 0)}")
        print(f"   Character count: {result.get('character_count', 0)}")
        print(f"   Quality score: {result.get('suggested_quality_score', 0):.1f}")
        
        # Show metadata
        metadata = result.get('metadata', {})
        if metadata:
            print(f"\n   Metadata flags:")
            for key, value in metadata.items():
                if value and key != 'quality_score':
                    print(f"     - {key}: {value}")
        
        # Show preview
        desc = result.get('generated_description', '')
        if desc:
            print(f"\n   Description preview (first 300 chars):")
            print(f"   {desc[:300]}...")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(test())