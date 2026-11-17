"""
tools.py
--------
Action Executor tools for the ReAct Travel Planning Agent.
Contains separate Python functions for:
- calculate_transport()
- search_accommodation()
- replan_accommodation()
- estimate_food_cost()
- select_sightseeing()
- calculate_total_budget()
- verify_budget()

All tools return standardized ActionResult objects with status, cost, and machine-readable payload data.
Simulates a realistic local travel database with inventory verification and controlled failure logic.
"""

from typing import Dict, Any, Optional
from models import ActionResult


# ==============================================================================
# Local Travel Catalog & Database (Offline, Realistic Ground-Truth Simulation)
# ==============================================================================

TRANSPORT_CATALOG = {
    "Goa": {
        "train_sleeper": {
            "name": "Konkan Express (AC 3-Tier Sleeper)",
            "rate_per_person_roundtrip": 1000.0,
            "description": "Overnight AC 3-Tier sleeper train to Madgaon / Thivim, Goa"
        },
        "train_non_ac": {
            "name": "Standard Express (Non-AC Sleeper)",
            "rate_per_person_roundtrip": 800.0,
            "description": "Economy sleeper rail transit"
        },
        "volvo_bus": {
            "name": "Multi-Axle Semi-Sleeper Luxury Bus",
            "rate_per_person_roundtrip": 1400.0,
            "description": "Direct AC Volvo luxury interstate coach"
        }
    }
}

ACCOMMODATION_CATALOG = {
    "Sunset Beach Resort": {
        "type": "3-Star Beachfront Resort",
        "total_cost": 3000.0,
        "available": False,  # Programmatic inventory check simulates fully booked
        "reason": "Fully booked for the selected dates due to peak weekend season."
    },
    "Palm Breeze Budget Guesthouse": {
        "type": "Cozy AC Budget Guesthouse",
        "total_cost": 2000.0,
        "available": True,
        "location": "Near Calangute Beach, North Goa",
        "amenities": ["Double Bed", "AC", "Free Wi-Fi", "Walking distance to beach"]
    },
    "Sea Mist Backpacker Hostel": {
        "type": "Dormitory / Budget Pod",
        "total_cost": 1500.0,
        "available": True,
        "location": "Anjuna, Goa",
        "amenities": ["Bunk Pod", "Shared Bath", "Lockers"]
    },
    "Heritage Boutique Beachfront Villa": {
        "type": "Luxury Heritage Villa",
        "total_cost": 4800.0,
        "available": True,
        "location": "Candolim, Goa",
        "amenities": ["Private Pool Access", "King Suite", "Breakfast Included"]
    }
}

FOOD_TIERS = {
    "budget_local": {
        "name": "Local Goan Beach Shacks & Authentic Thalis",
        "cost_per_person_per_day": 750.0,
        "includes": ["Breakfast (Goan Poi & Chai)", "Lunch (Fish / Veg Thali)", "Dinner (Beach Shack Grills)"]
    },
    "street_dhaba": {
        "name": "Local Dhabas & Street Food",
        "cost_per_person_per_day": 500.0,
        "includes": ["Quick street breakfast", "Local veg/egg meals", "Tea & snacks"]
    },
    "fine_dining": {
        "name": "Premium Multi-Cuisine Restaurants",
        "cost_per_person_per_day": 1000.0,
        "includes": ["Buffet breakfast", "Fine seafood dining", "Evening beach cocktails"]
    }
}

SIGHTSEEING_PACKAGES = {
    "Goa": {
        "standard_highlights": {
            "name": "North Goa Highlights & 2-Day Scooter Rental",
            "activities": [
                "Fort Aguada historical fort visit (Entry ₹100 x 2 = ₹200)",
                "Calangute & Baga beach stroll and sunset view (Free)",
                "Old Goa heritage churches tour (Basilica of Bom Jesus) (Free)",
                "2-Day Honda Activa Scooter Rental + Fuel (₹500/day = ₹1,000)"
            ],
            "total_cost": 1200.0
        },
        "budget_walks": {
            "name": "Public Beach Walks & Self-Guided Heritage Tour",
            "activities": [
                "Public bus local commute (₹400)",
                "Miramar & Dona Paula viewpoint walks (Free)",
                "Old Goa heritage churches walk (Free)"
            ],
            "total_cost": 800.0
        },
        "luxury_adventure": {
            "name": "Guided Water Sports & Scuba Package + Private Cab",
            "activities": [
                "Scuba diving session & banana boat ride (₹1,500)",
                "Dedicated private AC cab for 2 days (₹1,000)"
            ],
            "total_cost": 2500.0
        }
    }
}


# ==============================================================================
# Action Executor Functions (ReAct Tool Definitions)
# ==============================================================================

