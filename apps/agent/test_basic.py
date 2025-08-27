#!/usr/bin/env python
"""Basic test to verify Chat Agent can be initialized"""
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        from config import settings
        print("✅ Config imported successfully")
        
        from agent.chat_agent import WildernessAssistantAgent, AssistantResponse, EditorContext
        print("✅ Chat agent modules imported")
        
        from session.storage import InMemoryStorage, create_storage
        print("✅ Storage modules imported")
        
        from session.manager import SessionManager
        print("✅ Session manager imported")
        
        print("\n✅ All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {str(e)}")
        return False


async def test_storage():
    """Test storage initialization"""
    print("\nTesting storage...")
    
    try:
        from session.storage import create_storage
        
        # Test in-memory storage
        storage = create_storage("memory")
        print("✅ In-memory storage created")
        
        # Test basic operations
        await storage.save("test_key", {"data": "test"}, 60)
        data = await storage.load("test_key")
        assert data == {"data": "test"}
        print("✅ Storage save/load working")
        
        await storage.delete("test_key")
        data = await storage.load("test_key")
        assert data is None
        print("✅ Storage delete working")
        
        return True
        
    except Exception as e:
        print(f"❌ Storage test failed: {str(e)}")
        return False


async def test_session_manager():
    """Test session manager"""
    print("\nTesting session manager...")
    
    try:
        from session.storage import create_storage
        from session.manager import SessionManager
        
        storage = create_storage("memory")
        manager = SessionManager(storage)
        print("✅ Session manager created")
        
        # Create session
        session_id = await manager.create_session(user_id="test_user")
        print(f"✅ Session created: {session_id}")
        
        # Add message
        message = await manager.add_message(
            session_id, 
            "user", 
            "Test message"
        )
        assert message is not None
        print("✅ Message added to session")
        
        # Get history
        history = await manager.get_history(session_id)
        assert len(history) == 1
        assert history[0].content == "Test message"
        print("✅ Session history working")
        
        return True
        
    except Exception as e:
        print(f"❌ Session manager test failed: {str(e)}")
        return False


async def test_agent_initialization():
    """Test agent initialization (requires API key)"""
    print("\nTesting agent initialization...")
    
    try:
        import os
        from dotenv import load_dotenv
        
        # Load environment variables
        env_path = Path(__file__).parent / ".env"
        if env_path.exists():
            load_dotenv(env_path)
        
        # Check if API key is available
        if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
            print("⚠️  Skipping agent test - no API key configured")
            print("   To test agent, add OPENAI_API_KEY or ANTHROPIC_API_KEY to .env")
            return True
        
        from agent.chat_agent import WildernessAssistantAgent
        
        agent = WildernessAssistantAgent()
        print("✅ Agent initialized successfully")
        
        # Test basic chat (if API key is available)
        response = await agent.chat("Hello, are you working?")
        assert response.message
        print(f"✅ Agent responded: {response.message[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent test failed: {str(e)}")
        return False


async def main():
    """Run all tests"""
    print("=" * 60)
    print("Chat Agent Basic Tests")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(await test_imports())
    results.append(await test_storage())
    results.append(await test_session_manager())
    results.append(await test_agent_initialization())
    
    # Summary
    print("\n" + "=" * 60)
    if all(results):
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())