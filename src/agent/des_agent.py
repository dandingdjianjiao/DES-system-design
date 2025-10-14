"""
DES Formulation Agent with ReasoningBank

This module implements the main agent for DES formulation design,
integrating ReasoningBank memory system with CoreRAG and LargeRAG tools.
"""

from typing import Dict, List, Optional, Callable
import logging
from datetime import datetime

from .reasoningbank import (
    ReasoningBank,
    MemoryRetriever,
    MemoryExtractor,
    LLMJudge,
    MemoryItem,
    MemoryQuery,
    Trajectory,
    format_memories_for_prompt
)

logger = logging.getLogger(__name__)


class DESAgent:
    """
    Main agent for DES formulation design with ReasoningBank memory.

    The agent follows this workflow:
    1. Retrieve relevant memories from ReasoningBank
    2. Query CoreRAG for theoretical knowledge
    3. Query LargeRAG for literature precedents
    4. Generate DES formulation with reasoning
    5. Evaluate outcome (success/failure)
    6. Extract new memories and consolidate

    Attributes:
        llm_client: LLM for agent reasoning
        reasoning_bank: ReasoningBank instance
        retriever: MemoryRetriever instance
        extractor: MemoryExtractor instance
        judge: LLMJudge instance
        corerag_client: CoreRAG tool interface
        largerag_client: LargeRAG tool interface
        config: Configuration dictionary
    """

    def __init__(
        self,
        llm_client: Callable[[str], str],
        reasoning_bank: ReasoningBank,
        retriever: MemoryRetriever,
        extractor: MemoryExtractor,
        judge: LLMJudge,
        corerag_client: Optional[object] = None,
        largerag_client: Optional[object] = None,
        config: Optional[Dict] = None
    ):
        """
        Initialize DESAgent.

        Args:
            llm_client: Function for LLM calls
            reasoning_bank: ReasoningBank instance
            retriever: MemoryRetriever instance
            extractor: MemoryExtractor instance
            judge: LLMJudge instance
            corerag_client: CoreRAG tool (optional)
            largerag_client: LargeRAG tool (optional)
            config: Configuration dictionary
        """
        self.llm_client = llm_client
        self.memory = reasoning_bank
        self.retriever = retriever
        self.extractor = extractor
        self.judge = judge
        self.corerag = corerag_client
        self.largerag = largerag_client
        self.config = config or {}

        logger.info("Initialized DESAgent with ReasoningBank")

    def solve_task(self, task: Dict) -> Dict:
        """
        Main entry point for solving a DES formulation task.

        Args:
            task: Task dictionary with keys:
                - task_id: Unique identifier
                - description: Natural language description
                - target_material: Material to dissolve
                - target_temperature: Target temperature (°C)
                - constraints: Additional constraints

        Returns:
            Dict with keys:
                - formulation: Proposed DES formulation
                - reasoning: Explanation of design choices
                - confidence: Confidence score (0-1)
                - supporting_evidence: Literature/theory references
                - status: "success" or "failure"
        """
        task_id = task.get("task_id", f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        logger.info(f"Starting task {task_id}: {task['description'][:50]}...")

        # Initialize trajectory tracking
        trajectory_steps = []
        tool_calls = []

        # Step 1: Memory Retrieval
        logger.info("Step 1: Retrieving relevant memories")
        memories = self._retrieve_memories(task)
        trajectory_steps.append({
            "action": "retrieve_memories",
            "reasoning": f"Retrieved {len(memories)} relevant past experiences",
            "num_memories": len(memories)
        })

        # Step 2: Query Tools
        logger.info("Step 2: Querying knowledge tools")
        theory_knowledge = self._query_corerag(task) if self.corerag else None
        literature_knowledge = self._query_largerag(task) if self.largerag else None

        if theory_knowledge:
            tool_calls.append({"tool": "CoreRAG", "query": task["description"], "result": theory_knowledge})
            trajectory_steps.append({
                "action": "query_corerag",
                "reasoning": "Retrieved theoretical principles for DES design",
                "tool": "CoreRAG"
            })

        if literature_knowledge:
            tool_calls.append({"tool": "LargeRAG", "query": task["description"], "result": literature_knowledge})
            trajectory_steps.append({
                "action": "query_largerag",
                "reasoning": "Retrieved literature precedents",
                "tool": "LargeRAG"
            })

        # Step 3: Generate Formulation
        logger.info("Step 3: Generating DES formulation")
        formulation_result = self._generate_formulation(
            task, memories, theory_knowledge, literature_knowledge
        )
        trajectory_steps.append({
            "action": "generate_formulation",
            "reasoning": formulation_result.get("reasoning", ""),
            "formulation": formulation_result["formulation"]
        })

        # Step 4: Evaluate Outcome
        logger.info("Step 4: Evaluating outcome")
        trajectory = Trajectory(
            task_id=task_id,
            task_description=task["description"],
            steps=trajectory_steps,
            outcome="unknown",  # Will be determined by judge
            final_result=formulation_result,
            metadata={
                "target_material": task.get("target_material"),
                "target_temperature": task.get("target_temperature"),
                "constraints": task.get("constraints", {}),
                "tool_calls": tool_calls
            }
        )

        judge_result = self.judge.evaluate(trajectory)
        outcome = judge_result["status"]  # "success" or "failure"
        trajectory.outcome = outcome

        # Step 5: Extract and Consolidate Memories
        logger.info(f"Step 5: Extracting memories from {outcome} trajectory")
        new_memories = self.extractor.extract_from_trajectory(trajectory, outcome)

        if new_memories:
            self.memory.consolidate(new_memories)
            logger.info(f"Consolidated {len(new_memories)} new memories")

            # Auto-save if configured
            if self.config.get("memory", {}).get("auto_save", False):
                save_path = self.config["memory"]["persist_path"]
                self.memory.save(save_path)
                logger.info(f"Auto-saved memory bank to {save_path}")

        # Prepare final result
        result = formulation_result.copy()
        result["status"] = outcome
        result["judge_thoughts"] = judge_result.get("thoughts", "")
        result["task_id"] = task_id
        result["memories_used"] = [m.title for m in memories]
        result["memories_extracted"] = [m.title for m in new_memories]

        logger.info(f"Task {task_id} completed with status: {outcome.upper()}")

        return result

    def _retrieve_memories(self, task: Dict) -> List[MemoryItem]:
        """
        Retrieve relevant memories for the task.

        Args:
            task: Task dictionary

        Returns:
            List of relevant MemoryItem objects
        """
        query = MemoryQuery(
            query_text=task["description"],
            top_k=self.config.get("memory", {}).get("retrieval_top_k", 3),
            min_similarity=self.config.get("memory", {}).get("min_similarity", 0.0)
        )

        memories = self.retriever.retrieve(query)
        logger.debug(f"Retrieved {len(memories)} memories for task")

        return memories

    def _query_corerag(self, task: Dict) -> Optional[Dict]:
        """
        Query CoreRAG for theoretical knowledge.

        Args:
            task: Task dictionary

        Returns:
            Dict with theory knowledge, or None if unavailable
        """
        if not self.corerag:
            logger.warning("CoreRAG client not available")
            return None

        try:
            # Format query for CoreRAG
            query = {
                "query": f"What are the key principles for dissolving {task['target_material']} using DES?",
                "focus": ["hydrogen_bonding", "component_selection", "molar_ratio"]
            }

            # Call CoreRAG (interface depends on actual implementation)
            result = self.corerag.query(query)
            logger.debug(f"CoreRAG returned: {str(result)[:100]}...")

            return result

        except Exception as e:
            logger.error(f"CoreRAG query failed: {e}")
            return None

    def _query_largerag(self, task: Dict) -> Optional[Dict]:
        """
        Query LargeRAG for literature precedents.

        Args:
            task: Task dictionary

        Returns:
            Dict with literature knowledge, or None if unavailable
        """
        if not self.largerag:
            logger.warning("LargeRAG client not available")
            return None

        try:
            # Format query for LargeRAG
            query = {
                "query": f"DES formulations for {task['target_material']} at {task.get('target_temperature', 25)}°C",
                "filters": {
                    "material_type": task.get("material_category", "polymer"),
                    "temperature_range": [task.get("target_temperature", 25) - 10, task.get("target_temperature", 25) + 10]
                },
                "top_k": self.config.get("tools", {}).get("largerag", {}).get("max_results", 10)
            }

            # Call LargeRAG
            result = self.largerag.query(query)
            logger.debug(f"LargeRAG returned: {str(result)[:100]}...")

            return result

        except Exception as e:
            logger.error(f"LargeRAG query failed: {e}")
            return None

    def _generate_formulation(
        self,
        task: Dict,
        memories: List[MemoryItem],
        theory: Optional[Dict],
        literature: Optional[Dict]
    ) -> Dict:
        """
        Generate DES formulation using LLM with all available knowledge.

        Args:
            task: Task dictionary
            memories: Retrieved memory items
            theory: CoreRAG theory knowledge
            literature: LargeRAG literature knowledge

        Returns:
            Dict with formulation, reasoning, confidence, etc.
        """
        # Build comprehensive prompt
        prompt = self._build_formulation_prompt(task, memories, theory, literature)

        # Call LLM
        try:
            llm_output = self.llm_client(prompt)
            logger.debug(f"LLM formulation output: {llm_output[:200]}...")
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            return {
                "formulation": {},
                "reasoning": f"Error: {str(e)}",
                "confidence": 0.0,
                "supporting_evidence": []
            }

        # Parse LLM output
        result = self._parse_formulation_output(llm_output)

        return result

    def _build_formulation_prompt(
        self,
        task: Dict,
        memories: List[MemoryItem],
        theory: Optional[Dict],
        literature: Optional[Dict]
    ) -> str:
        """
        Build comprehensive prompt for formulation generation.

        Args:
            task: Task dictionary
            memories: Retrieved memories
            theory: Theory knowledge
            literature: Literature knowledge

        Returns:
            Formatted prompt string
        """
        prompt = "# DES Formulation Design Task\n\n"

        # Task description
        prompt += f"## Task\n{task['description']}\n\n"
        prompt += f"**Target Material:** {task['target_material']}\n"
        prompt += f"**Target Temperature:** {task.get('target_temperature', 25)}°C\n"

        constraints = task.get("constraints", {})
        if constraints:
            prompt += f"**Constraints:** {constraints}\n"

        prompt += "\n"

        # Inject memories
        if memories:
            prompt += format_memories_for_prompt(memories)
            prompt += "\n"

        # Add theory knowledge
        if theory:
            prompt += "## Theoretical Knowledge (from CoreRAG)\n\n"
            prompt += f"{theory}\n\n"

        # Add literature knowledge
        if literature:
            prompt += "## Literature Precedents (from LargeRAG)\n\n"
            prompt += f"{literature}\n\n"

        # Instructions
        prompt += """## Instructions

Based on the above information, design a DES formulation. Your output must include:

1. **HBD (Hydrogen Bond Donor)**: Component name
2. **HBA (Hydrogen Bond Acceptor)**: Component name
3. **Molar Ratio**: e.g., "1:2" (HBD:HBA)
4. **Reasoning**: Explain your design choices (2-3 sentences)
5. **Confidence**: 0.0 to 1.0
6. **Supporting Evidence**: List key facts from memory/theory/literature

Format your response as JSON:
```json
{
    "formulation": {
        "HBD": "...",
        "HBA": "...",
        "molar_ratio": "..."
    },
    "reasoning": "...",
    "confidence": 0.0,
    "supporting_evidence": ["...", "..."]
}
```
"""

        return prompt

    def _parse_formulation_output(self, llm_output: str) -> Dict:
        """
        Parse LLM output to extract formulation.

        Args:
            llm_output: Raw LLM output

        Returns:
            Structured formulation dict
        """
        import json
        import re

        # Try to extract JSON
        json_match = re.search(r'```json\s*(.*?)\s*```', llm_output, re.DOTALL)
        if json_match:
            try:
                result = json.loads(json_match.group(1))
                return result
            except json.JSONDecodeError:
                logger.warning("Failed to parse JSON from LLM output")

        # Fallback: return minimal structure
        return {
            "formulation": {},
            "reasoning": llm_output[:500],
            "confidence": 0.5,
            "supporting_evidence": []
        }


# Example usage and testing
if __name__ == "__main__":
    # This will be implemented in examples/example_des_task.py
    pass