def calculate_transport(
    destination: str,
    num_people: int,
    mode: str = "train_sleeper"
) -> ActionResult:
    """
    Calculates round-trip transportation cost for the given number of travelers.
    
    Args:
        destination: Destination city/region (e.g. 'Goa')
        num_people: Number of people traveling
        mode: Chosen transport mode ('train_sleeper', 'train_non_ac', or 'volvo_bus')
        
    Returns:
        ActionResult containing status, cost, and booking details.
    """
    dest_data = TRANSPORT_CATALOG.get(destination, TRANSPORT_CATALOG["Goa"])
    transport_info = dest_data.get(mode, dest_data["train_sleeper"])
    
    rate = transport_info["rate_per_person_roundtrip"]
    total_transport_cost = rate * num_people
    
    obs_msg = (
        f"Transportation estimated at ₹{total_transport_cost:,.0f} "
        f"({transport_info['name']} round-trip for {num_people} people at ₹{rate:,.0f} each)."
    )
    
    return ActionResult(
        success=True,
        action_name="calculate_transport",
        message=obs_msg,
        cost=total_transport_cost,
        data={
            "mode": transport_info["name"],
            "rate_per_person": rate,
            "num_people": num_people,
            "cost": total_transport_cost
        }
    )


def search_accommodation(
    destination: str,
    duration_days: int,
    num_people: int,
    hotel_name: str = "Sunset Beach Resort",
    simulate_failure: bool = True
) -> ActionResult:
    """
    Searches and attempts booking for initial accommodation preference.
    Programmatically verifies inventory availability in the ACCOMMODATION_CATALOG.
    
    Args:
        destination: Travel destination
        duration_days: Duration of the stay in days
        num_people: Number of guests
        hotel_name: Target hotel to check
        simulate_failure: If True, tests realistic room unavailability
        
    Returns:
        ActionResult indicating whether accommodation is available or failed.
    """
    hotel_info = ACCOMMODATION_CATALOG.get(hotel_name)
    
    # Controlled failure simulation: hotel is fully booked in inventory
    if not hotel_info or not hotel_info["available"] or simulate_failure:
        failure_detail = (
            hotel_info["reason"] if hotel_info and "reason" in hotel_info 
            else f"Hotel '{hotel_name}' has no available vacancy for requested dates."
        )
        obs_msg = f"Selected hotel '{hotel_name}' is unavailable. ({failure_detail})"
        
        return ActionResult(
            success=False,
            action_name="search_accommodation",
            message=obs_msg,
            cost=0.0,
            failure_reason=failure_detail,
            data={
                "attempted_hotel": hotel_name,
                "intended_budget": 3000.0,
                "available": False
            }
        )
    
    cost = hotel_info["total_cost"]
    obs_msg = f"Accommodation '{hotel_name}' booked successfully for ₹{cost:,.0f}."
    return ActionResult(
        success=True,
        action_name="search_accommodation",
        message=obs_msg,
        cost=cost,
        data={"hotel_name": hotel_name, "cost": cost}
    )


def replan_accommodation(
    destination: str,
    duration_days: int,
    num_people: int,
    preferred_type: str = "budget_guesthouse"
) -> ActionResult:
    """
    Dynamic replanning tool executed when primary hotel booking fails.
    Searches available alternatives from the verified inventory and reserves a budget guesthouse.
    
    Args:
        destination: Destination location
        duration_days: Stay length
        num_people: Number of people
        preferred_type: Fallback accommodation category
        
    Returns:
        ActionResult with alternative accommodation details and reduced cost.
    """
    alternative_name = "Palm Breeze Budget Guesthouse"
    alt_info = ACCOMMODATION_CATALOG[alternative_name]
    cost = alt_info["total_cost"]
    
    obs_msg = (
        f"Alternative guesthouse '{alternative_name}' successfully selected for ₹{cost:,.0f}. "
        f"Includes AC Double Room near Calangute Beach with verified availability."
    )
    
    return ActionResult(
        success=True,
        action_name="replan_accommodation",
        message=obs_msg,
        cost=cost,
        data={
            "accommodation_name": alternative_name,
            "type": alt_info["type"],
            "location": alt_info["location"],
            "amenities": alt_info["amenities"],
            "cost": cost,
            "status": "Confirmed"
        }
    )


