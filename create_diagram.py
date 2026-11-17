"""
create_diagram.py
-----------------
Generates a publication-quality architecture diagram illustrating the unified
Chain-of-Thought (CoT), Tree-of-Thought (ToT), and ReAct travel planning agent.
Saves as a high-resolution PNG (300 DPI) for inclusion in the academic submission report.
"""

import os
import tempfile
os.environ["MPLCONFIGDIR"] = os.path.join(tempfile.gettempdir(), ".mplcache")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches


def generate_architecture_diagram(output_path: str):
    fig, ax = plt.subplots(figsize=(12, 10), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    # Professional Academic Color Palette (Navy, Slate, Amber, Green, Crimson)
    c_navy_dark = "#1B365D"     # Deep Navy
    c_blue_primary = "#0969DA"  # Technical Accent Blue
    c_blue_light = "#EBF3FA"    # Light Ice Blue
    c_slate_bg = "#F4F6F9"      # Light Neutral Slate
    c_amber_bg = "#FFF8E7"      # Alert / Replanning Amber Light
    c_amber_border = "#BF8700"  # Amber Border
    c_green_acc = "#1A7F37"     # Success Green
    c_red_acc = "#CF222E"       # Failure Crimson
    c_text_dark = "#24292E"     # Charcoal Black

    # =========================================================================
    # 1. USER GOAL BOX (TOP)
    # =========================================================================
    goal_box = patches.FancyBboxPatch((10, 89), 80, 8.5, boxstyle="round,pad=1.2",
                                      facecolor=c_blue_light, edgecolor=c_navy_dark, linewidth=2.2)
    ax.add_patch(goal_box)
    ax.text(50, 94.5, "USER MISSION OBJECTIVE & CONSTRAINTS", fontsize=11, fontweight="bold",
            ha="center", va="center", color=c_navy_dark)
    ax.text(50, 91.2, '"Plan a 2-day trip to Goa for 2 people within a total budget of ₹10,000, including transportation, accommodation, food and sightseeing."',
            fontsize=8.5, fontstyle="italic", ha="center", va="center", color=c_text_dark)

    # Arrow: User Goal -> Phase 1
    ax.annotate("", xy=(50, 84), xytext=(50, 89),
                arrowprops=dict(arrowstyle="->", lw=2, color=c_navy_dark))

    # =========================================================================
    # 2. PHASE 1: CHAIN-OF-THOUGHT (CoT) REASONING & DECOMPOSITION
    # =========================================================================
    cot_box = patches.FancyBboxPatch((8, 70), 84, 14, boxstyle="round,pad=1.2",
                                     facecolor="#F0F4F8", edgecolor=c_blue_primary, linewidth=2)
    ax.add_patch(cot_box)
    ax.text(50, 81.5, "PHASE 1: CHAIN-OF-THOUGHT (CoT) GOAL DECOMPOSITION & REASONING",
            fontsize=10.5, fontweight="bold", ha="center", va="center", color=c_navy_dark)
    ax.text(50, 77.8, "• Goal & Entity Analysis: Destination (Goa), Duration (2 Days), Party (2 People), Budget Ceiling (₹10,000)\n"
                      "• Causal Subtask Decomposition: 1. Transport -> 2. Accommodation -> 3. Food -> 4. Sightseeing -> 5. Aggregate -> 6. Audit\n"
                      "• Structured Reasoning Summaries: Explains WHY each task is needed without exposing raw private prompts\n"
                      "• Strict Dependency Graph: Preconditions enforced before execution order is frozen",
            fontsize=7.8, ha="center", va="center", color=c_text_dark, linespacing=1.3)

    # Arrow: CoT -> ToT
    ax.annotate("", xy=(50, 65), xytext=(50, 70),
                arrowprops=dict(arrowstyle="->", lw=2, color=c_navy_dark))

    # =========================================================================
    # 3. PHASE 2: TREE-OF-THOUGHT (ToT) ALTERNATIVE PLAN EXPLORATION
    # =========================================================================
    tot_outer_box = patches.FancyBboxPatch((4, 45), 92, 20, boxstyle="round,pad=1.2",
                                           facecolor="#FAFBFC", edgecolor="#D0D7DE", linewidth=1.8)
    ax.add_patch(tot_outer_box)
    ax.text(50, 63, "PHASE 2: TREE-OF-THOUGHT (ToT) MULTI-BRANCH PLAN EXPLORATION & SCORING",
            fontsize=10.5, fontweight="bold", ha="center", va="center", color=c_navy_dark)

    # Branch A: Budget
    b1_box = patches.FancyBboxPatch((6, 47), 27, 13.5, boxstyle="round,pad=1.0",
                                    facecolor="#FFFFFF", edgecolor="#6E7781", linewidth=1.5)
    ax.add_patch(b1_box)
    ax.text(19.5, 58.5, "BRANCH A: BUDGET-FOCUSED", fontsize=8.5, fontweight="bold", ha="center", color=c_navy_dark)
    ax.text(19.5, 53.0, "• Non-AC Train (₹1,600)\n• Hostel Dorm Pod (₹1,500)\n• Dhabas / Street (₹2,000)\n• Public Walks (₹800)\n• Total: ₹5,900 [FEASIBLE]\n• Score: 75.40 (Low Luxury)",
            fontsize=7.2, ha="center", va="center", color=c_text_dark, linespacing=1.2)

    # Branch B: Balanced (Winner)
    b2_box = patches.FancyBboxPatch((36.5, 47), 27, 13.5, boxstyle="round,pad=1.0",
                                    facecolor="#EBF5FF", edgecolor=c_green_acc, linewidth=2.2)
    ax.add_patch(b2_box)
    ax.text(50, 58.8, "BRANCH B: BALANCED [SELECTED]", fontsize=8.5, fontweight="bold", ha="center", color=c_green_acc)
    ax.text(50, 53.0, "• AC 3-Tier Train (₹2,000)\n• Sunset Beach Resort (₹3,000)\n• Beach Shacks/Thalis (₹3,000)\n• Forts + Scooter (₹1,200)\n• Total: ₹9,200 [FEASIBLE]\n• Score: 82.00 (TOP RANKED)",
            fontsize=7.2, ha="center", va="center", color=c_text_dark, linespacing=1.2)

    # Branch C: Experience (Pruned)
    b3_box = patches.FancyBboxPatch((67, 47), 27, 13.5, boxstyle="round,pad=1.0",
                                    facecolor="#FFF0F0", edgecolor=c_red_acc, linewidth=1.5)
    ax.add_patch(b3_box)
    ax.text(80.5, 58.5, "BRANCH C: EXPERIENCE [REJECTED]", fontsize=8.5, fontweight="bold", ha="center", color=c_red_acc)
    ax.text(80.5, 53.0, "• AC Volvo Bus (₹2,800)\n• Boutique Villa (₹4,800)\n• Fine Dining (₹4,000)\n• Scuba + Cab (₹2,500)\n• Total: ₹14,100 [INFEASIBLE]\n• Over budget by ₹4,100",
            fontsize=7.2, ha="center", va="center", color=c_text_dark, linespacing=1.2)

    # Arrow: Selected Branch B -> ReAct
    ax.annotate("", xy=(50, 40), xytext=(50, 45),
                arrowprops=dict(arrowstyle="->", lw=2.2, color=c_green_acc))

    # =========================================================================
    # 4. PHASE 3: REACT EXECUTION CYCLE & DYNAMIC REPLANNING
    # =========================================================================
    react_box = patches.FancyBboxPatch((6, 17), 54, 23, boxstyle="round,pad=1.2",
                                       facecolor="#F4F6F9", edgecolor=c_blue_primary, linewidth=2)
    ax.add_patch(react_box)
    ax.text(33, 37.5, "PHASE 3: ReAct EXECUTION CYCLE", fontsize=10.5, fontweight="bold",
            ha="center", va="center", color=c_navy_dark)

    # Step mini-boxes inside ReAct
    ax.text(33, 33.5, "THOUGHT: Contextual reasoning explaining upcoming action rationale",
            fontsize=7.5, fontweight="bold", ha="center", color=c_blue_primary)
    ax.text(33, 30.5, "ACTION: Dispatch concrete Python tool function with validated inputs",
            fontsize=7.5, fontweight="bold", ha="center", color="#9A6700")
    ax.text(33, 27.5, "OBSERVATION: Inspect ground-truth result returned by tool execution",
            fontsize=7.5, fontweight="bold", ha="center", color=c_green_acc)

    ax.text(33, 22.0, "Concrete Python Tools Executed:\n"
                      "calculate_transport() -> search_accommodation() [FAILED]\n"
                      "-> replan_accommodation() [OK] -> estimate_food_cost()\n"
                      "-> select_sightseeing() -> calculate_total_budget() -> verify_budget()",
            fontsize=7.2, ha="center", va="center", color=c_text_dark, linespacing=1.2)

    # =========================================================================
    # 5. DYNAMIC REPLANNING & FAULT RECOVERY LAYER (RIGHT SIDE)
    # =========================================================================
    replan_box = patches.FancyBboxPatch((64, 17), 32, 23, boxstyle="round,pad=1.2",
                                        facecolor=c_amber_bg, edgecolor=c_amber_border, linewidth=2)
    ax.add_patch(replan_box)
    ax.text(80, 37.5, "DYNAMIC REPLANNING", fontsize=10.5, fontweight="bold",
            ha="center", va="center", color="#9A6700")
    ax.text(80, 34.0, "[Assumption Failure Detected]", fontsize=8.0, fontweight="bold", ha="center", color=c_red_acc)
    ax.text(80, 29.5, "• Sunset Beach Resort = 404 / Booked\n"
                      "• Violated Precondition: Hotel unavailable\n"
                      "• Autonomous Diagnostic Reasoning:\n"
                      "  Plan cannot proceed unchanged\n"
                      "• Fallback: Palm Breeze Guesthouse\n"
                      "• Verified Available: ₹2,000 (Saved ₹1,000)\n"
                      "• In-Flight Mutation: No restart needed",
            fontsize=7.2, ha="center", va="center", color=c_text_dark, linespacing=1.25)

    # Bidirectional communication arrow between ReAct and Dynamic Replanning
    ax.annotate("", xy=(64, 28), xytext=(60, 28),
                arrowprops=dict(arrowstyle="<->", lw=2, color=c_amber_border))

    # Arrow: ReAct & Dynamic Replanning down to Final State
    ax.annotate("", xy=(50, 11), xytext=(50, 17),
                arrowprops=dict(arrowstyle="->", lw=2.2, color=c_navy_dark))

    # =========================================================================
    # 6. PHASE 4: VERIFIED AUDITED PLAN STATE (BOTTOM)
    # =========================================================================
    final_box = patches.FancyBboxPatch((12, 1.5), 76, 9.5, boxstyle="round,pad=1.2",
                                       facecolor="#EBF5FF", edgecolor=c_navy_dark, linewidth=2.2)
    ax.add_patch(final_box)
    ax.text(50, 8.5, "FINAL AUDITED PLAN & VERIFIED STATE (APPROVED)",
            fontsize=10.5, fontweight="bold", ha="center", va="center", color=c_navy_dark)
    ax.text(50, 4.5, "• Transport: ₹2,000  |  • Lodging: ₹2,000 (Guesthouse)  |  • Food: ₹3,000  |  • Sightseeing: ₹1,200\n"
                      "• Final Total Cost: ₹8,200  |  • Budget Ceiling: ₹10,000  |  • Net Safety Margin: ₹1,800 Surplus\n"
                      "• Deliverables: execution_trace.txt, candidate_plans.json, final_plan.json",
            fontsize=7.8, ha="center", va="center", color=c_text_dark, linespacing=1.2)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[+] Architecture diagram generated: {output_path}")


if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    out_img = os.path.join(current_dir, "architecture_diagram.png")
    generate_architecture_diagram(out_img)

