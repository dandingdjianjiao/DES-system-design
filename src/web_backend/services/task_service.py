"""
Task Service

Business logic for creating and managing DES formulation tasks.
"""

import logging
import threading
from typing import Dict, Any
from datetime import datetime

from models.schemas import TaskRequest, TaskData, FormulationData, ComponentData
from utils.agent_loader import get_agent, get_rec_manager

logger = logging.getLogger(__name__)


class TaskService:
    """Service for managing DES formulation tasks"""

    def __init__(self):
        """Initialize task service"""
        pass

    def create_task(self, task_request: TaskRequest) -> TaskData:
        """
        Create a DES formulation task and generate recommendation asynchronously.

        This method:
        1. Creates a GENERATING recommendation immediately
        2. Starts background thread to execute Agent
        3. Returns the GENERATING recommendation to user
        4. Updates to PENDING when generation completes

        Args:
            task_request: Validated task request

        Returns:
            TaskData with GENERATING status

        Raises:
            RuntimeError: If initial setup fails
        """
        logger.info(f"Creating task for material: {task_request.target_material}")

        try:
            # Build task dictionary for agent
            task_dict = {
                "description": task_request.description,
                "target_material": task_request.target_material,
                "target_temperature": task_request.target_temperature,
                "num_components": task_request.num_components or 2,
                "constraints": task_request.constraints or {}
            }

            if task_request.task_id:
                task_dict["task_id"] = task_request.task_id
            else:
                # Generate task_id if not provided
                task_dict["task_id"] = f"{task_request.target_material}_{int(datetime.now().timestamp() * 1000)}"

            # Create initial GENERATING recommendation
            rec_manager = get_rec_manager()
            from agent.reasoningbank import Recommendation
            from agent.reasoningbank.memory import Trajectory

            # Generate recommendation_id
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            rec_id = f"REC_{timestamp}_{task_dict['target_material']}_{task_dict['task_id']}"

            # Create placeholder trajectory
            placeholder_trajectory = Trajectory(
                task_id=task_dict["task_id"],
                task_description=task_dict["description"],
                steps=[],
                outcome="generating",
                final_result={},
                metadata={
                    "target_material": task_dict["target_material"],
                    "target_temperature": task_dict["target_temperature"],
                    "num_components": task_dict["num_components"]
                }
            )

            # Create GENERATING recommendation
            rec = Recommendation(
                recommendation_id=rec_id,
                task=task_dict,
                task_id=task_dict["task_id"],
                formulation={"placeholder": True, "molar_ratio": "Generating..."},
                reasoning="Configuration正在生成中，请稍候...",
                confidence=0.0,
                trajectory=placeholder_trajectory,
                status="GENERATING",
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )

            # Save GENERATING recommendation
            rec_manager.save_recommendation(rec)
            logger.info(f"Created GENERATING recommendation: {rec_id}")

            # Start background thread to execute agent
            thread = threading.Thread(
                target=self._execute_task_async,
                args=(task_dict, rec_id),
                daemon=True
            )
            thread.start()
            logger.info(f"Started background task for {rec_id}")

            # Return GENERATING status immediately
            task_data = TaskData(
                task_id=task_dict["task_id"],
                recommendation_id=rec_id,
                formulation=FormulationData(
                    HBD="Generating",
                    HBA="Generating",
                    molar_ratio="Generating..."
                ),
                reasoning="配方正在后台生成中，请稍候...",
                confidence=0.0,
                supporting_evidence=["任务已提交到后台队列"],
                status="GENERATING",
                created_at=rec.created_at,
                memories_used=[],
                next_steps="请前往推荐列表查��生成进度，或稍后刷新页面"
            )

            return task_data

        except Exception as e:
            logger.error(f"Failed to create task: {e}", exc_info=True)
            raise RuntimeError(f"Task creation failed: {str(e)}")

    def _execute_task_async(self, task_dict: Dict[str, Any], rec_id: str):
        """
        Execute agent task asynchronously in background thread.

        This method:
        1. Calls agent.solve_task()
        2. Replaces GENERATING recommendation with PENDING result
        3. Handles errors by updating status to FAILED

        Args:
            task_dict: Task parameters
            rec_id: Recommendation ID that was created with GENERATING status
        """
        try:
            logger.info(f"[Background] Executing task {rec_id}...")

            # Get agent instance
            agent = get_agent()

            # Call agent to solve task (this may take minutes)
            # Agent will create a new recommendation with status=PENDING
            result = agent.solve_task(task_dict)

            logger.info(f"[Background] Task {rec_id} completed successfully")

            # Agent created a new recommendation, we need to:
            # 1. Delete the GENERATING placeholder
            # 2. Rename agent's recommendation to our rec_id
            rec_manager = get_rec_manager()

            agent_rec_id = result.get("recommendation_id")
            if agent_rec_id and agent_rec_id != rec_id:
                # Load agent's recommendation
                agent_rec = rec_manager.get_recommendation(agent_rec_id)

                if agent_rec:
                    # Update its ID to match our placeholder ID
                    agent_rec.recommendation_id = rec_id
                    agent_rec.updated_at = datetime.now().isoformat()

                    # Save with new ID
                    rec_manager.save_recommendation(agent_rec)

                    # Delete agent's original recommendation file
                    import os
                    agent_rec_file = rec_manager.storage_path / f"{agent_rec_id}.json"
                    if agent_rec_file.exists():
                        os.remove(agent_rec_file)

                    # Remove from index
                    if agent_rec_id in rec_manager.index:
                        del rec_manager.index[agent_rec_id]
                        rec_manager._save_index()

                    logger.info(f"[Background] Replaced GENERATING {rec_id} with completed recommendation")
                else:
                    logger.warning(f"[Background] Agent recommendation {agent_rec_id} not found")
            else:
                logger.info(f"[Background] Recommendation IDs match, no replacement needed")

        except Exception as e:
            logger.error(f"[Background] Task {rec_id} failed: {e}", exc_info=True)

            # Update recommendation to FAILED status
            try:
                rec_manager = get_rec_manager()
                rec = rec_manager.get_recommendation(rec_id)
                if rec:
                    rec.status = "FAILED"
                    rec.reasoning = f"配方生成失败: {str(e)}"
                    rec.updated_at = datetime.now().isoformat()
                    rec_manager.save_recommendation(rec)
                    logger.info(f"[Background] Updated {rec_id} to FAILED status")
            except Exception as update_error:
                logger.error(f"[Background] Failed to update recommendation status: {update_error}")

    def _convert_agent_result(self, result: Dict[str, Any]) -> TaskData:
        """
        Convert agent result to TaskData format.

        Args:
            result: Agent solve_task() result

        Returns:
            TaskData instance
        """
        # Extract formulation
        formulation_dict = result.get("formulation", {})

        # Check if multi-component or binary formulation
        if "components" in formulation_dict and formulation_dict["components"]:
            # Multi-component formulation
            components = [
                ComponentData(
                    name=comp.get("name", "Unknown"),
                    role=comp.get("role", "Unknown"),
                    function=comp.get("function")
                )
                for comp in formulation_dict["components"]
            ]
            formulation = FormulationData(
                components=components,
                num_components=formulation_dict.get("num_components", len(components)),
                molar_ratio=formulation_dict.get("molar_ratio", "Unknown")
            )
        else:
            # Binary formulation (backward compatible)
            formulation = FormulationData(
                HBD=formulation_dict.get("HBD", "Unknown"),
                HBA=formulation_dict.get("HBA", "Unknown"),
                molar_ratio=formulation_dict.get("molar_ratio", "Unknown")
            )

        # Build TaskData
        task_data = TaskData(
            task_id=result.get("task_id", "unknown"),
            recommendation_id=result.get("recommendation_id", "unknown"),
            formulation=formulation,
            reasoning=result.get("reasoning", "No reasoning provided"),
            confidence=result.get("confidence", 0.5),
            supporting_evidence=result.get("supporting_evidence", []),
            status=result.get("status", "PENDING"),
            created_at=datetime.now().isoformat(),
            memories_used=result.get("memories_used", []),
            next_steps=result.get("next_steps")
        )

        return task_data


# Singleton instance
_service: TaskService = None


def get_task_service() -> TaskService:
    """Get task service singleton"""
    global _service
    if _service is None:
        _service = TaskService()
    return _service
