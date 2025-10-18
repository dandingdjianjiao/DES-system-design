"""
Test script for the new ReAct-based DESAgent

This script tests the Think-Act-Observe loop with a simple DES formulation task.
"""

import sys
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agent.reasoningbank import (
    ReasoningBank,
    MemoryRetriever,
    MemoryExtractor,
    LLMJudge,
    RecommendationManager
)
from agent.des_agent import DESAgent
from agent.utils import LLMClient, EmbeddingClient
from agent.config import get_config  # NEW: Load config from YAML
from agent.tools import create_largerag_adapter, create_corerag_adapter  # NEW: Real tools

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Test the ReAct agent with a simple task"""

    print("="*70)
    print("Testing ReAct-based DES Formulation Agent")
    print("="*70)
    print()

    # Load configuration from YAML
    logger.info("Loading configuration from reasoningbank_config.yaml...")
    config_loader = get_config()

    # Get config sections
    llm_config = config_loader.get_llm_config("agent_llm")  # Use agent_llm for main reasoning
    embedding_config = config_loader.get_embedding_config()
    memory_config = config_loader.get_memory_config()
    rec_config = config_loader.get_recommendations_config()
    extractor_config = config_loader.get_extractor_config()
    judge_config = config_loader.get_judge_config()
    agent_config = config_loader.get_agent_config()

    logger.info(f"Config loaded: max_iterations={agent_config.get('max_iterations', 8)}")

    # Initialize components
    logger.info("Initializing agent components...")

    try:
        # Create LLM client from config
        llm_client = LLMClient(
            provider=llm_config["provider"],
            model=llm_config["model"],
            temperature=llm_config["temperature"],
            max_tokens=llm_config["max_tokens"]
        )
        logger.info(f"LLM client initialized: {llm_client.provider}/{llm_client.model}")

        # Create embedding client from config
        embedding_client = EmbeddingClient(
            provider=embedding_config["provider"],
            model=embedding_config["model"]
        )
        logger.info(f"Embedding client initialized")

    except Exception as e:
        logger.error(f"Failed to initialize API clients: {e}")
        logger.error("Please ensure DASHSCOPE_API_KEY is set in environment")
        return

    # Create memory bank from config
    bank = ReasoningBank(
        embedding_func=embedding_client.embed,
        max_items=memory_config["max_items"]
    )

    # Create retriever
    retriever = MemoryRetriever(
        bank=bank,
        embedding_func=embedding_client.embed
    )

    # Create extractor from config
    extractor = MemoryExtractor(
        llm_client=llm_client,
        temperature=extractor_config["temperature"],
        max_items_per_trajectory=memory_config["extraction_max_per_trajectory"]
    )

    # Create judge from config
    judge = LLMJudge(
        llm_client=llm_client,
        temperature=judge_config["temperature"]
    )

    # Create recommendation manager from config
    rec_manager = RecommendationManager(
        storage_path=rec_config["storage_path"]
    )

    # Initialize tool clients
    logger.info("CoreRAG temporarily disabled for fast testing")
    corerag = None  # Temporarily disable to test LLM query generation logic

    logger.info("Initializing LargeRAG adapter...")
    try:
        largerag = create_largerag_adapter()
        status = largerag.get_status()
        if status["status"] == "ready":
            logger.info("LargeRAG adapter initialized successfully")
        elif status["status"] == "no_index":
            logger.warning("LargeRAG index not found. Build index first: python src/tools/largerag/examples/1_build_index.py")
            largerag = None
        else:
            logger.error(f"LargeRAG initialization failed: {status.get('message', '')}")
            largerag = None
    except Exception as e:
        logger.error(f"Failed to initialize LargeRAG: {e}")
        largerag = None

    # Pass full config dict to agent (it will use agent_config section)
    agent = DESAgent(
        llm_client=llm_client,
        reasoning_bank=bank,
        retriever=retriever,
        extractor=extractor,
        judge=judge,
        rec_manager=rec_manager,
        corerag_client=corerag,  # Use real tools
        largerag_client=largerag,
        config=config_loader.config  # Pass entire config dict
    )

    logger.info("Agent initialized successfully")
    print()

    # Define a test task
    task = {
        "task_id": "react_test_001",
        "description": "Design a DES to dissolve cellulose at room temperature (25°C)",
        "target_material": "cellulose",
        "target_temperature": 25,
        "constraints": {
            "viscosity": "< 500 cP",
            "toxicity": "low"
        }
    }

    print("Test Task:")
    print(f"  Description: {task['description']}")
    print(f"  Target Material: {task['target_material']}")
    print(f"  Target Temperature: {task['target_temperature']}°C")
    print(f"  Constraints: {task['constraints']}")
    print()

    # Solve task with ReAct loop
    print("Starting ReAct loop...")
    print("="*70)

    result = agent.solve_task(task)

    # Display results
    print("\n" + "="*70)
    print("RESULT")
    print("="*70)
    print(f"Status: {result['status']}")
    print(f"Iterations Used: {result['iterations_used']}")
    print()

    if result.get('formulation'):
        formulation = result['formulation']
        print("Formulation:")

        # Check if multi-component DES (has "components" key) or binary DES (has "HBD"/"HBA")
        if 'components' in formulation:
            # Multi-component DES
            num_components = formulation.get('num_components', len(formulation.get('components', [])))
            print(f"  Type: {num_components}-component DES")
            print(f"  Components:")
            for i, comp in enumerate(formulation.get('components', []), 1):
                print(f"    {i}. {comp.get('name', 'Unknown')} ({comp.get('role', 'N/A')}) - {comp.get('function', 'N/A')}")
            print(f"  Molar Ratio: {formulation.get('molar_ratio', 'N/A')}")
        else:
            # Binary DES
            print(f"  Type: Binary DES")
            print(f"  HBD: {formulation.get('HBD', 'N/A')}")
            print(f"  HBA: {formulation.get('HBA', 'N/A')}")
            print(f"  Molar Ratio: {formulation.get('molar_ratio', 'N/A')}")
        print()

    print(f"Reasoning: {result.get('reasoning', 'N/A')[:300]}...")
    print()
    print(f"Confidence: {result.get('confidence', 0.0):.2f}")
    print()

    if result.get('information_sources'):
        sources = result['information_sources']
        print("Information Sources:")
        print(f"  Memories: {sources['memories']}")
        print(f"  Theory (CoreRAG): {sources['theory']}")
        print(f"  Literature (LargeRAG): {sources['literature']}")
        print()

    print(f"Recommendation ID: {result.get('recommendation_id', 'N/A')}")
    print()
    print(f"Next Steps: {result.get('next_steps', 'N/A')[:150]}...")
    print()

    print("="*70)
    print("ReAct Agent Test Completed")
    print("="*70)


if __name__ == "__main__":
    main()
