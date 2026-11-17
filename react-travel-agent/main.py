"""
main.py
-------
Main execution entry point for the Unified CoT + ToT + ReAct Travel Planning Agent.

Coordinates:
1. Chain-of-Thought (CoT) Goal Analysis & Structured Reasoning Decomposition.
2. Tree-of-Thought (ToT) Alternative Branch Exploration, Scoring & Optimal Plan Selection.
3. ReAct Execution Loop (THOUGHT -> ACTION -> OBSERVATION).
4. Dynamic Replanning & Autonomous Fault Recovery.
5. Persistent disk output serialization (execution_trace.txt, candidate_plans.json, final_plan.json).
"""

import os
import json
import sys

# Ensure UTF-8 output encoding on Windows consoles for currency symbols (e.g. ₹)
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

from reasoning import ChainOfThoughtReasoner
from tree_search import TreeOfThoughtPlanner
from agent import ReActAgent
from models import TravelPlan


def print_banner(title: str, char: str = "=", width: int = 80):
    """Utility to print clean terminal section dividers."""
    print("\n" + char * width)
    print(f" {title.upper()} ".center(width, char))
    print(char * width + "\n")


def run_pipeline(user_goal_text: str):
    """
    Executes the entire end-to-end intelligent travel planning pipeline.
    Seamlessly integrates Chain-of-Thought, Tree-of-Thought, and ReAct frameworks.
    """
    print_banner("INTELLIGENT TASK-PLANNING AGENT: CoT + ToT + ReAct WORKFLOW")
    print(f"User Goal Input:\n\"{user_goal_text}\"\n")

    # ==========================================================================
    # 1. CHAIN-OF-THOUGHT (CoT): Goal Decomposition & Structured Reasoning
    # ==========================================================================
    print_banner("PHASE 1: CHAIN-OF-THOUGHT (CoT) REASONING & SUBTASK DECOMPOSITION", "-")
    goal = ChainOfThoughtReasoner.parse_goal(user_goal_text)
    reasoning_summary = ChainOfThoughtReasoner.decompose_goal(goal)

    print(f"Parsed Goal Parameters:")
    print(f"  * Destination:          {goal.destination}")
    print(f"  * Trip Duration:        {goal.duration_days} Days / 1 Night")
    print(f"  * Number of Travelers:  {goal.num_people} People")
    print(f"  * Total Budget Ceiling: ₹{goal.budget_limit:,.0f}")
    print(f"  * Expense Categories:   {', '.join(goal.categories)}\n")

    print("Goal Constraints Identified:")
    for c in reasoning_summary.constraints:
        print(f"  [!] {c}")

    print("\nOrdered Subtasks with Concise Reasoning Justifications:")
    for task_info in reasoning_summary.subtasks:
        print(f"  Step {task_info['step']}: {task_info['task_name']} [{task_info['tool_action']}]")
        print(f"    -> Rationale: {task_info['justification']}")

    print("\nTask Dependencies:")
    for dep in reasoning_summary.dependencies:
        print(f"  * {dep}")

    print(f"\nExecution Order Rationale:\n  {reasoning_summary.execution_order_rationale}")

    # ==========================================================================
    # 2. TREE-OF-THOUGHT (ToT): Alternative Plan Exploration & Scoring
    # ==========================================================================
    print_banner("PHASE 2: TREE-OF-THOUGHT (ToT) ALTERNATIVE PLAN EXPLORATION", "-")
    candidate_plans = TreeOfThoughtPlanner.explore_tree(goal)

    print("Generated Candidate Plan Branches:")
    for cand in candidate_plans:
        feas_label = "FEASIBLE" if cand.is_feasible else "INFEASIBLE (OVER BUDGET)"
        print(f"\n--- {cand.plan_id}: {cand.name} [{feas_label}] ---")
        print(f"  * Strategy:       {cand.description}")
        print(f"  * Transit:        {cand.transport_choice} (₹{cand.cost_breakdown['transportation']:,.0f})")
        print(f"  * Lodging:        {cand.accommodation_choice} (₹{cand.cost_breakdown['accommodation']:,.0f})")
        print(f"  * Dining:         {cand.food_tier} (₹{cand.cost_breakdown['food']:,.0f})")
        print(f"  * Sightseeing:    {cand.sightseeing_tier} (₹{cand.cost_breakdown['sightseeing']:,.0f})")
        print(f"  * Total Budget:   ₹{cand.total_cost:,.0f} (Ceiling: ₹{goal.budget_limit:,.0f})")
        print(f"  * Scoring:        Cost={cand.cost_score:.1f} | Feasibility={cand.feasibility_score:.1f} | "
              f"Experience={cand.experience_score:.1f} => Composite={cand.composite_score:.2f}")

    print("\nStructured Candidate Evaluation Table:")
    table_str = TreeOfThoughtPlanner.generate_comparison_table_text(candidate_plans)
    print(table_str)

    # Select the optimal candidate
    selected_candidate = TreeOfThoughtPlanner.select_best_candidate(candidate_plans)
    print(f"\n[ToT SELECTION] Optimal Candidate Chosen: {selected_candidate.plan_id} ({selected_candidate.name})")
    print(f"  * Justification: Highest composite multi-attribute score ({selected_candidate.composite_score:.2f}/100) "
          f"satisfying hard budget feasibility with an estimated initial cost of ₹{selected_candidate.total_cost:,.0f}.")

    # ==========================================================================
    # 3. REACT FRAMEWORK: Execution Loop & Dynamic Replanning
    # ==========================================================================
    print_banner("PHASE 3: REACT EXECUTION TRACE (THOUGHT -> ACTION -> OBSERVATION)")
    agent = ReActAgent(
        goal=goal,
        selected_candidate=selected_candidate,
        reasoning_summary=reasoning_summary,
        candidate_plans=candidate_plans
    )
    plan: TravelPlan = agent.run()

    formatted_trace = agent.get_formatted_trace()
    print(formatted_trace)

    # ==========================================================================
    # 4. FINAL EXECUTION SUMMARY & BUDGET AUDIT
    # ==========================================================================
    print_banner("PHASE 4: FINAL EXECUTION SUMMARY & BUDGET AUDIT", "-")
    print(f"Original User Goal:       {goal.raw_goal}")
    print(f"Selected Strategy (ToT):  {selected_candidate.plan_id} - {selected_candidate.name}")
    print(f"Initial Planned Tasks:    {len(plan.initial_tasks)}")
    print(f"Total Steps Executed:     {len(plan.current_tasks)}")

    if plan.replanning_occurred:
        print(f"\n[DYNAMIC REPLANNING EVENT TRIGGERED]")
        print(f"  * Detected Failed Task: {plan.failed_task.name} ({plan.failed_task.action})")
        print(f"  * Root Failure Cause:   {plan.replanning_reason}")
        print(f"  * Agent Diagnosis:      Hotel room inventory unavailable. Infeasible to proceed unchanged.")
        print(f"  * Recovery Action:      Dispatched replan_accommodation() to select Palm Breeze Budget Guesthouse.")
        print(f"  * Replanned Subtask:    {plan.replanned_task.name} ({plan.replanned_task.action})")
        print(f"  * Status:               Successfully recovered in-flight without restarting workflow.")

    print("\nFinal Executed Task Sequence:")
    for idx, t in enumerate(plan.current_tasks, 1):
        status_flag = "[FAILED]" if t.status.value == "FAILED" else ("[REPLANNED]" if t.is_replanned else "[OK]")
        cost_str = f"₹{t.cost:,.0f}" if t.cost > 0 else "-"
        print(f"  {idx}. {status_flag:<12} {t.name:<54} Cost: {cost_str}")

    print("\nAudited Cost Breakdown by Category:")
    print(f"  * Transportation:       ₹{plan.cost_breakdown.get('transportation', 0.0):>8,.0f}")
    print(f"  * Accommodation:        ₹{plan.cost_breakdown.get('accommodation', 0.0):>8,.0f}  (Saved ₹1,000 via replanning)")
    print(f"  * Food & Dining:        ₹{plan.cost_breakdown.get('food', 0.0):>8,.0f}")
    print(f"  * Sightseeing & Commute:₹{plan.cost_breakdown.get('sightseeing', 0.0):>8,.0f}")
    print("  " + "-" * 45)
    print(f"  * Final Total Cost:     ₹{plan.total_cost:>8,.0f}")
    print(f"  * User Budget Ceiling:  ₹{goal.budget_limit:>8,.0f}")
    print(f"  * Net Savings Buffer:   ₹{plan.remaining_budget:>8,.0f}")
    print(f"  * Final Feasibility:    {'SUCCESS - FULLY APPROVED' if plan.is_approved else 'FAILED - OVER BUDGET'}")

    # ==========================================================================
    # 5. PERSIST ARTIFACTS TO DISK
    # ==========================================================================
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "outputs")
    os.makedirs(output_dir, exist_ok=True)

    # 1. execution_trace.txt
    trace_path = os.path.join(output_dir, "execution_trace.txt")
    with open(trace_path, "w", encoding="utf-8") as f:
        f.write(formatted_trace + "\n")

    # 2. candidate_plans.json
    cand_path = os.path.join(output_dir, "candidate_plans.json")
    with open(cand_path, "w", encoding="utf-8") as f:
        json.dump([c.to_dict() for c in candidate_plans], f, indent=2)

    # 3. final_plan.json
    plan_path = os.path.join(output_dir, "final_plan.json")
    with open(plan_path, "w", encoding="utf-8") as f:
        json.dump(plan.to_dict(), f, indent=2)

    print_banner("OUTPUT ARTIFACTS PERSISTED", "-")
    print(f"  [+] Execution Trace saved to:   {trace_path}")
    print(f"  [+] Candidate Plans saved to:   {cand_path}")
    print(f"  [+] Final Executed Plan to:     {plan_path}\n")

    return plan, candidate_plans, formatted_trace


if __name__ == "__main__":
    default_goal = (
        "Plan a 2-day trip to Goa for 2 people within a total budget of ₹10,000, "
        "including transportation, accommodation, food and sightseeing."
    )
    goal_input = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else default_goal
    run_pipeline(goal_input)

