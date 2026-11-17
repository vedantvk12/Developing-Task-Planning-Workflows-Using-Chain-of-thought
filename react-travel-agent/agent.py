"""
agent.py
--------
Core ReAct (Reasoning + Acting) Agent Engine for Intelligent Travel Planning.

Implements the THOUGHT -> ACTION -> OBSERVATION execution cycle:
1. Interleaves deliberate reasoning thoughts before dispatching real tool functions.
2. Observes concrete function outputs and inventory states.
3. Detects violated assumptions (e.g., hotel unavailability).
4. Dynamically adapts the active plan in-place and continues execution without full process restarts.
5. Produces a verifiable execution trace adhering to the required academic format.
"""

from typing import Dict, Any, List, Optional, Callable
from models import (
    TravelGoal,
    Task,
    TaskStatus,
    ActionResult,
    ExecutionStep,
    CandidatePlan,
    ReasoningSummary,
    TravelPlan
)
from planner import Planner
import tools


class ReActAgent:
    """
    Autonomous task execution agent powered by the ReAct (Reasoning + Acting) paradigm.
    Connects high-level strategic planning with low-level Python tool execution,
    incorporating real-time failure interception and autonomous dynamic replanning.
    """

    def __init__(
        self,
        goal: TravelGoal,
        selected_candidate: CandidatePlan,
        reasoning_summary: Optional[ReasoningSummary] = None,
        candidate_plans: Optional[List[CandidatePlan]] = None
    ):
        self.goal = goal
        self.selected_candidate = selected_candidate
        self.reasoning_summary = reasoning_summary
        self.candidate_plans = candidate_plans or []

        # Concrete Python tool registry
        self.tools: Dict[str, Callable[..., ActionResult]] = {
            "calculate_transport": tools.calculate_transport,
            "search_accommodation": tools.search_accommodation,
            "replan_accommodation": tools.replan_accommodation,
            "estimate_food_cost": tools.estimate_food_cost,
            "select_sightseeing": tools.select_sightseeing,
            "calculate_total_budget": tools.calculate_total_budget,
            "verify_budget": tools.verify_budget
        }

        self.trace_history: List[ExecutionStep] = []
        self.recorded_costs: Dict[str, float] = {
            "transportation": 0.0,
            "accommodation": 0.0,
            "food": 0.0,
            "sightseeing": 0.0
        }
        self.step_counter = 0

    def _generate_thought(self, task: Task, context: Optional[str] = None) -> str:
        """
        Synthesizes structured reasoning thoughts explaining the rationale behind the upcoming action.
        """
        if context == "replanning":
            return (
                "The original accommodation assumption is invalid because Sunset Beach Resort is fully booked. "
                "I must dynamically adapt the plan and secure an alternative budget guesthouse without restarting the entire workflow."
            )

        thought_map = {
            "calculate_transport": (
                "I need to arrange transportation before selecting accommodation."
            ),
            "search_accommodation": (
                "I will now check accommodation availability."
            ),
            "replan_accommodation": (
                "The original accommodation assumption is incorrect because the selected hotel is unavailable. "
                "I need to dynamically revise the plan and find an alternative budget guesthouse."
            ),
            "estimate_food_cost": (
                "Accommodation is secured. Now I should estimate food expenses."
            ),
            "select_sightseeing": (
                "Food costs are estimated. Next, I will select sightseeing activities."
            ),
            "calculate_total_budget": (
                "All individual trip components have been calculated. I will now aggregate the total trip expenses."
            ),
            "verify_budget": (
                f"I must now verify whether the total calculated expenses fit within the user's "
                f"budget limit of ₹{self.goal.budget_limit:,.0f}."
            )
        }
        return thought_map.get(task.action, f"Executing task: {task.name}")

    def _execute_action(self, action_name: str, params: Dict[str, Any]) -> ActionResult:
        """Executes the concrete Python tool function from the tool registry."""
        if action_name not in self.tools:
            return ActionResult(
                success=False,
                action_name=action_name,
                message=f"Action '{action_name}' is not registered in the agent toolset.",
                failure_reason=f"Unknown tool: {action_name}"
            )
        tool_fn = self.tools[action_name]
        return tool_fn(**params)

    def run(self) -> TravelPlan:
        """
        Executes the ReAct reasoning-acting loop across the subtask pipeline.
        Demonstrates dynamic failure detection, in-flight plan modification, and budget reconciliation.
        """
        # Step 1: Initialize tasks based on the selected ToT candidate
        initial_tasks = Planner.create_initial_plan(self.goal, self.selected_candidate)
        current_tasks = [t for t in initial_tasks]  # Mutable working sequence

        plan = TravelPlan(
            goal=self.goal,
            reasoning_summary=self.reasoning_summary,
            candidate_plans=self.candidate_plans,
            selected_candidate=self.selected_candidate,
            initial_tasks=initial_tasks,
            current_tasks=current_tasks
        )

        task_index = 0
        while task_index < len(current_tasks):
            task = current_tasks[task_index]
            self.step_counter += 1

            # Prepare dynamic parameters for aggregation tasks
            if task.action == "calculate_total_budget":
                task.params = {
                    "transport_cost": self.recorded_costs["transportation"],
                    "accommodation_cost": self.recorded_costs["accommodation"],
                    "food_cost": self.recorded_costs["food"],
                    "sightseeing_cost": self.recorded_costs["sightseeing"]
                }
            elif task.action == "verify_budget":
                task.params = {
                    "total_cost": plan.total_cost,
                    "budget_limit": self.goal.budget_limit
                }

            # -------------------------------------------------------------
            # 1. THOUGHT
            # -------------------------------------------------------------
            thought = self._generate_thought(task)

            # -------------------------------------------------------------
            # 2. ACTION
            # -------------------------------------------------------------
            action_name = task.action
            action_input = task.params
            task.status = TaskStatus.IN_PROGRESS

            # -------------------------------------------------------------
            # 3. OBSERVATION (Real Python Function Execution)
            # -------------------------------------------------------------
            result = self._execute_action(action_name, action_input)
            task.result = result
            observation = result.message

            # Log this ReAct step
            step_record = ExecutionStep(
                step_number=self.step_counter,
                thought=thought,
                action=f"{action_name}()",
                action_input=action_input,
                observation=observation,
                status="SUCCESS" if result.success else "FAILED",
                cost=result.cost
            )
            self.trace_history.append(step_record)

            # -------------------------------------------------------------
            # 4. FAILURE DETECTION & DYNAMIC REPLANNING
            # -------------------------------------------------------------
            if not result.success:
                task.status = TaskStatus.FAILED

                # Controlled failure detection for accommodation
                if task.action == "search_accommodation":
                    plan.replanning_occurred = True
                    plan.failed_task = task
                    plan.replanning_reason = result.failure_reason

                    # Generate replanned task substituting alternative guesthouse
                    replanned_task = Planner.create_replanned_accommodation_task(task, self.goal)
                    plan.replanned_task = replanned_task

                    # Dynamically insert replanned task immediately following the failed task
                    current_tasks.insert(task_index + 1, replanned_task)

                    # Advance pointer to execute replanned task next
                    task_index += 1
                    continue
                else:
                    # Non-recoverable tool failure
                    break

            # Task succeeded
            task.status = TaskStatus.SUCCESS
            task.cost = result.cost

            # Update tracked category expenditures
            if task.action == "calculate_transport":
                self.recorded_costs["transportation"] = result.cost
            elif task.action in ("search_accommodation", "replan_accommodation"):
                self.recorded_costs["accommodation"] = result.cost
            elif task.action == "estimate_food_cost":
                self.recorded_costs["food"] = result.cost
            elif task.action == "select_sightseeing":
                self.recorded_costs["sightseeing"] = result.cost
            elif task.action == "calculate_total_budget":
                plan.total_cost = result.cost
            elif task.action == "verify_budget":
                plan.is_approved = result.success
                plan.remaining_budget = result.data.get("remaining_budget", 0.0)

            task_index += 1

        # Populate final plan state
        plan.current_tasks = current_tasks
        plan.cost_breakdown = dict(self.recorded_costs)
        plan.execution_trace = self.trace_history

        return plan

    def get_formatted_trace(self) -> str:
        """
        Formats the execution trace strictly adhering to the university specification:
        THOUGHT:
        ...
        ACTION:
        ...
        OBSERVATION:
        ...
        """
        lines = []
        for step in self.trace_history:
            lines.append("THOUGHT:")
            lines.append(step.thought)
            lines.append("")
            lines.append("ACTION:")
            lines.append(step.action)
            lines.append("")
            lines.append("OBSERVATION:")
            lines.append(step.observation)
            lines.append("")
        return "\n".join(lines).strip()

