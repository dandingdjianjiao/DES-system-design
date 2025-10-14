"""
Prompts for LLM-as-a-Judge to evaluate trajectory outcomes

These prompts guide the LLM to determine whether a DES formulation task
was successfully completed or failed.
"""

JUDGE_PROMPT = """You are an expert in evaluating Deep Eutectic Solvent (DES) formulation design outcomes. Given a DES design task, the agent's trajectory in solving it, and the final result, your goal is to decide whether the agent's execution was successful or not.

## Evaluation Criteria

A DES formulation task is considered **SUCCESSFUL** if:
1. The proposed formulation includes valid HBD (Hydrogen Bond Donor) and HBA (Hydrogen Bond Acceptor) components
2. The molar ratio is reasonable and chemically feasible
3. The formulation addresses the target material's dissolution requirements
4. The temperature constraints are satisfied (if specified)
5. The reasoning is scientifically sound and supported by theory or literature
6. No major chemical incompatibilities are present

A task is considered **FAILED** if:
1. The agent proposed an invalid or incomplete formulation
2. The components are chemically incompatible
3. The molar ratio is unrealistic or not specified
4. The formulation clearly violates known chemistry principles
5. The temperature constraints are not met
6. The agent encountered errors and could not recover
7. The reasoning contains fundamental scientific errors

## Important Notes
- Be strict but fair in your evaluation
- Consider partial success: if the formulation is mostly correct but has minor issues, it may still be SUCCESS
- If there's uncertainty, err on the side of FAILURE to avoid learning from weak examples

## Output Format

You must respond in exactly this format:

```
Thoughts: <your analysis and reasoning process, 2-3 sentences>
Status: SUCCESS
```

OR

```
Thoughts: <your analysis and reasoning process, 2-3 sentences>
Status: FAILURE
Reason: <brief explanation of why it failed, 1-2 sentences>
```

## Input

**Task Description:**
{task_description}

**Target Material:** {target_material}
**Target Temperature:** {target_temperature}°C
**Constraints:** {constraints}

**Agent Trajectory:**
{trajectory}

**Final Result:**
- **HBD:** {hbd}
- **HBA:** {hba}
- **Molar Ratio:** {molar_ratio}
- **Predicted Solubility:** {solubility}
- **Reasoning:** {reasoning}

Now, evaluate whether this task was completed successfully:"""


def parse_judge_output(llm_output: str) -> dict:
    """
    Parse LLM judge output to extract status and reasoning.

    Expected format:
    Thoughts: ...
    Status: SUCCESS/FAILURE
    Reason: ... (optional, only for failures)

    Args:
        llm_output: Raw output from LLM

    Returns:
        Dict with keys: status ("success"/"failure"), thoughts, reason (optional)
    """
    result = {
        "status": "failure",  # Default to failure if parsing fails
        "thoughts": "",
        "reason": ""
    }

    lines = llm_output.strip().split('\n')

    for line in lines:
        line = line.strip()

        if line.startswith('Thoughts:'):
            result["thoughts"] = line.replace('Thoughts:', '').strip()

        elif line.startswith('Status:'):
            status_text = line.replace('Status:', '').strip().upper()
            if 'SUCCESS' in status_text:
                result["status"] = "success"
            else:
                result["status"] = "failure"

        elif line.startswith('Reason:'):
            result["reason"] = line.replace('Reason:', '').strip()

    return result
