
import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path.cwd()))

from app.core.config import settings
from app.services.memory.rememberall_service import RememberallService
from app.services.monitoring.opik_service import OpikService

async def test_memory_service():
    print("\n--- Testing Rememberall Service (Memory) ---")
    try:
        service = RememberallService()
        await service.initialize()
        
        # Test storing a preference
        print("Storing user preference...")
        await service.store_memory(
            user_id="test_user",
            content="User prefers fast upbeat music for videos.",
            metadata={"type": "preference", "category": "music"}
        )
        
        # Test retrieval
        print("Retrieving memories...")
        memories = await service.retrieve_relevant(
            user_id="test_user",
            query="What music does the user like?"
        )
        
        print(f"Retrieved {len(memories)} memories.")
        for m in memories:
            print(f"- {m['content']}")
            
        print("✅ Memory Service Test Passed")
    except Exception as e:
        print(f"❌ Memory Service Test Failed: {e}")

async def test_monitoring_service():
    print("\n--- Testing Opik Service (Monitoring) ---")
    try:
        service = OpikService()
        
        # Test tracking a simple event
        print("Tracking event...")
        await service.track_event(
            name="test_event",
            input_data={"test": "data"},
            output_data={"result": "success"},
            metadata={"user": "test_user"}
        )
        
        print("✅ Monitoring Service Test Passed (Event logged)")
    except Exception as e:
        print(f"❌ Monitoring Service Test Failed: {e}")

async def main():
    # Ensure OPENAI_API_KEY is set (mock if needed for testing structure)
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️ OPENAI_API_KEY not set. Some AI calls might fail or need mocking.")
        # We can set a dummy key if we just want to test structure, but Chroma/Langchain might validate it.
        # os.environ["OPENAI_API_KEY"] = "sk-dummy" 

    await test_memory_service()
    await test_monitoring_service()

if __name__ == "__main__":
    asyncio.run(main())
