"""
models.py
---------
Data models and structure definitions for the Unified CoT + ToT + ReAct Travel Planning Agent.
Defines representation for goals, tasks, candidate plans (Tree-of-Thought), execution steps,
reasoning summaries (Chain-of-Thought), tool action results, and the overall plan lifecycle.
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, List, Optional


class TaskStatus(str, Enum):
    """Enumeration of possible task states in the execution pipeline."""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    REPLANNED = "REPLANNED"


@dataclass
class TravelGoal:
    """Represents the parsed user travel goal and associated constraints."""
    raw_goal: str
    destination: str
    duration_days: int
    num_people: int
    budget_limit: float
    categories: List[str] = field(default_factory=lambda: [
        "transportation", "accommodation", "food", "sightseeing"
    ])

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ActionResult:
    """Standardized result returned by every action / tool execution."""
    success: bool
    action_name: str
    message: str
    cost: float = 0.0
    data: Dict[str, Any] = field(default_factory=dict)
    failure_reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Task:
    """Represents an atomic subtask within the execution plan."""
    task_id: str
    name: str
    action: str
    params: Dict[str, Any] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    cost: float = 0.0
    result: Optional[ActionResult] = None
    is_replanned: bool = False
    original_task_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        return data


@dataclass
class ExecutionStep:
    """Represents a single step in the ReAct (Thought -> Action -> Observation) trace."""
    step_number: int
    thought: str
    action: str
    action_input: Dict[str, Any]
    observation: str
    status: str
    cost: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CandidatePlan:
    """
    Represents an alternative candidate plan generated and evaluated
    during the Tree-of-Thought (ToT) exploration phase.
    """
    plan_id: str                  # e.g., "Plan A", "Plan B", "Plan C"
    name: str                     # e.g., "Budget-Focused Travel", "Balanced Travel", etc.
    transport_choice: str
    accommodation_choice: str
    food_tier: str
    sightseeing_tier: str
    cost_breakdown: Dict[str, float]
    total_cost: float
    is_feasible: bool
    cost_score: float             # 0.0 to 100.0
    feasibility_score: float      # 0.0 to 100.0
    experience_score: float       # 0.0 to 100.0
    composite_score: float        # Weighted evaluation score
    description: str
    pros: List[str] = field(default_factory=list)
    cons: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ReasoningSummary:
    """
    Represents the structured Chain-of-Thought (CoT) decomposition summary.
    Explains the rationale, constraints, and dependencies without exposing raw internal thoughts.
    """
    goal_statement: str
    constraints: List[str]
    subtasks: List[Dict[str, str]]
    dependencies: List[str]
    execution_order_rationale: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TravelPlan:
    """Encapsulates the complete lifecycle of a travel plan across CoT, ToT, and ReAct."""
    goal: TravelGoal
    reasoning_summary: Optional[ReasoningSummary] = None
    candidate_plans: List[CandidatePlan] = field(default_factory=list)
    selected_candidate: Optional[CandidatePlan] = None
    initial_tasks: List[Task] = field(default_factory=list)
    current_tasks: List[Task] = field(default_factory=list)
    replanning_occurred: bool = False
    failed_task: Optional[Task] = None
    replanned_task: Optional[Task] = None
    replanning_reason: Optional[str] = None
    cost_breakdown: Dict[str, float] = field(default_factory=dict)
    total_cost: float = 0.0
    remaining_budget: float = 0.0
    is_approved: bool = False
    execution_trace: List[ExecutionStep] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "goal": self.goal.to_dict(),
            "reasoning_summary": self.reasoning_summary.to_dict() if self.reasoning_summary else None,
            "candidate_plans": [cp.to_dict() for cp in self.candidate_plans],
            "selected_candidate": self.selected_candidate.to_dict() if self.selected_candidate else None,
            "initial_tasks": [t.to_dict() for t in self.initial_tasks],
            "current_tasks": [t.to_dict() for t in self.current_tasks],
            "replanning_occurred": self.replanning_occurred,
            "failed_task": self.failed_task.to_dict() if self.failed_task else None,
            "replanned_task": self.replanned_task.to_dict() if self.replanned_task else None,
            "replanning_reason": self.replanning_reason,
            "cost_breakdown": self.cost_breakdown,
            "total_cost": self.total_cost,
            "remaining_budget": self.remaining_budget,
            "is_approved": self.is_approved,
            "execution_trace": [s.to_dict() for s in self.execution_trace]
        }

