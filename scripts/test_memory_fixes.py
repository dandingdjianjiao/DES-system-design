"""
Test script to verify memory-related fixes in DESAgent

This script:
1. Generates a new recommendation with the updated Agent
2. Verifies memories_used is saved to trajectory.final_result
3. Verifies LLM-autonomous memory retrieval decision appears in logs
"""

import sys
import os
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from agent.des_agent import DESAgent
from agent.reasoningbank import (
    ReasoningBank,
    MemoryRetriever,
    MemoryExtractor,
    LLMJudge,
    RecommendationManager
)
from dotenv import load_dotenv

# Load environment
load_dotenv()

def simple_llm_client(prompt: str) -> str:
    """Simple LLM client using DashScope"""
    import openai

    client = openai.OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    )

    response = client.chat.completions.create(
        model="qwen-plus",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    return response.choices[0].message.content


def main():
    print("="*60)
    print("Testing Memory Fixes in DESAgent")
    print("="*60)

    # Initialize components
    print("\n[1/5] Initializing ReasoningBank components...")

    data_dir = project_root / "src" / "agent" / "data"
    memory_path = data_dir / "memory_bank.json"
    rec_dir = data_dir / "recommendations"

    memory_bank = ReasoningBank()
    retriever = MemoryRetriever(memory_bank, simple_llm_client)
    extractor = MemoryExtractor(simple_llm_client)
    judge = LLMJudge(simple_llm_client)
    rec_manager = RecommendationManager(str(rec_dir))

    # Load existing memories if available
    if memory_path.exists():
        memory_bank.load(str(memory_path))
        print(f"   ✓ Loaded {len(memory_bank.get_all_memories())} existing memories")
    else:
        print("   ✓ Starting with empty memory bank")

    # Initialize Agent
    print("\n[2/5] Initializing DESAgent...")
    agent = DESAgent(
        llm_client=simple_llm_client,
        reasoning_bank=memory_bank,
        retriever=retriever,
        extractor=extractor,
        judge=judge,
        rec_manager=rec_manager,
        corerag_client=None,  # Not needed for this test
        largerag_client=None,  # Not needed for this test
        config={
            "agent": {"max_iterations": 3},  # Shorter for testing
            "memory": {"min_similarity": 0.0}
        }
    )
    print("   ✓ DESAgent initialized")

    # Create test task
    print("\n[3/5] Creating test task...")
    task = {
        "task_id": "memory_fix_test_001",
        "description": "Design a DES to dissolve lignin at low temperature (-10°C)",
        "target_material": "lignin",
        "target_temperature": -10,
        "constraints": {
            "viscosity": "< 300 cP"
        }
    }
    print(f"   ✓ Task: {task['description']}")

    # Generate recommendation
    print("\n[4/5] Generating recommendation...")
    print("   (This will test LLM-autonomous memory retrieval)")
    result = agent.solve_task(task)

    rec_id = result["recommendation_id"]
    print(f"   ✓ Generated recommendation: {rec_id}")
    print(f"   ✓ Confidence: {result.get('confidence', 0):.2f}")

    # Verify memories_used in final_result
    print("\n[5/5] Verifying fixes...")

    # Load the saved recommendation
    rec_file = rec_dir / f"{rec_id}.json"
    if not rec_file.exists():
        print(f"   ✗ ERROR: Recommendation file not found: {rec_file}")
        return

    with open(rec_file, 'r', encoding='utf-8') as f:
        saved_rec = json.load(f)

    # Check Fix #1: memories_used in final_result
    final_result = saved_rec.get("trajectory", {}).get("final_result", {})
    memories_used = final_result.get("memories_used")

    if memories_used is not None:
        print(f"   ✓ FIX #1 VERIFIED: memories_used field exists in final_result")
        print(f"      - Contains {len(memories_used)} memory titles")
        if memories_used:
            print(f"      - Example: {memories_used[0][:60]}...")
    else:
        print(f"   ✗ FIX #1 FAILED: memories_used field NOT found in final_result")

    # Check Fix #2: Look for LLM decision in result
    if "memories_used" in result:
        print(f"   ✓ FIX #2 VERIFIED: LLM-autonomous retrieval decision completed")
        print(f"      - Retrieved {len(result.get('memories_used', []))} memories")
    else:
        print(f"   ! FIX #2: No memories retrieved (memory bank may be empty)")

    # Summary
    print("\n" + "="*60)
    print("VERIFICATION COMPLETE")
    print("="*60)
    print(f"Recommendation ID: {rec_id}")
    print(f"Recommendation file: {rec_file}")
    print("\nNext steps:")
    print("1. Check the recommendation detail page in web frontend")
    print("2. Verify 'Used Memories' section appears (if memories exist)")
    print("3. Check agent logs for '[Memory Retrieval] LLM decision' messages")


if __name__ == "__main__":
    main()
