"""
planner.py
----------
Task Planner and Replanning Coordinator for the ReAct Travel Planning Agent.

Coordinates:
1. Converting selected Tree-of-Thought (ToT) candidate plans into an ordered sequence of executable tasks.
2. Generating dynamic replanning task substitutions upon environmental assumption failure.
"""

from typing import List, Dict, Any
from models import TravelGoal, Task, CandidatePlan


class Planner:
    """
    Constructs concrete execution pipelines from travel goals and ToT candidate selections.
    Supports in-flight plan modification and replanned task creation.
    """

    @staticmethod
    def create_initial_plan(goal: TravelGoal, selected_candidate: CandidatePlan) -> List[Task]:
        """
        Translates the selected candidate strategy into an ordered sequence of executable tasks.
        """
        # Determine transport parameter mode
        mode_map = {
            "Konkan Express (AC 3-Tier Sleeper)": "train_sleeper",
            "Standard Sleeper Train (Non-AC)": "train_non_ac",
            "Multi-Axle AC Volvo Sleeper Bus": "volvo_bus"
        }
        transport_mode = mode_map.get(selected_candidate.transport_choice, "train_sleeper")

        return [
            Task(
                task_id="task_1",
                name="Calculate transportation budget",
                action="calculate_transport",
                params={
                    "destination": goal.destination,
                    "num_people": goal.num_people,
                    "mode": transport_mode
                }
            ),
            Task(
                task_id="task_2",
                name="Search for available accommodation",
                action="search_accommodation",
                params={
                    "destination": goal.destination,
                    "duration_days": goal.duration_days,
                    "num_people": goal.num_people,
                    "hotel_name": "Sunset Beach Resort",
                    "simulate_failure": True  # Tests programmatic room inventory verification
                }
            ),
            Task(
                task_id="task_3",
                name="Estimate food expenses",
                action="estimate_food_cost",
                params={
                    "duration_days": goal.duration_days,
                    "num_people": goal.num_people,
                    "meal_tier": "budget_local"
                }
            ),
            Task(
                task_id="task_4",
                name="Select sightseeing activities",
                action="select_sightseeing",
                params={
                    "destination": goal.destination,
                    "num_people": goal.num_people,
                    "duration_days": goal.duration_days,
                    "package": "standard_highlights"
                }
            ),
            Task(
                task_id="task_5",
                name="Calculate total expenses",
                action="calculate_total_budget",
                params={}  # Bound dynamically at runtime from executed subtask costs
            ),
            Task(
                task_id="task_6",
                name="Verify whether the plan fits the budget",
                action="verify_budget",
                params={
                    "budget_limit": goal.budget_limit
                }
            )
        ]

    @staticmethod
    def create_replanned_accommodation_task(failed_task: Task, goal: TravelGoal) -> Task:
        """
        Generates an alternative accommodation task to substitute for a failed room booking.
        Selects a verified budget guesthouse to recover execution and lower expenditure.
        """
        return Task(
            task_id="task_2_replan",
            name="Replan accommodation (Select budget guesthouse)",
            action="replan_accommodation",
            params={
                "destination": goal.destination,
                "duration_days": goal.duration_days,
                "num_people": goal.num_people,
                "preferred_type": "budget_guesthouse"
            },
            is_replanned=True,
            original_task_id=failed_task.task_id
        )

