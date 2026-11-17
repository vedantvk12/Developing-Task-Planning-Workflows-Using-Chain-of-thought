"""
tree_search.py
--------------
Tree-of-Thought (ToT) Alternative Plan Exploration and Evaluation Module.

Implements an authentic Tree-of-Thought search mechanism:
1. Generates multiple candidate plan branches across discrete travel modalities:
   - Plan A: Budget-Focused Travel
   - Plan B: Balanced Travel
   - Plan C: Experience-Focused Travel
2. Computes component expenses using actual Python math functions.
3. Evaluates hard budget feasibility constraints against user ceilings.
4. Computes multi-attribute scoring across Cost Efficiency, Feasibility, and Experience Quality.
5. Produces a structured comparative evaluation table and selects the optimal candidate.
"""

from typing import List, Dict, Tuple, Any
from models import TravelGoal, CandidatePlan


class TreeOfThoughtPlanner:
    """
    Explores alternative plan spaces using Tree-of-Thought (ToT) principles.
    Branches into distinct strategic paradigms, evaluates each leaf node mathematically,
    and returns the highest-scoring feasible candidate.
    """

    # Catalog of travel configuration options for candidate generation
    TRAVEL_MODALITIES = {
        "Plan A": {
            "name": "Budget-Focused Travel",
            "transport": {
                "name": "Standard Sleeper Train (Non-AC)",
                "rate_per_person": 800.0
            },
            "accommodation": {
                "name": "Sea Mist Backpacker Hostel (Dorm Pod)",
                "total_cost": 1500.0
            },
            "food": {
                "tier": "Local Dhabas & Street Food",
                "daily_rate_per_person": 500.0
            },
            "sightseeing": {
                "tier": "Self-Guided Beach Walks & Heritage Sites",
                "total_cost": 800.0
            },
            "experience_rating": 55.0,
            "description": "Maximizes financial savings with dormitory lodging and public walking tours.",
            "pros": ["Lowest expenditure", "High savings buffer (₹4,100)", "No debt risk"],
            "cons": ["Shared dorm room", "Non-AC overnight transit", "Limited dining variety"]
        },
        "Plan B": {
            "name": "Balanced Travel",
            "transport": {
                "name": "Konkan Express (AC 3-Tier Sleeper)",
                "rate_per_person": 1000.0
            },
            "accommodation": {
                "name": "Sunset Beach Resort (3-Star Beachfront)",
                "total_cost": 3000.0
            },
            "food": {
                "tier": "Local Goan Beach Shacks & Authentic Thalis",
                "daily_rate_per_person": 750.0
            },
            "sightseeing": {
                "tier": "Fort Aguada + Churches + 2-Day Scooter Rental",
                "total_cost": 1200.0
            },
            "experience_rating": 88.0,
            "description": "Optimal equilibrium of comfort, private resort stay, authentic cuisine, and motorized mobility.",
            "pros": ["Private beachfront resort room", "AC train transit", "Scooter mobility across Goa", "Fits budget comfortably"],
            "cons": ["Moderate savings buffer (₹800)", "Subject to resort room inventory availability"]
        },
        "Plan C": {
            "name": "Experience-Focused Travel",
            "transport": {
                "name": "Multi-Axle AC Volvo Sleeper Bus",
                "rate_per_person": 1400.0
            },
            "accommodation": {
                "name": "Heritage Boutique Beachfront Villa",
                "total_cost": 4800.0
            },
            "food": {
                "tier": "Fine Dining Seafood & Beachfront Cafes",
                "daily_rate_per_person": 1000.0
            },
            "sightseeing": {
                "tier": "Guided Water Sports & Scuba Package + Private Cab",
                "total_cost": 2500.0
            },
            "experience_rating": 96.0,
            "description": "Luxury-oriented itinerary prioritizing premium hospitality, watersports, and gourmet dining.",
            "pros": ["Luxury villa stay", "Curated scuba diving and water sports", "Private chauffeur cab"],
            "cons": ["Exceeds budget ceiling by ₹4,100", "Infeasible without significant budget escalation"]
        }
    }

    @classmethod
    def calculate_candidate_cost(
        cls,
        modal_data: Dict[str, Any],
        goal: TravelGoal
    ) -> Tuple[Dict[str, float], float]:
        """
        Calculates itemized costs and total budget for a candidate plan branch.
        """
        # 1. Transport = rate_per_person * num_people
        transport_cost = modal_data["transport"]["rate_per_person"] * goal.num_people

        # 2. Accommodation = fixed stay package
        accommodation_cost = modal_data["accommodation"]["total_cost"]

        # 3. Food = daily_rate_per_person * num_people * duration_days
        food_cost = modal_data["food"]["daily_rate_per_person"] * goal.num_people * goal.duration_days

        # 4. Sightseeing = package cost
        sightseeing_cost = modal_data["sightseeing"]["total_cost"]

        breakdown = {
            "transportation": transport_cost,
            "accommodation": accommodation_cost,
            "food": food_cost,
            "sightseeing": sightseeing_cost
        }
        total_cost = sum(breakdown.values())
        return breakdown, total_cost

    @classmethod
    def evaluate_candidate(
        cls,
        total_cost: float,
        budget_limit: float,
        experience_rating: float
    ) -> Tuple[bool, float, float, float, float]:
        """
        Evaluates candidate plan feasibility and computes multi-criteria scores:
        - Feasibility Score (100.0 if within budget, 0.0 if over budget)
        - Cost Efficiency Score (scaled by remaining budget buffer)
        - Experience Score (0-100 based on comfort and excursion depth)
        - Composite Weighted Score: (0.35 * Feas) + (0.35 * Exp) + (0.30 * Cost)
        """
        is_feasible = total_cost <= budget_limit

        if is_feasible:
            feasibility_score = 100.0
            remaining = budget_limit - total_cost
            # Cost efficiency: 50 base + up to 50 for savings headroom
            cost_score = round(50.0 + 50.0 * (remaining / budget_limit), 2)
        else:
            feasibility_score = 0.0
            cost_score = 0.0  # Disqualified due to budget breach

        experience_score = experience_rating

        # Composite multi-criteria calculation
        composite = (
            (0.35 * feasibility_score) +
            (0.35 * experience_score) +
            (0.30 * cost_score)
        )
        composite_score = round(composite, 2)

        return is_feasible, cost_score, feasibility_score, experience_score, composite_score

    @classmethod
    def explore_tree(cls, goal: TravelGoal) -> List[CandidatePlan]:
        """
        Generates and evaluates all candidate branches in the decision tree.
        """
        candidates: List[CandidatePlan] = []

        for plan_id, data in cls.TRAVEL_MODALITIES.items():
            breakdown, total_cost = cls.calculate_candidate_cost(data, goal)
            is_feasible, cost_score, feas_score, exp_score, comp_score = cls.evaluate_candidate(
                total_cost=total_cost,
                budget_limit=goal.budget_limit,
                experience_rating=data["experience_rating"]
            )

            candidate = CandidatePlan(
                plan_id=plan_id,
                name=data["name"],
                transport_choice=data["transport"]["name"],
                accommodation_choice=data["accommodation"]["name"],
                food_tier=data["food"]["tier"],
                sightseeing_tier=data["sightseeing"]["tier"],
                cost_breakdown=breakdown,
                total_cost=total_cost,
                is_feasible=is_feasible,
                cost_score=cost_score,
                feasibility_score=feas_score,
                experience_score=exp_score,
                composite_score=comp_score,
                description=data["description"],
                pros=data["pros"],
                cons=data["cons"]
            )
            candidates.append(candidate)

        return candidates

    @classmethod
    def select_best_candidate(cls, candidates: List[CandidatePlan]) -> CandidatePlan:
        """
        Selects the optimal candidate plan based on highest composite score among feasible plans.
        """
        feasible_candidates = [c for c in candidates if c.is_feasible]
        if not feasible_candidates:
            raise ValueError("Tree-of-Thought search failed: No candidate plan satisfies budget feasibility.")

        # Sort descending by composite score
        feasible_candidates.sort(key=lambda c: c.composite_score, reverse=True)
        return feasible_candidates[0]

    @classmethod
    def generate_comparison_table_text(cls, candidates: List[CandidatePlan]) -> str:
        """
        Generates a clean ASCII table comparing candidate plans for terminal and report logs.
        """
        header = (
            f"{'Plan ID':<8} | {'Strategy Name':<24} | {'Total Cost':<11} | "
            f"{'Feasible?':<10} | {'Cost Sc.':<8} | {'Exp. Sc.':<8} | {'Composite':<9}"
        )
        separator = "-" * len(header)
        rows = [header, separator]

        for c in candidates:
            feas_str = "YES" if c.is_feasible else "NO"
            row = (
                f"{c.plan_id:<8} | {c.name:<24} | ₹{c.total_cost:<10,.0f} | "
                f"{feas_str:<10} | {c.cost_score:<8.1f} | {c.experience_score:<8.1f} | {c.composite_score:<9.2f}"
            )
            rows.append(row)

        return "\n".join(rows)