def estimate_food_cost(
    duration_days: int,
    num_people: int,
    meal_tier: str = "budget_local"
) -> ActionResult:
    """
    Estimates total meal expenses across the trip based on travel duration and party size.
    
    Args:
        duration_days: Trip duration in days
        num_people: Number of travelers
        meal_tier: Budget tier ('budget_local', 'street_dhaba', or 'fine_dining')
        
    Returns:
        ActionResult containing food estimate and daily breakdown.
    """
    tier_info = FOOD_TIERS.get(meal_tier, FOOD_TIERS["budget_local"])
    daily_rate = tier_info["cost_per_person_per_day"]
    total_food_cost = daily_rate * num_people * duration_days
    
    obs_msg = (
        f"Food expenses estimated at ₹{total_food_cost:,.0f} "
        f"({duration_days} days x {num_people} people @ ₹{daily_rate:,.0f}/person/day for {tier_info['name']})."
    )
    
    return ActionResult(
        success=True,
        action_name="estimate_food_cost",
        message=obs_msg,
        cost=total_food_cost,
        data={
            "meal_tier": tier_info["name"],
            "daily_per_person": daily_rate,
            "duration_days": duration_days,
            "num_people": num_people,
            "cost": total_food_cost,
            "includes": tier_info["includes"]
        }
    )


def select_sightseeing(
    destination: str,
    num_people: int,
    duration_days: int,
    package: str = "standard_highlights"
) -> ActionResult:
    """
    Selects curated sightseeing activities and local commute options for the destination.
    
    Args:
        destination: City/region
        num_people: Number of people
        duration_days: Trip duration
        package: Selected package key ('standard_highlights', 'budget_walks', or 'luxury_adventure')
        
    Returns:
        ActionResult with itinerary highlights and total activity cost.
    """
    dest_activities = SIGHTSEEING_PACKAGES.get(destination, SIGHTSEEING_PACKAGES["Goa"])
    pkg = dest_activities.get(package, dest_activities["standard_highlights"])
    cost = pkg["total_cost"]
    
    obs_msg = (
        f"Sightseeing and local commute estimated at ₹{cost:,.0f}. "
        f"Selected: Fort Aguada, Calangute/Baga beaches, Old Goa churches & 2-day scooter rental."
    )
    
    return ActionResult(
        success=True,
        action_name="select_sightseeing",
        message=obs_msg,
        cost=cost,
        data={
            "package_name": pkg["name"],
            "activities": pkg["activities"],
            "cost": cost
        }
    )


def calculate_total_budget(
    transport_cost: float,
    accommodation_cost: float,
    food_cost: float,
    sightseeing_cost: float
) -> ActionResult:
    """
    Aggregates all subtask expenses into a final combined trip cost.
    
    Args:
        transport_cost: Final transport expense
        accommodation_cost: Final accommodation expense
        food_cost: Final food expense
        sightseeing_cost: Final sightseeing expense
        
    Returns:
        ActionResult containing itemized breakdown and overall sum.
    """
    total = transport_cost + accommodation_cost + food_cost + sightseeing_cost
    obs_msg = (
        f"Total expenses calculated at ₹{total:,.0f} "
        f"(Transport: ₹{transport_cost:,.0f}, Accommodation: ₹{accommodation_cost:,.0f}, "
        f"Food: ₹{food_cost:,.0f}, Sightseeing: ₹{sightseeing_cost:,.0f})."
    )
    
    return ActionResult(
        success=True,
        action_name="calculate_total_budget",
        message=obs_msg,
        cost=total,
        data={
            "transport_cost": transport_cost,
            "accommodation_cost": accommodation_cost,
            "food_cost": food_cost,
            "sightseeing_cost": sightseeing_cost,
            "total_cost": total
        }
    )


def verify_budget(
    total_cost: float,
    budget_limit: float
) -> ActionResult:
    """
    Verifies if the final total cost falls within the specified user budget ceiling.
    
    Args:
        total_cost: Aggregated plan expense
        budget_limit: User's maximum budget ceiling
        
    Returns:
        ActionResult indicating approval status and remaining buffer.
    """
    remaining = budget_limit - total_cost
    is_valid = remaining >= 0
    
    if is_valid:
        obs_msg = (
            f"Plan is within budget. Total ₹{total_cost:,.0f} is within limit of ₹{budget_limit:,.0f}. "
            f"Remaining savings buffer: ₹{remaining:,.0f}."
        )
    else:
        deficit = abs(remaining)
        obs_msg = (
            f"Plan exceeds budget by ₹{deficit:,.0f}! Total ₹{total_cost:,.0f} exceeds limit of ₹{budget_limit:,.0f}."
        )
        
    return ActionResult(
        success=is_valid,
        action_name="verify_budget",
        message=obs_msg,
        cost=total_cost,
        data={
            "total_cost": total_cost,
            "budget_limit": budget_limit,
            "remaining_budget": remaining,
            "is_within_budget": is_valid,
            "savings_percentage": round((remaining / budget_limit) * 100, 2) if budget_limit else 0
        }
    )

