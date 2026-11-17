"""
reasoning.py
------------
Chain-of-Thought (CoT) Structured Reasoning and Goal Decomposition Module.

Responsible for:
1. Parsing natural language user travel goals and extracting core entities & constraints.
2. Formulating structured, user-facing reasoning summaries (explaining WHY each task is needed).
3. Establishing mathematical task dependencies and determining optimal execution order.
4. Keeping private raw chain-of-thought non-leaking, surfacing crisp, professional rationales.
"""

import re
from typing import Dict, List, Any
from models import TravelGoal, ReasoningSummary


class ChainOfThoughtReasoner:
    """
    Implements structured Chain-of-Thought (CoT) reasoning for goal decomposition.
    Analyzes complex travel objectives into ordered subtasks with clear justifications.
    """

    @staticmethod
    def parse_goal(goal_text: str) -> TravelGoal:
        """
        Parses the user's natural language goal into a structured TravelGoal dataclass.
        Extracts destination, duration, party size, and budget ceiling.
        """
        # Destination extraction
        dest_match = re.search(r'\bto\s+([A-Za-z]+)', goal_text, re.IGNORECASE)
        destination = dest_match.group(1).capitalize() if dest_match else "Goa"

        # Duration extraction (e.g. "2-day", "2 days")
        dur_match = re.search(r'(\d+)[-\s]*(?:day|days)', goal_text, re.IGNORECASE)
        duration_days = int(dur_match.group(1)) if dur_match else 2

        # Party size extraction (e.g. "2 people", "for 2 travelers")
        people_match = re.search(r'(\d+)\s*(?:people|persons|travelers|guests)', goal_text, re.IGNORECASE)
        num_people = int(people_match.group(1)) if people_match else 2

        # Budget extraction (e.g. "₹10,000", "Rs. 10000", "budget of 10000")
        budget_match = (
            re.search(r'budget\s*(?:of|is|:)?\s*(?:₹|rs\.?|inr)?\s*([\d,]+)', goal_text, re.IGNORECASE) or
            re.search(r'(?:₹|rs\.?|inr)\s*([\d,]+)', goal_text, re.IGNORECASE)
        )
        if budget_match:
            clean_num = budget_match.group(1).replace(',', '')
            budget_limit = float(clean_num) if clean_num.isdigit() else 10000.0
        else:
            budget_limit = 10000.0

        return TravelGoal(
            raw_goal=goal_text.strip(),
            destination=destination,
            duration_days=duration_days,
            num_people=num_people,
            budget_limit=budget_limit,
            categories=["transportation", "accommodation", "food", "sightseeing"]
        )

    @classmethod
    def decompose_goal(cls, goal: TravelGoal) -> ReasoningSummary:
        """
        Applies Chain-of-Thought (CoT) reasoning to decompose the goal into structured,
        ordered subtasks with explicit justifications and dependency mappings.
        """
        constraints = [
            f"Strict Total Budget Ceiling: ₹{goal.budget_limit:,.0f} (Non-negotiable hard ceiling)",
            f"Geographic Target: {goal.destination} (Requires inter-city transit and local mobility)",
            f"Trip Duration: {goal.duration_days} Days / 1 Night (Compact schedule requiring efficient logistics)",
            f"Party Size: {goal.num_people} Persons (All per-person rates must scale by {goal.num_people})",
            "Mandatory Scope: Transportation, Accommodation, Food, and Sightseeing must all be covered"
        ]

        subtasks = [
            {
                "step": "1",
                "task_name": "Calculate Transportation Expenses",
                "tool_action": "calculate_transport",
                "justification": (
                    f"Transit to and from {goal.destination} constitutes the foundational logistics prerequisite. "
                    f"Round-trip tickets for {goal.num_people} people must be locked in first to establish baseline expenditure "
                    f"and confirm arrival timing before hotel bookings."
                )
            },
            {
                "step": "2",
                "task_name": "Find and Secure Accommodation",
                "tool_action": "search_accommodation",
                "justification": (
                    f"Lodging is the primary fixed overhead during the {goal.duration_days}-day stay. "
                    f"Inventory availability in {goal.destination} must be actively verified to secure overnight rest "
                    f"and provide an anchor point for daily sightseeing."
                )
            },
            {
                "step": "3",
                "task_name": "Estimate Food and Dining Expenses",
                "tool_action": "estimate_food_cost",
                "justification": (
                    f"Daily sustenance across {goal.duration_days} days for {goal.num_people} travelers represents a essential variable cost. "
                    f"Estimating realistic local dining tiers prevents cash shortfalls while ensuring authentic culinary experiences."
                )
            },
            {
                "step": "4",
                "task_name": "Select Sightseeing and Local Commute",
                "tool_action": "select_sightseeing",
                "justification": (
                    f"Sightseeing maximizes leisure value. Activities and local scooter rentals must be budgeted to fit "
                    f"within the remaining margin after transit, stay, and food are provisioned."
                )
            },
            {
                "step": "5",
                "task_name": "Calculate Total Trip Expenses",
                "tool_action": "calculate_total_budget",
                "justification": (
                    "Aggregates expenditure across all 4 discrete categories (Transit + Accommodation + Food + Sightseeing) "
                    "into an authoritative total sum."
                )
            },
            {
                "step": "6",
                "task_name": "Verify Budget Feasibility",
                "tool_action": "verify_budget",
                "justification": (
                    f"Performs automated constraint satisfaction audit against the ₹{goal.budget_limit:,.0f} limit, "
                    f"calculating exact financial buffer or surplus savings."
                )
            }
        ]

        dependencies = [
            "calculate_transport -> search_accommodation: Arrival timing and hub proximity influence hotel selection.",
            "search_accommodation -> estimate_food_cost: Geographic base determines nearby dining access and meal options.",
            "estimate_food_cost -> select_sightseeing: Remaining financial bandwidth determines excursion package scale.",
            "{transport, accommodation, food, sightseeing} -> calculate_total_budget: Total aggregation strictly requires all 4 inputs.",
            "calculate_total_budget -> verify_budget: Final compliance audit depends strictly on aggregated trip total."
        ]

        order_rationale = (
            "The execution order strictly respects causal and financial dependencies. "
            "Fixed inter-city transportation is determined first, followed by accommodation booking. "
            "Daily variable sustenance (food) and discretionary recreation (sightseeing) are scheduled within remaining capacity. "
            "Finally, mathematical aggregation and constraint validation verify full compliance with the user's budget ceiling."
        )

        return ReasoningSummary(
            goal_statement=goal.raw_goal,
            constraints=constraints,
            subtasks=subtasks,
            dependencies=dependencies,
            execution_order_rationale=order_rationale
        )

